import io
import os
from functools import wraps
from typing import Any

import fitz
import jwt
import pytesseract
from flask import jsonify, request
from PIL import Image
from werkzeug.utils import secure_filename

from Modelo.pdf_modelo import ResultadoPDF


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "utils_remington")
JWT_ALGORITHM = "HS256"
ALLOWED_EXTENSIONS = {"pdf"}


# Construye la respuesta JSON y los encabezados cuando la autenticación falla.
def obtener_respuesta_no_autorizado() -> tuple[dict[str, str], int, dict[str, str]]:
    return (
        {"error": "No autorizado. Token JWT invalido o ausente."},
        401,
        {"WWW-Authenticate": 'Bearer realm="Microservicio PDF"'}
    )


# Verifica que el token JWT enviado en el header Authorization sea válido.
def autenticacion_jwt_valida(authorization_header: Any) -> bool:
    if not authorization_header:
        return False

    if not isinstance(authorization_header, str):
        return False

    if not authorization_header.startswith("Bearer "):
        return False

    token = authorization_header.split(" ", 1)[1].strip()
    if not token:
        return False

    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def token_requerido(funcion: Any) -> Any:
    @wraps(funcion)
    def decorador(*args: Any, **kwargs: Any) -> Any:
        if not autenticacion_jwt_valida(request.headers.get("Authorization")):
            payload, status_code, headers = obtener_respuesta_no_autorizado()
            respuesta = jsonify(payload)
            respuesta.status_code = status_code
            for llave, valor in headers.items():
                respuesta.headers[llave] = valor
            return respuesta

        return funcion(*args, **kwargs)

    return decorador


# Valida que el archivo recibido exista, tenga nombre, extensión PDF y MIME type correcto.
def validar_archivo_pdf(archivo: Any) -> tuple[str | None, str | None, int | None]:
    if archivo is None:
        return None, "Debes enviar un archivo PDF en el campo 'archivo'.", 400

    if archivo.filename == "":
        return None, "El archivo no tiene nombre.", 400

    nombre_archivo = secure_filename(archivo.filename)
    if not _archivo_permitido(nombre_archivo):
        return None, "Solo se permiten archivos con extension .pdf", 400

    if archivo.mimetype and archivo.mimetype != "application/pdf":
        return None, "El contenido enviado no corresponde a un PDF.", 400

    return nombre_archivo, None, None


# Comprueba si el nombre del archivo termina en una extensión permitida.
def _archivo_permitido(nombre_archivo: str) -> bool:
    if "." not in nombre_archivo:
        return False
    extension = nombre_archivo.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


# Configura la ruta de tesseract.exe mediante variable de entorno.
# Ejemplo en Windows:
# setx TESSERACT_CMD "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if not TESSERACT_CMD:
    ruta_default_windows = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(ruta_default_windows):
        TESSERACT_CMD = ruta_default_windows

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# Abre el PDF, extrae texto directo y aplica OCR cuando el contenido viene como imagen.
def extraer_texto_pdf(ruta_pdf: str) -> ResultadoPDF:

    documento = fitz.open(ruta_pdf)

    texto = ""
    imagenes_procesadas = 0

    for numero_pagina, pagina in enumerate(documento, start=1):
        texto_pagina = pagina.get_text().strip()
        if texto_pagina:
            texto += texto_pagina + "\n"

        texto_ocr_pagina = ""
        imagenes_detectadas_pagina = 0

        # OCR de imágenes incrustadas en la página.
        for imagen in pagina.get_images(full=True):
            imagenes_detectadas_pagina += 1
            xref = imagen[0]

            try:
                imagen_extraida = documento.extract_image(xref)
                contenido = imagen_extraida["image"]
                imagen_pil = Image.open(io.BytesIO(contenido))

                texto_ocr = pytesseract.image_to_string(imagen_pil, lang="spa+eng")
                if texto_ocr.strip():
                    texto_ocr_pagina += f"\n[OCR pagina {numero_pagina}]\n{texto_ocr}\n"

                imagenes_procesadas += 1
            except Exception:
                continue

        # Fallback para PDFs escaneados: OCR de la página completa.
        if not texto_pagina and not texto_ocr_pagina:
            try:
                matriz = fitz.Matrix(2, 2)
                pix = pagina.get_pixmap(matrix=matriz)
                imagen_pagina = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                texto_ocr_fallback = pytesseract.image_to_string(imagen_pagina, lang="spa+eng")
                if texto_ocr_fallback.strip():
                    texto_ocr_pagina += f"\n[OCR pagina completa {numero_pagina}]\n{texto_ocr_fallback}\n"

                if imagenes_detectadas_pagina == 0:
                    imagenes_procesadas += 1
            except Exception:
                pass

        texto += texto_ocr_pagina

    paginas = len(documento)
    documento.close()

    return ResultadoPDF(
        texto=texto,
        paginas=paginas,
        imagenes_procesadas=imagenes_procesadas
    )

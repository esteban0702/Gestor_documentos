import os

from flask import Blueprint, jsonify, request

from Controlador.pdf_controlador import autenticacion_basica_valida, extraer_texto_pdf, obtener_respuesta_no_autorizado, validar_archivo_pdf

# Define el blueprint que expone las rutas del microservicio.
pdf_bp = Blueprint("pdf", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Devuelve un mensaje simple para confirmar que el microservicio está activo.
@pdf_bp.route("/")
def inicio():
    return jsonify({"mensaje": "Microservicio de extracción de texto de PDF"})


# Recibe el PDF, valida acceso y archivo, y retorna el texto extraído con sus metadatos.
@pdf_bp.route("/api/utils", methods=["POST"])
def leer_pdf():
    if not autenticacion_basica_valida(request.authorization):
        payload, status_code, headers = obtener_respuesta_no_autorizado()
        respuesta = jsonify(payload)
        respuesta.status_code = status_code
        for llave, valor in headers.items():
            respuesta.headers[llave] = valor
        return respuesta

    archivo = request.files.get("archivo")
    nombre_archivo, mensaje_error, status_code = validar_archivo_pdf(archivo)
    if mensaje_error:
        return jsonify({"error": mensaje_error}), status_code

    ruta = os.path.join(UPLOAD_FOLDER, nombre_archivo)
    archivo.save(ruta)

    resultado = extraer_texto_pdf(ruta)

    return jsonify({
        "archivo": nombre_archivo,
        "paginas": resultado.paginas,
        "imagenes_procesadas": resultado.imagenes_procesadas,
        "texto": resultado.texto
    })

import os

from flask import Blueprint, jsonify, request

from Controlador.pdf_controlador import extraer_texto_pdf, token_requerido, validar_archivo_pdf

# Define el blueprint que expone las rutas del microservicio.
pdf_bp = Blueprint("pdf", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Devuelve un mensaje simple para confirmar que el microservicio esta activo.
@pdf_bp.route("/")
def inicio():
    return jsonify({"mensaje": "Microservicio de extraccion de texto de PDF"})


# Recibe el PDF, valida acceso y archivo, y retorna el texto extraido con sus metadatos.
@pdf_bp.route("/api/utils", methods=["POST"])
@token_requerido
def leer_pdf():
    
    """
    Procesa un PDF y extrae texto nativo y OCR.
    ---
    tags:
      - Utils
    consumes:
      - multipart/form-data
    produces:
      - application/json
    security:
      - BearerAuth: []
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: JWT en formato Bearer <token>
      - name: archivo
        in: formData
        type: file
        required: true
        description: Archivo PDF a procesar
    responses:
      200:
        description: Procesamiento exitoso
        schema:
          type: object
          properties:
            archivo:
              type: string
              example: mi_documento.pdf
            paginas:
              type: integer
              example: 3
            imagenes_procesadas:
              type: integer
              example: 2
            texto:
              type: string
              example: Texto extraido del PDF y OCR...
      400:
        description: Archivo faltante o invalido
        schema:
          type: object
          properties:
            error:
              type: string
      401:
        description: Token JWT ausente, invalido o expirado
        schema:
          type: object
          properties:
            error:
              type: string
    """

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
        "texto": resultado.texto,
    })

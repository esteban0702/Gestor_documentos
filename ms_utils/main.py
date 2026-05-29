import sys

sys.dont_write_bytecode = True

from flask import Flask
from flasgger import Swagger

from Vista.pdf_vista import pdf_bp

# Crea la aplicación Flask principal del microservicio.
app = Flask(__name__)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "ms_utils API",
        "description": "Microservicio para extracción de texto de PDF con OCR",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT en formato: Bearer <token>"
        }
    }
}

Swagger(app, template=swagger_template)

# Registra las rutas expuestas por la capa de vista.
app.register_blueprint(pdf_bp)

if __name__ == "__main__":
    app.run(debug=True)

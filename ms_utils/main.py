import sys

sys.dont_write_bytecode = True

from flask import Flask

from Vista.pdf_vista import pdf_bp

# Crea la aplicación Flask principal del microservicio.
app = Flask(__name__)

# Registra las rutas expuestas por la capa de vista.
app.register_blueprint(pdf_bp)

if __name__ == "__main__":
    app.run(debug=True)

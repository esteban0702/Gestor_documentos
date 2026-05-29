from dataclasses import dataclass


# Representa el resultado estructurado de la extracción de texto del PDF.
@dataclass
class ResultadoPDF:
    texto: str
    paginas: int
    imagenes_procesadas: int

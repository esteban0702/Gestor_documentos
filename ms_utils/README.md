# ms_utils

Microservicio en Flask para utilidades de procesamiento de PDF e imágenes.

## Arquitectura y flujo de ms_utils

Este microservicio sigue una estructura MVC simple para mantener separadas las responsabilidades:

- Modelo: estructura de datos de salida.
- Vista: rutas HTTP, request y response.
- Controlador: validaciones, autenticación y lógica de extracción OCR/PDF.

### Estructura principal

- main.py: crea la app Flask y registra el blueprint.
- Vista/pdf_vista.py: define rutas como / y /api/utils.
- Controlador/pdf_controlador.py: autentica, valida y procesa PDFs.
- Modelo/pdf_modelo.py: dataclass con el resultado.

### Flujo de procesamiento

1. El cliente envía POST a /api/utils con multipart/form-data y campo archivo.
2. Se valida autenticación mediante JWT en el header Authorization: Bearer <token>.
3. Se valida que el archivo sea PDF válido.
4. El archivo se guarda en uploads/.
5. Se extrae texto:
	- Texto nativo del PDF (si existe).
	- OCR en imágenes incrustadas.
	- Fallback: OCR de página completa para PDFs escaneados.
6. Se responde con JSON: archivo, paginas, imagenes_procesadas, texto.


### Respuesta exitosa (ejemplo)

```json
{
	"archivo": "mi_documento.pdf",
	"paginas": 3,
	"imagenes_procesadas": 2,
	"texto": "Texto extraido del PDF y OCR..."
}
```

### Respuestas de error comunes

- 401: No autorizado (token JWT ausente, inválido o expirado).
- 400: archivo faltante, sin nombre o no PDF válido.

## Requisitos

- Python 3.10+ instalado
- pip disponible

## 1. Crear entorno virtual

Desde la raíz del proyecto, ejecuta:

```powershell
python -m venv env
```

Esto crea la carpeta env con un entorno virtual aislado para el proyecto.

## 2. Activar entorno virtual

### En PowerShell

```powershell
env\Scripts\Activate.ps1
```

Si PowerShell bloquea scripts, habilita ejecución para el usuario actual:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### En CMD

```cmd
env\Scripts\activate.bat
```

## 3. Instalar dependencias

Con el entorno virtual activo:

```powershell
pip install -r requirements.txt
```

## 4. Levantar el servicio en un puerto específico

Comando general:

```powershell
python -m flask --app main run --host 127.0.0.1 --port 5000
```

Ejemplo en otro puerto (8000):

```powershell
python -m flask --app main run --host 127.0.0.1 --port 8000
```

## 5. Verificar que el servicio está corriendo

Abre en el navegador:

- http://127.0.0.1:5000
- o el puerto que hayas configurado

## 5.1 Documentación Swagger

Con el servicio levantado, abre:

- http://127.0.0.1:5000/apidocs

En Swagger UI puedes probar el endpoint /api/utils enviando:

- Header Authorization con formato: Bearer <token>
- Form-data con el campo archivo (PDF)

## 6. Desactivar entorno virtual

Cuando termines:

```powershell
deactivate
```

## Nota

Si no activas el entorno virtual, python puede usar el Python global y fallar con errores como No module named flask.

## Estado del proyecto

Resumen de funcionalidades y componentes implementados.

| Área | Detalle | Estado |
| --- | --- | --- |
| OCR | Extraer texto en imágenes | OK |
| Arquitectura | Patrón MVC | OK |
| Estructura | 3 módulos (Modelo, Vista, Controlador) | OK |
| Validaciones | Verificar tipos/formato de archivos de entrada esperados | OK |
| Seguridad | Autenticación JWT entre servicios | OK |
| Helpers | Protección de puertos y manejo de errores por defecto | Pendiente |
| Respuesta HTTP | Retornar 404 cuando la petición es incorrecta | Pendiente |
| Documentación API | Swagger de los microservicios | OK |

### Notas por módulo

- Validaciones:
	- Los archivos de entrada deben ser los esperados.
	- Se requiere un JWT válido en el header Authorization.
- Helpers:
	- Protección de puertos.
	- Manejo de errores por defecto (por ejemplo, 404 para peticiones incorrectas).



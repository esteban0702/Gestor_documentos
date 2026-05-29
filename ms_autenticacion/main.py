from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, get_db
from app.models.user import User
from app.views.schemas import UserResponse
from app.controllers.auth_controller import router as auth_router
from app.services.security import get_current_user
from database import Base

# ── Crear tablas ──────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ms_autenticacion — GestorDocs",
    description="""
## Microservicio de Autenticación JWT — Arquitectura MVC
1. **POST /auth/register** — crea el usuario
2. **POST /auth/login** — obtén el token
3. Clic en **Authorize 🔒** y pega el token
    """,
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ─────────────────────────────────────────────────────────────────────
app.include_router(auth_router)

@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "service": "ms_autenticacion", "port": 8001, "arquitectura": "MVC"}

@app.get("/health/db", tags=["Health"], summary="Test conexión BD")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "conectada"}
    except Exception as e:
        return {"database": "error", "detalle": str(e)}

@app.get("/users/me", response_model=UserResponse, tags=["Users"], summary="Mi perfil (requiere JWT)")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# ── Swagger con Authorize ─────────────────────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi

# ── Crear tablas si no existen ────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ms_autenticacion — GestorDocs",
    description="""
## Microservicio de Autenticación JWT

Valida credenciales contra PostgreSQL (Supabase) y emite tokens JWT.

### Flujo básico
1. **POST /auth/register** — crea el usuario
2. **POST /auth/login** — obtén el `token`
3. Haz clic en **Authorize ** y pega el token para probar rutas protegidas
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS: permite peticiones del frontend de Esteban ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # frontend Next.js local
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rutas ─────────────────────────────────────────────────────────────────────
app.include_router(auth_router)


# ── Ruta raíz (health check) ──────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "service": "ms_autenticacion", "port": 8001}


# ── Ruta protegida de ejemplo ─────────────────────────────────────────────────
@app.get(
    "/users/me",
    response_model=UserResponse,
    tags=["Users"],
    summary="Mi perfil (requiere JWT)",
)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Ruta de prueba protegida — solo accesible con JWT válido."""
    return current_user


# ── Swagger con botón Authorize para JWT ──────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Agrega el esquema de seguridad Bearer para el botón Authorize 🔒
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Pega aquí el token obtenido en /auth/login",
        }
    }

    # Aplica el esquema a todas las rutas automáticamente
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

# # 1. Verificar conexión a BD — agrega este endpoint temporal

# @app.get("/health/db", tags=["Health"], summary="Test conexión BD")
# def check_db(db: Session = Depends(get_db)):
#     try:
#         db.execute(text("SELECT 1"))
#         return {"database": "conectada ✅", "host": "supabase pooler"}
#     except Exception as e:
#         return {"database": "error ❌", "detalle": str(e)}
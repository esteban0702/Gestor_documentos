from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import engine, get_db, Base
from app.models.user import User
from app.views.schemas import UserResponse
from app.controllers.auth_controller import router as auth_router
from app.services.security import get_current_user, create_access_token


# ── Crear tablas si no existen ────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ms_autenticacion — GestorDocs",
    description="""
## Microservicio de Autenticación JWT

1. POST /auth/register
2. POST /auth/login
3. Usa Authorize para probar rutas protegidas
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS: necesario para preflight OPTIONS del frontend ──────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.20.30:3000",
        "http://192.168.20.39:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "service": "ms_autenticacion", "port": 8001}


@app.get("/health/db", tags=["Health"], summary="Test conexión BD")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "conectada"}
    except Exception as e:
        return {"database": "error", "detalle": str(e)}


# ── Token de prueba (temporal) ───────────────────────────────────────────────
@app.get("/token-test", tags=["Testing"])
def token_test():
    token = create_access_token({"sub": "admin", "id": "123"})
    return {"token": token}


# ── Ruta protegida de prueba ──────────────────────────────────────────────────
@app.get("/users/me", response_model=UserResponse, tags=["Users"], summary="Mi perfil")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


# ── Swagger JWT ───────────────────────────────────────────────────────────────
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
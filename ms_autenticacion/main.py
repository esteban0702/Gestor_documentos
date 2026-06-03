from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.models.user import User
from app.views.schemas import UserResponse
from app.controllers.auth_controller import router as auth_router
from app.services.security import (
    get_current_user,
    create_access_token
)

# ─────────────────────────────────────────────────────────────────────────────
# APP
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTERS
# ─────────────────────────────────────────────────────────────────────────────

app.include_router(auth_router)

# ─────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "service": "ms_autenticacion",
        "port": 8001
    }

# ─────────────────────────────────────────────────────────────────────────────
# TOKEN DE PRUEBA (TEMPORAL)
#
# Este endpoint permite generar un JWT sin usar la base de datos.
# Úsalo únicamente mientras terminas la configuración de PostgreSQL/Supabase.
#
# Eliminar cuando el login real esté funcionando.
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/token-test", tags=["Testing"])
def token_test():

    token = create_access_token(
        {
            "sub": "admin",
            "id": "123"
        }
    )

    return {
        "token": token
    }

# ─────────────────────────────────────────────────────────────────────────────
# RUTA PROTEGIDA DE PRUEBA
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/users/me",
    response_model=UserResponse,
    tags=["Users"]
)
def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

# ─────────────────────────────────────────────────────────────────────────────
# SWAGGER JWT
# ─────────────────────────────────────────────────────────────────────────────

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
            "bearerFormat": "JWT"
        }
    }

    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault(
                "security",
                [{"BearerAuth": []}]
            )

    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi
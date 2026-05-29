from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


# ── REQUEST: Registro ────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    usuario:   str = Field(..., min_length=3, max_length=50,  example="jperez")
    nombre:    str = Field(..., min_length=2, max_length=100, example="Juan Pérez")
    contrasena: str = Field(..., min_length=6,                example="asd123")
    perfil:    str = Field(default="admin",                 example="admin")


# ── REQUEST: Login  ──────────────────────────────────────────────────────────
# El frontend de Esteban envía exactamente estos campos:
# { "usuario": "jperez", "password": "mi_clave" }
class UserLogin(BaseModel):
    usuario:  str = Field(..., example="Jhon")
    password: str = Field(..., example="asd123")


# ── RESPONSE: datos del usuario (sin contraseña) ─────────────────────────────
class UserPublic(BaseModel):
    id:     UUID
    nombre: str
    rol:    str   # el frontend espera "rol", no "perfil"

    class Config:
        from_attributes = True


# ── RESPONSE: Login exitoso ───────────────────────────────────────────────────
# El frontend de Esteban espera exactamente:
# { "token": "eyJ...", "usuario": { "id": ..., "nombre": ..., "rol": ... } }
class LoginResponse(BaseModel):
    token:   str
    usuario: UserPublic


# ── RESPONSE: Registro / perfil completo ─────────────────────────────────────
class UserResponse(BaseModel):
    user_id: UUID
    usuario: str
    nombre:  str
    perfil:  str
    estado:  str
    fecha:   datetime

    class Config:
        from_attributes = True


# ── RESPONSE: Validate token ─────────────────────────────────────────────────
class ValidateResponse(BaseModel):
    valid:   bool
    usuario: Optional[UserPublic] = None


# ── RESPONSE: Mensajes genéricos ─────────────────────────────────────────────
class MessageResponse(BaseModel):
    message: str

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from app.models.user import User
from app.views.schemas import (
    UserCreate, UserLogin, LoginResponse,
    UserResponse, ValidateResponse, MessageResponse
)
from app.services.security import (
    verify_password, get_password_hash,
    create_access_token, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── POST /auth/register ───────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Crea un nuevo usuario con la contraseña hasheada."""

    # Verificar duplicado
    if db.query(User).filter(User.usuario == user.usuario).first():
        raise HTTPException(status_code=400, detail="El usuario ya está registrado.")

    new_user = User(
        usuario    = user.usuario,
        nombre     = user.nombre,
        contrasena = get_password_hash(user.contrasena),
        perfil     = user.perfil,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ── POST /auth/login ──────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Iniciar sesión — devuelve JWT",
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Valida usuario y contraseña contra la BD.
    Devuelve el JWT y los datos básicos del usuario.

    El frontend de Esteban espera exactamente:
    { "token": "...", "usuario": { "id": ..., "nombre": ..., "rol": ... } }
    """
    user = db.query(User).filter(User.usuario == credentials.usuario).first()

    if not user or not verify_password(credentials.password, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    if user.estado.lower() != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacta al administrador.",
        )

    token = create_access_token(
        data={"sub": user.usuario, "id": str(user.user_id)}
    )

    return {
        "token": token,
        "usuario": {
            "id":     user.user_id,
            "nombre": user.nombre,
            "rol":    user.perfil,   # el frontend llama "rol" a lo que BD guarda como "perfil"
        },
    }


# ── GET /auth/validate ────────────────────────────────────────────────────────
@router.get(
    "/validate",
    response_model=ValidateResponse,
    summary="Verificar si el token sigue activo",
)
def validate_token(
    current_user: User = Depends(get_current_user),
):
    """El frontend llama a esto para saber si la sesión sigue viva."""
    return {
        "valid": True,
        "usuario": {
            "id":     current_user.user_id,
            "nombre": current_user.nombre,
            "rol":    current_user.perfil,
        },
    }


# ── POST /auth/logout ─────────────────────────────────────────────────────────
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Cerrar sesión",
)
def logout(current_user: User = Depends(get_current_user)):
    """
    JWT es stateless: la invalidación real la hace el frontend borrando la cookie.
    Este endpoint confirma el logout para el flujo de Esteban.
    """
    return {"message": f"Sesión cerrada para {current_user.usuario}."}


# ── GET /usuarios ─────────────────────────────────────────────────────────────
@router.get(
    "/usuarios",
    response_model=list[UserResponse],
    summary="Listar todos los usuarios (admin)",
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.perfil != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores.")
    return db.query(User).all()


# ── POST /usuarios ────────────────────────────────────────────────────────────
@router.post(
    "/usuarios",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario (admin)",
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.perfil != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores.")
    return register(user, db)   # reutiliza la lógica de registro


# ── PATCH /usuarios/{id}/inactivar ────────────────────────────────────────────
@router.patch(
    "/usuarios/{user_id}/inactivar",
    response_model=UserResponse,
    summary="Inactivar usuario (admin)",
)
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.perfil != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores.")

    user = db.query(User).filter(User.usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    user.estado = "inactivo"
    db.commit()
    db.refresh(user)
    return user

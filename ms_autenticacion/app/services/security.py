import os
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from app.models.user import User


# ── Configuración ─────────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY                 = os.getenv("SECRET_KEY", "cambia_esto_en_produccion")
ALGORITHM                  = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))


# ── Contraseñas ───────────────────────────────────────────────────────────────
def verify_password(plain: str, hashed: str) -> bool:
    """Compara la contraseña plana con el hash almacenado en BD."""
    return pwd_context.verify(plain, hashed)


def get_password_hash(password: str) -> str:
    """Hashea la contraseña con bcrypt antes de guardarla."""
    return pwd_context.hash(password)


# ── JWT ───────────────────────────────────────────────────────────────────────
def create_access_token(data: dict) -> str:
    """
    Genera un JWT firmado.
    El payload incluye: sub (usuario), id (uuid), exp (expiración).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica y valida un JWT.
    Lanza HTTPException 401 si el token es inválido o expiró.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── Dependencia: usuario autenticado ─────────────────────────────────────────
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependencia reutilizable: extrae el usuario del JWT y lo busca en BD.
    Úsala en cualquier ruta protegida con Depends(get_current_user).
    """
    payload = decode_token(token)
    username: str = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token sin usuario.")

    user = db.query(User).filter(User.usuario == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario del token no encontrado.")
    return user

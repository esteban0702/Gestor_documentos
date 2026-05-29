import uuid
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class User(Base):
    """
    Tabla 'usuarios' en Supabase.
    Usa UUID como PK (estándar en Supabase), no Integer.
    """
    __tablename__ = "usuarios"

    user_id    = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    usuario    = Column(String(50),  unique=True, index=True, nullable=False)
    nombre     = Column(String(100), nullable=False)
    contrasena = Column(String(255), nullable=False)   # siempre hasheada con bcrypt
    perfil     = Column(String(50),  nullable=False, default="admin")
    estado     = Column(String(20),  nullable=False, default="Activo")
    fecha      = Column(DateTime(timezone=True), server_default=func.now())

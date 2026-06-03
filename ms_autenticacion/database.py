import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ADVERTENCIA: DATABASE_URL no configurada")
    engine = None
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"},
        pool_pre_ping=True,
    )

if engine:
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
else:
    SessionLocal = None
Base = declarative_base()


def get_db():
    if not SessionLocal:
        raise RuntimeError("Base de datos no configurada")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

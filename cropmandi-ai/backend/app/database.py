import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Point to root cropmandi-ai/cropmandi.db
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = (ROOT_DIR / "cropmandi.db").as_posix()

db_url = f"sqlite:///{DB_PATH}"

connect_args = {"check_same_thread": False}

engine = create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

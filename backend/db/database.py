"""
Database configuration using SQLite (no setup required).
Uses SQLAlchemy ORM with SQLite for zero-config local storage.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# SQLite database file - stored in project root
DB_PATH = os.getenv("DB_PATH", "empathetic_guard.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Models ────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String(100), nullable=False)
    email     = Column(String(200), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, nullable=False, index=True)
    message   = Column(Text, nullable=False)
    response  = Column(Text, nullable=False)
    emotion   = Column(String(50))
    risk      = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)


class EmotionLog(Base):
    __tablename__ = "emotion_logs"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, nullable=False, index=True)
    emotion   = Column(String(50), nullable=False)
    score     = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class RiskLog(Base):
    __tablename__ = "risk_logs"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False, index=True)
    risk_level = Column(String(10), nullable=False)
    message    = Column(Text, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency: yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

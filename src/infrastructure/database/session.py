import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

load_dotenv()


def get_db_url():
    """Get database URL with fallback to SQLite for local development"""
    db_url = os.getenv("POSTGRES_URL")
    if db_url:
        result = urlparse(db_url)
        if result.scheme == "postgres":
            db_url = db_url.replace("postgres://", "postgresql://", 1)
    else:
        db_url = "sqlite:///data/price_history.db"
    return db_url


engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

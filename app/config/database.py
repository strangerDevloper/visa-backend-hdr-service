# app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Convert PostgresDsn to string explicitly
database_url = str(settings.DATABASE_URL)

engine = create_engine(
    database_url,  # Now passing a string
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    connect_args={
        "connect_timeout": 5  # Optional: add connection timeout
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
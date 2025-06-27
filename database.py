from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # ✅ Fix: import declarative_base
import os
import redis

# ✅ Expose Base so other modules like models.py or conftest.py can use it
Base = declarative_base()

# Redis setup
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Database URL - defaults to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./book_reviews.db")

# SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

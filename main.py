from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import redis
import json
import logging
from contextlib import asynccontextmanager

# Avoid circular imports
from database import get_db, engine, redis_client
import models  # Register models before metadata.create_all
from models import Book as BookModel
from models import Base
from schemas import BookCreate, Book, ReviewCreate, Review
from crud import (
    create_book, get_books, get_book,
    create_review, get_reviews_by_book
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("📘 Database tables created")
    if redis_client:
        try:
            redis_client.ping()
            logger.info("✅ Redis cache connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis is NOT available at startup: {e}")
    else:
        logger.warning("⚠️ Redis client is not configured")
    yield

app = FastAPI(
    title="Book Review Service",
    description="A service for managing books and their reviews",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Book Review Service API"}

@app.get("/books", response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
    cache_key = "books:all"

    if redis_client:
        try:
            cached_books = redis_client.get(cache_key)
            if cached_books:
                logger.info("📦 Cache hit - returning books from Redis")
                return json.loads(cached_books)
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable: {e}")

    try:
        books = db.query(BookModel).all()
        logger.info(f"📚 Retrieved {len(books)} books from DB")
        result = [Book.model_validate(book) for book in books]
    except Exception as e:
        logger.exception(f"❌ Error during book processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch books")

    if redis_client:
        try:
            redis_client.setex(cache_key, 300, json.dumps([b.model_dump() for b in result], default=str))
            logger.info("✅ Books cached successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to cache books: {e}")

    return result

@app.post("/books", response_model=Book, status_code=201)
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        db_book = create_book(db, book)
        if redis_client:
            try:
                redis_client.delete("books:all")
                logger.info("🧹 Books cache invalidated")
            except Exception as e:
                logger.warning(f"⚠️ Failed to invalidate cache: {e}")
        return db_book
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create book")

@app.get("/books/{book_id}/reviews", response_model=List[Review])
async def get_book_reviews(book_id: int, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        return get_reviews_by_book(db, book_id)
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch reviews")

@app.post("/books/{book_id}/reviews", response_model=Review, status_code=201)
async def add_book_review(book_id: int, review: ReviewCreate, db: Session = Depends(get_db)):
    book = get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        return create_review(db, review, book_id)
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create review")

@app.get("/health")
async def health_check():
    redis_status = "not configured"
    if redis_client:
        try:
            redis_client.ping()
            redis_status = "connected"
        except Exception:
            redis_status = "disconnected"

    return {
        "status": "healthy",
        "database": "sqlite",
        "redis": redis_status
    }

@app.get("/debug-cache")
async def debug_cache():
    if redis_client:
        try:
            data = redis_client.get("books:all")
            return {
                "present": bool(data),
                "content": json.loads(data) if data else None
            }
        except Exception as e:
            return {"error": str(e)}
    return {"redis": "disabled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

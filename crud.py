from sqlalchemy.orm import Session
from models import Book, Review
from schemas import BookCreate, ReviewCreate
from typing import List

def get_books(db: Session) -> List[Book]:
    """Get all books from database."""
    return db.query(Book).all()

def get_book(db: Session, book_id: int) -> Book:
    """Get a specific book by ID."""
    return db.query(Book).filter(Book.id == book_id).first()

def create_book(db: Session, book: BookCreate) -> Book:
    """Create a new book."""
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_reviews_by_book(db: Session, book_id: int) -> List[Review]:
    """Get all reviews for a specific book."""
    return db.query(Review).filter(Review.book_id == book_id).order_by(Review.created_at.desc()).all()

def create_review(db: Session, review: ReviewCreate, book_id: int) -> Review:
    """Create a new review for a book."""
    db_review = Review(**review.model_dump(), book_id=book_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

"""
Script to populate the database with sample data for testing
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Book, Review

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def seed_database():
    """Add sample data to the database"""
    
    # Create tables first
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Book).count() > 0:
            print("Database already has data. Skipping seed.")
            return
        
        # Sample books
        books_data = [
            {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "isbn": "9780743273565",
                "publication_year": 1925,
                "description": "A classic American novel about the Jazz Age"
            },
            {
                "title": "To Kill a Mockingbird",
                "author": "Harper Lee",
                "isbn": "9780061120084",
                "publication_year": 1960,
                "description": "A gripping tale of racial injustice and childhood innocence"
            },
            {
                "title": "1984",
                "author": "George Orwell",
                "isbn": "9780451524935",
                "publication_year": 1949,
                "description": "A dystopian social science fiction novel"
            }
        ]
        
        # Create books
        created_books = []
        for book_data in books_data:
            book = Book(**book_data)
            db.add(book)
            created_books.append(book)
        
        db.commit()
        
        # Refresh to get IDs
        for book in created_books:
            db.refresh(book)
        
        # Sample reviews
        reviews_data = [
            {"book_id": created_books[0].id, "reviewer_name": "Alice Johnson", "rating": 5, "comment": "Absolutely brilliant! A masterpiece."},
            {"book_id": created_books[0].id, "reviewer_name": "Bob Smith", "rating": 4, "comment": "Great character development."},
            {"book_id": created_books[1].id, "reviewer_name": "Carol Davis", "rating": 5, "comment": "A powerful and moving story."},
            {"book_id": created_books[2].id, "reviewer_name": "David Wilson", "rating": 4, "comment": "Chilling and thought-provoking."},
        ]
        
        # Create reviews
        for review_data in reviews_data:
            review = Review(**review_data)
            db.add(review)
        
        db.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - Created {len(created_books)} books")
        print(f"   - Created {len(reviews_data)} reviews")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

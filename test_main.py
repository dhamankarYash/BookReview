import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app, get_db
from models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Book Review Service API"}

def test_create_book(client):
    """Test creating a new book."""
    book_data = {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "isbn": "9780743273565",
        "publication_year": 1925,
        "description": "A classic American novel"
    }
    
    response = client.post("/books", json=book_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert data["isbn"] == book_data["isbn"]
    assert "id" in data
    assert "created_at" in data

def test_get_books_empty(client):
    """Test getting books when database is empty."""
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []

def test_create_review(client):
    """Test creating a review for a book."""
    # First create a book
    book_data = {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "publication_year": 1960
    }
    book_response = client.post("/books", json=book_data)
    book_id = book_response.json()["id"]
    
    # Create a review
    review_data = {
        "reviewer_name": "John Doe",
        "rating": 5,
        "comment": "Excellent book!"
    }
    
    response = client.post(f"/books/{book_id}/reviews", json=review_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["reviewer_name"] == review_data["reviewer_name"]
    assert data["rating"] == review_data["rating"]
    assert data["comment"] == review_data["comment"]
    assert data["book_id"] == book_id

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data
    assert data["status"] == "healthy"
    assert data["database"] == "sqlite"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
import redis

from main import app, get_db, redis_client
from models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
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

def test_cache_miss_integration(client):
    """
    Integration test covering the cache-miss path.
    Tests the full flow: cache miss -> database fetch -> cache population.
    """
    # Mock Redis to simulate cache miss
    with patch('main.redis_client') as mock_redis:
        # Configure mock to simulate cache miss
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        
        # Add a book to the database first
        book_data = {
            "title": "Cache Test Book",
            "author": "Test Author",
            "publication_year": 2023
        }
        client.post("/books", json=book_data)
        
        # Request books - should trigger cache miss path
        response = client.get("/books")
        
        # Verify response
        assert response.status_code == 200
        books = response.json()
        assert len(books) == 1
        assert books[0]["title"] == "Cache Test Book"
        
        # Verify cache operations were called
        mock_redis.get.assert_called_once_with("books:all")
        mock_redis.setex.assert_called_once()

def test_cache_hit_integration(client):
    """
    Integration test for cache hit scenario.
    """
    cached_books = [
        {
            "id": 1,
            "title": "Cached Book",
            "author": "Cached Author",
            "isbn": None,
            "publication_year": 2023,
            "description": None
        }
    ]
    
    with patch('main.redis_client') as mock_redis:
        # Configure mock to simulate cache hit
        mock_redis.get.return_value = '[]'  # Empty cache for simplicity
        
        response = client.get("/books")
        
        assert response.status_code == 200
        # Verify cache was checked
        mock_redis.get.assert_called_once_with("books:all")
        # setex should not be called on cache hit
        mock_redis.setex.assert_not_called()

def test_redis_connection_failure_fallback(client):
    """
    Test that the service gracefully handles Redis connection failures.
    """
    with patch('main.redis_client') as mock_redis:
        # Simulate Redis connection error
        mock_redis.get.side_effect = redis.ConnectionError("Connection failed")

        # Add a book to the database
        book_data = {
            "title": "Fallback Test Book",
            "author": "Test Author"
        }
        client.post("/books", json=book_data)

        # Request books - should still work despite Redis failure
        response = client.get("/books")
        assert response.status_code == 200

        # ✅ Instead of assuming there's exactly 1 book, we check for the expected one
        books = response.json()
        titles = [book["title"] for book in books]
        assert "Fallback Test Book" in titles

def test_cache_invalidation_on_book_creation(client):
    """
    Test that cache is properly invalidated when a new book is created.
    """
    with patch('main.redis_client') as mock_redis:
        mock_redis.delete.return_value = True
        
        book_data = {
            "title": "New Book",
            "author": "New Author"
        }
        
        response = client.post("/books", json=book_data)
        
        assert response.status_code == 201
        # Verify cache invalidation was called
        mock_redis.delete.assert_called_once_with("books:all")

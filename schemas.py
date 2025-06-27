from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# ✅ Use new Pydantic V2 config (ConfigDict)
from pydantic import ConfigDict

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, pattern=r'^\d{10}(\d{3})?$')
    publication_year: Optional[int] = Field(None, ge=1000, le=2030)
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # ✅ replaces class Config

class ReviewBase(BaseModel):
    reviewer_name: str = Field(..., min_length=1, max_length=255)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    book_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # ✅ replaces class Config

class BookWithReviews(Book):
    reviews: List[Review] = []

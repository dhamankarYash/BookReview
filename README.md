# 📚 Book Review Service — Full Stack Application

A comprehensive Book Review Service built with **FastAPI** (backend) and **vanilla JavaScript** (frontend), featuring Redis caching, robust testing, and a modern responsive design.

🎥 **[Watch Demo Video](https://www.loom.com/share/2144b5f718b54f2aa115efd0fe61b7b6)**

---

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│ (HTML/CSS/JS)   │◄──►│    FastAPI      │◄──►│    SQLite       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Cache Layer   │
                       │     Redis       │
                       └─────────────────┘
```

---

## 🚀 Features

### 🧠 Backend Features
- ✅ RESTful API with FastAPI
- ✅ Auto API docs (Swagger/OpenAPI)
- ✅ SQLAlchemy ORM + Alembic migrations
- ✅ Redis cache with fallback support
- ✅ Graceful error handling & logging
- ✅ Pydantic input validation
- ✅ Unit and integration tests
- ✅ Indexed database tables

### 🎨 Frontend Features
- ✅ Responsive UI (CSS Grid/Flexbox)
- ✅ Book CRUD + star-based reviews
- ✅ Live search and filter
- ✅ Toast alerts & modal dialogs
- ✅ API health monitoring
- ✅ Mobile-first design

---

## 📁 Project Structure

```
book-review-service/
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # DB connection
│   ├── crud.py                 # DB logic
│   ├── cache.py                # Redis logic
│   ├── test_main.py            # Unit tests
│   ├── test_integration.py     # Integration tests
│   ├── seed_data.py            # Seeder script
│   ├── alembic.ini             # Migration config
│   ├── alembic/                # Migration scripts
│   ├── scripts/                # Setup/start/test scripts
│   └── requirements.txt
├── frontend/
│   ├── index.html              # UI
│   ├── styles.css              # Styling
│   ├── script.js               # JS logic
│   └── assets/
├── docs/                       # Project docs
├── README.md                   # This file
└── LICENSE
```

---

## 🛠️ Technology Stack

### Backend
- FastAPI 0.104.1
- SQLite + SQLAlchemy 2.0.23
- Alembic 1.12.1
- Redis 5.0.1
- Pydantic 2.5.0
- Pytest 7.4.3
- Uvicorn

### Frontend
- HTML5, CSS3, JS (ES6+)
- Flexbox, CSS Grid
- Font Awesome, Google Fonts (Inter)

---

## 🔄 Redis Caching Strategy

- Cache-aside pattern with 5-min TTL
- Automatic fallback if Redis is down
- Cache invalidation on book creation
- Reduced DB load via cached listings

---

## ⚙️ Quick Start Guide

### Prerequisites
- Python 3.8+
- Redis (optional)
- Web browser

### Backend Setup

```bash
git clone <repository-url>
cd book-review-service/backend
python -m venv venv
venv\Scripts\activate     # On Windows
# source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
alembic upgrade head
python seed_data.py
uvicorn main:app --reload
```

### Redis Setup (Optional)

```bash
# Local
redis-server

# Or with Docker
docker run -p 6379:6379 redis
```

### Frontend Setup

```bash
cd ../frontend
python -m http.server 3000
```

### Access

- Frontend: http://localhost:3000  
- Backend API: http://localhost:8000  
- Swagger Docs: http://localhost:8000/docs  
- Redoc: http://localhost:8000/redoc  

---

## 📊 API Endpoints

| Method | Endpoint                  | Description            |
|--------|---------------------------|------------------------|
| GET    | `/`                       | Welcome endpoint       |
| GET    | `/health`                | Health check           |
| GET    | `/books`                 | Fetch all books        |
| POST   | `/books`                 | Add a new book         |
| GET    | `/books/{id}/reviews`    | Get book reviews       |
| POST   | `/books/{id}/reviews`    | Submit a review        |

---

## ✅ Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific files
pytest test_main.py -v
pytest test_integration.py -v
```

---

## 🏗️ Architecture Decisions

- **FastAPI**: async support + auto docs + modern syntax
- **SQLite**: lightweight, easy local setup
- **Redis**: simple and effective cache layer
- **Vanilla JS**: fast loading, full control over UX

---

## 🔐 Security Considerations

- Input validation with Pydantic  
- SQL injection protection via ORM  
- Sanitized error messages  
- Logging for debugging

---

## 🚀 Deployment

### Backend

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker (Optional)
docker build -t book-review-api .
docker run -p 8000:8000 book-review-api
```

### Frontend
- Deploy `index.html`, `script.js`, and `styles.css` to Netlify/Vercel
- Update API URL in `script.js`
- Enable CORS on the backend

---


## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)  
- [SQLAlchemy](https://www.sqlalchemy.org/)  
- [Redis](https://redis.io/)  
- [Font Awesome](https://fontawesome.com/)  
- [Google Fonts](https://fonts.google.com/)

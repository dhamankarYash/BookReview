import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, engine, get_db
from fastapi.testclient import TestClient
from main import app

# ✅ Create tables before running any tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ✅ Use a new database session for each test
@pytest.fixture
def db_session():
    SessionTesting = sessionmaker(bind=engine)
    session = SessionTesting()
    try:
        yield session
    finally:
        session.close()

# ✅ Inject test DB session into FastAPI dependency
@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

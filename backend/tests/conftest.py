import os

# Force SQLite for tests before any app module imports settings
os.environ["DATABASE_URL"] = "sqlite:///./test_fmppi.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.deps import get_db
from app.database import Base
from app.main import app
from app.security.rate_limit import _counters

TEST_URL = "sqlite:///./test_fmppi.db"
test_engine = create_engine(TEST_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="session", autouse=True)
def init_schema() -> None:
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db() -> Session:
    # Fully isolated DB per test: recreate schema on the shared test file.
    _counters.clear()
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)

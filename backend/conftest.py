import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import main
import database
import models
import auth


@pytest.fixture(scope="session")
def db_engine():
    url = os.environ.get("FMPPI_TEST_DATABASE_URL")
    container = None
    if not url:
        try:
            from testcontainers.postgres import PostgresContainer
            container = PostgresContainer("postgres:15-alpine")
            container.start()
            url = container.get_connection_url()
        except Exception:
            container = None
            url = "sqlite:///./fmppi_test.db"
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=connect_args)
    models.Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()
    if container is not None:
        container.stop()


@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def make_client(db_session):
    def factory(role="admin"):
        main.app.dependency_overrides.clear()

        def override_get_db():
            yield db_session

        def override_user():
            return {"username": "tester", "role": role}

        main.app.dependency_overrides[database.get_db] = override_get_db
        main.app.dependency_overrides[auth.get_current_user] = override_user
        return TestClient(main.app)

    return factory


@pytest.fixture
def client(make_client):
    return make_client("admin")

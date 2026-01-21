# tests/conftest.py
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.pool import StaticPool  # <--- 1. IMPORT THIS
from main import app, get_session

TEST_DB_URL = "sqlite://"


@pytest.fixture(name="session")
def session_fixture():
    # 2. ADD poolclass=StaticPool TO THE ENGINE
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    # Now when this runs, the connection stays open thanks to StaticPool
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    # Cleanup
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
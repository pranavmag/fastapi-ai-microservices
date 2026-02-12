from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.pool import StaticPool
from main import app, get_session, User, hash_password

TEST_DB_URL = "sqlite://"

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user in the database."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient, test_user: User):
    """Login and return a valid JWT token."""
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"}
    )
    return response.json()["access_token"]

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """Return authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}

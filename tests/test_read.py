from fastapi.testclient import TestClient
from sqlmodel import Session
from main import Note


def test_read_notes_empty(client: TestClient):
    """Test that reading from an empty database returns an empty list."""
    response = client.get("/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_read_multiple_notes(session: Session, client: TestClient):
    """Test reading multiple notes from the database."""
    # Arrange: Inject data directly into DB
    session.add(Note(content="First", is_completed=False))
    session.add(Note(content="Second", is_completed=True))
    session.commit()

    # Act
    response = client.get("/notes")

    # Assert
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["content"] == "First"
    assert data[1]["content"] == "Second"


def test_get_note_by_id_success(client: TestClient):
    """Test fetching a single note by its specific ID."""
    # Arrange: Create a note via API to ensure valid ID
    setup_resp = client.post("/notes", json={"content": "Target", "is_completed": False})
    note_id = setup_resp.json()["id"]

    # Act
    response = client.get(f"/notes/{note_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["content"] == "Target"
    assert response.json()["id"] == note_id


def test_get_note_by_id_not_found(client: TestClient):
    """Test that requesting a non-existent ID returns 404."""
    response = client.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
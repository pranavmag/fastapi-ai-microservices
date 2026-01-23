# tests/test_main.py
from fastapi.testclient import TestClient
from sqlmodel import Session
from main import Note


# pytest automatically finds the 'client' fixture in conftest.py
def test_read_notes_empty(client: TestClient):
    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == []  # Must be empty list

def test_create_and_read_note(client: TestClient):
    # 1. Create a note
    client.post("/notes", json={"content": "Buy milk", "is_completed": False})

    # 2. Read it back
    response = client.get("/notes")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["content"] == "Buy milk"

def test_read_multiple_notes(session: Session, client: TestClient):
    # 1. Inject data directly (bypassing the API)
    note_1 = Note(content="First", is_completed=False)
    note_2 = Note(content="Second", is_completed=True)
    session.add(note_1)
    session.add(note_2)
    session.commit()

    # 2. Read via API
    response = client.get("/notes")
    data = response.json()

    assert len(data) == 2
    assert data[0]["content"] == "First"
    assert data[1]["content"] == "Second"


def test_create_note_invalid_type(client: TestClient):
    # content should be a string, we send an integer
    payload = {"content": 123, "is_completed": False}

    response = client.post("/notes", json=payload)

    # 422 means "We understood the request, but the data is wrong"
    assert response.status_code == 422


def test_create_note_missing_content(client: TestClient):
    # "content" is required in our schema. We send an empty object.
    payload = {"is_completed": False}

    response = client.post("/notes", json=payload)

    assert response.status_code == 422
    # Verify the error message mentions the missing field
    assert "Field required" in response.json()["detail"][0]["msg"]


def test_get_note_by_id_success(client: TestClient):
    # 1. Create a note to get its ID
    # Note: We use your new strict input format!
    payload = {"content": "Target Note", "is_completed": False}
    create_response = client.post("/notes", json=payload)
    data = create_response.json()
    note_id = data["id"]

    # 2. Fetch that specific ID
    response = client.get(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.json()["content"] == "Target Note"
    assert response.json()["id"] == note_id


def test_get_note_by_id_not_found(client: TestClient):
    # 999 is unlikely to exist in an ephemeral test DB
    response = client.get("/notes/999")

    assert response.status_code == 404
    # Verify the clean JSON error message
    assert response.json()["detail"] == "Note not found"
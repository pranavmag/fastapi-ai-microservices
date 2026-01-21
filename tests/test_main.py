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


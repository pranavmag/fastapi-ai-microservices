import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from main import Note, User, hash_password


def test_update_note_success(client: TestClient, auth_headers: dict):
    """Test successfully updating a note."""
    # Create a note
    create_resp = client.post(
        "/notes",
        json={"content": "Original content", "is_completed": False, "tags": "test"},
        headers=auth_headers
    )
    note_id = create_resp.json()["id"]
    
    # Update it
    update_resp = client.put(
        f"/notes/{note_id}",
        json={"content": "Updated content!", "is_completed": True, "tags": "updated"},
        headers=auth_headers
    )
    
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["content"] == "Updated content!"
    assert data["is_completed"] == True
    assert data["tags"] == "updated"


def test_update_note_not_found(client: TestClient, auth_headers: dict):
    """Test updating a non-existent note returns 404."""
    response = client.put(
        "/notes/99999",
        json={"content": "Doesn't matter", "is_completed": False, "tags": "test"},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note_unauthorized(client: TestClient):
    """Test updating without auth token returns 401."""
    response = client.put(
        "/notes/1",
        json={"content": "Hacker trying", "is_completed": False, "tags": "bad"}
    )
    assert response.status_code == 401


def test_update_note_wrong_user(session: Session, client: TestClient, test_user, auth_headers: dict):
    """Test user cannot update another user's note."""
    # Create a different user
    other_user = User(
        username="otheruser",
        email="other@example.com",
        hashed_password=hash_password("otherpass")
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)
    
    # Create a note belonging to other_user
    other_note = Note(
        content="Other user's note",
        is_completed=False,
        user_id=other_user.id
    )
    session.add(other_note)
    session.commit()
    session.refresh(other_note)
    
    # Try to update it with test_user's token
    response = client.put(
        f"/notes/{other_note.id}",
        json={"content": "Trying to steal", "is_completed": True, "tags": "hack"},
        headers=auth_headers
    )
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this note"


def test_delete_note_success(client: TestClient, auth_headers: dict):
    """Test successfully deleting a note."""
    # Create a note
    create_resp = client.post(
        "/notes",
        json={"content": "To be deleted", "is_completed": False, "tags": "temp"},
        headers=auth_headers
    )
    note_id = create_resp.json()["id"]
    
    # Delete it
    delete_resp = client.delete(f"/notes/{note_id}", headers=auth_headers)
    
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Note deleted successfully"
    assert delete_resp.json()["id"] == note_id
    
    # Verify it's gone
    get_resp = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_delete_note_not_found(client: TestClient, auth_headers: dict):
    """Test deleting a non-existent note returns 404."""
    response = client.delete("/notes/99999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_delete_note_unauthorized(client: TestClient):
    """Test deleting without auth token returns 401."""
    response = client.delete("/notes/1")
    assert response.status_code == 401


def test_delete_note_wrong_user(session: Session, client: TestClient, test_user, auth_headers: dict):
    """Test user cannot delete another user's note."""
    # Create a different user
    other_user = User(
        username="anotheruser",
        email="another@example.com",
        hashed_password=hash_password("anotherpass")
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)
    
    # Create a note belonging to other_user
    other_note = Note(
        content="Protected note",
        is_completed=False,
        user_id=other_user.id
    )
    session.add(other_note)
    session.commit()
    session.refresh(other_note)
    
    # Try to delete it with test_user's token
    response = client.delete(f"/notes/{other_note.id}", headers=auth_headers)
    
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to delete this note"


def test_update_note_validation_error(client: TestClient, auth_headers: dict):
    """Test updating with invalid data returns 422."""
    # Create a note
    create_resp = client.post(
        "/notes",
        json={"content": "Valid", "is_completed": False, "tags": "test"},
        headers=auth_headers
    )
    note_id = create_resp.json()["id"]
    
    # Try to update with empty content
    response = client.put(
        f"/notes/{note_id}",
        json={"content": "", "is_completed": False, "tags": "test"},
        headers=auth_headers
    )
    
    assert response.status_code == 422

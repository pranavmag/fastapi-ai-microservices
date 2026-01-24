# tests/test_create.py
import pytest
from fastapi.testclient import TestClient


def test_create_note_success(client: TestClient):
    """
    Test that POST /notes creates a note and returns 201.

    This verifies the happy path:
    - Valid payload is accepted
    - Note is saved to database with new ID
    - Response matches the Note schema
    """
    payload = {"content": "New Note", "is_completed": False}
    response = client.post("/notes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "New Note"
    assert "id" in data


@pytest.mark.parametrize("payload", [
    # Case 1: Invalid Type (Integer instead of String)
    {"content": 123, "is_completed": False},

    # Case 2: Missing Content (Empty Payload)
    {"is_completed": False},

    # Case 3: Empty String (Business Logic)
    {"content": "", "is_completed": False},
])
def test_create_note_validation_errors(client: TestClient, payload):
    """
    Test that invalid payloads return 422 Unprocessable Entity.

    Covers:
    - Type mismatch (int vs str)
    - Missing required fields
    - Business logic violations (empty strings)
    """
    response = client.post("/notes", json=payload)

    # The key assertion: all invalid inputs should return 422
    assert response.status_code == 422

    # Optional: verify error response has proper structure
    assert "detail" in response.json()
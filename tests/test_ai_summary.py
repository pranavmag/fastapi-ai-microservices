from openai import APITimeoutError
from unittest.mock import MagicMock

def test_note_creation_includes_ai_summary(client, auth_headers):
    """New notes should have an AI summary in the response."""
    response = client.post(
        "/notes",
        json={"content": "Team meeting about Q1 goals and hiring.", "is_completed": False},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "ai_summary" in data
    assert data["ai_summary"] == "This is a mocked AI summary."

def test_note_created_when_ai_fails(client, auth_headers, mocker):
    """Note creation should succeed even when AI API fails."""
    mock_client = mocker.MagicMock()
    mock_client.chat.completions.create.side_effect = APITimeoutError(request=MagicMock())
    mocker.patch("ai_service.OpenAI", return_value=mock_client)

    response = client.post(
        "/notes",
        json={"content": "This note should still be created.", "is_completed": False},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ai_summary"] is None
    assert data["content"] == "This note should still be created."

def test_note_created_when_api_key_missing(client, auth_headers, mocker):
    """Note creation should work with no OPENAI_API_KEY set."""
    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": ""})

    response = client.post(
        "/notes",
        json={"content": "Note with no API key.", "is_completed": False},
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["ai_summary"] is None

"""Unit tests for PagerDuty incident note operations."""

import pytest

from pagerduty_mcp_server import incidents, utils
from pagerduty_mcp_server.models.note import Note


"""
Note Model Tests
"""


@pytest.mark.unit
@pytest.mark.incidents
def test_parse_note(mock_notes, mock_notes_parsed):
    """Test that note parsing works correctly via Pydantic model."""
    model = Note.model_validate(mock_notes[0])
    parsed_note = model.to_clean_dict()
    assert parsed_note == mock_notes_parsed[0]


@pytest.mark.unit
@pytest.mark.incidents
def test_parse_note_missing_fields():
    """Test parsing note with missing fields — None optional fields are excluded."""
    input_data = {"id": "PWL7QXS", "content": "Test content"}

    model = Note.model_validate(input_data)
    result = model.to_clean_dict()
    assert result["id"] == "PWL7QXS"
    assert result["content"] == "Test content"
    # None optional fields are excluded from output by to_clean_dict
    assert "created_at" not in result or result.get("created_at") is None
    assert "user" not in result or result.get("user") is None
    assert "channel" not in result or result.get("channel") is None


"""
API Function Tests
"""


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test__list_notes(mock_get_api_client, mock_notes, mock_notes_parsed):
    """Test that notes are fetched correctly."""
    incident_id = "ABC123"
    mock_get_api_client.jget.return_value = {"notes": mock_notes}

    result = await incidents._list_notes(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/notes"
    )

    expected_response = utils.api_response_handler(
        results=mock_notes_parsed, resource_name="notes"
    )
    assert result == expected_response


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test__list_notes_empty_id(mock_get_api_client):
    """Test that _list_notes raises ValueError for empty incident ID."""
    with pytest.raises(ValueError, match="incident_id cannot be empty"):
        await incidents._list_notes(incident_id="")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test__list_notes_api_error(mock_get_api_client):
    """Test that _list_notes handles API errors correctly."""
    incident_id = "ABC123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_notes(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test__list_notes_missing_notes_field(mock_get_api_client):
    """Test that _list_notes handles missing notes field in response correctly."""
    incident_id = "ABC123"
    mock_get_api_client.jget.return_value = {}  # Missing 'notes' key

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_notes(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch notes for incident {incident_id}: Response missing 'notes' field"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test__list_notes_empty_list(mock_get_api_client):
    """Test that _list_notes handles empty notes list correctly."""
    incident_id = "ABC123"
    mock_get_api_client.jget.return_value = {"notes": []}

    result = await incidents._list_notes(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/notes"
    )

    expected_response = utils.api_response_handler(results=[], resource_name="notes")
    assert result == expected_response

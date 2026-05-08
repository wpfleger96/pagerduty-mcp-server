"""Unit tests for the oncalls module."""

from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import oncalls, utils
from tests.conftest import ApiRuntimeError


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls(mock_get_api_client, mock_oncalls, mock_oncalls_parsed):
    """Test that oncalls are fetched correctly."""
    mock_get_api_client.iter_all.return_value = mock_oncalls

    oncall_list = await oncalls.list_oncalls()

    mock_get_api_client.iter_all.assert_called_once_with(
        oncalls.ONCALLS_URL, params={}, page_size=100
    )
    assert oncall_list == utils.api_response_handler(
        results=mock_oncalls_parsed,
        resource_name="oncalls",
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls_with_earliest(
    mock_get_api_client, mock_oncalls_earliest, mock_oncalls_earliest_parsed
):
    """Test that oncalls are fetched correctly with the earliest parameter."""
    mock_get_api_client.iter_all.return_value = mock_oncalls_earliest

    oncall_list = await oncalls.list_oncalls(earliest=True)

    mock_get_api_client.iter_all.assert_called_once_with(
        oncalls.ONCALLS_URL, params={"earliest": True}, page_size=100
    )

    assert "metadata" in oncall_list
    assert "oncalls" in oncall_list
    assert "error" not in oncall_list
    assert len(oncall_list["oncalls"]) == len(mock_oncalls_earliest_parsed)

    # Build a set of (user_id, policy_id, level, start) tuples for comparison
    expected_entries = {
        (
            entry["user"]["id"],
            entry["escalation_policy"]["id"],
            entry["escalation_level"],
            entry["start"],
        )
        for entry in mock_oncalls_earliest_parsed
    }

    for oncall in oncall_list["oncalls"]:
        key = (
            oncall["user"]["id"],
            oncall["escalation_policy"]["id"],
            oncall["escalation_level"],
            oncall["start"],
        )
        assert key in expected_entries, f"Unexpected entry for {key}"

    for oncall in oncall_list["oncalls"]:
        assert "user" in oncall
        assert "escalation_policy" in oncall
        assert "schedule" in oncall
        assert "escalation_level" in oncall
        assert "start" in oncall
        assert "end" in oncall


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls_api_error(mock_get_api_client):
    """Test that list_oncalls handles API errors correctly."""
    mock_get_api_client.iter_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await oncalls.list_oncalls()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls_empty_response(mock_get_api_client):
    """Test that list_oncalls handles empty response correctly."""
    mock_get_api_client.iter_all.return_value = []

    oncall_list = await oncalls.list_oncalls()
    assert oncall_list == utils.api_response_handler(
        results=[], resource_name="oncalls"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls_preserves_full_error_message(mock_get_api_client):
    """Test that list_oncalls preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = ApiRuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.iter_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        await oncalls.list_oncalls()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.oncalls
async def test_list_oncalls_with_include(mock_get_api_client, mock_oncalls):
    """Test that oncalls can be filtered to include only specific fields."""
    mock_get_api_client.iter_all.return_value = mock_oncalls

    oncall_list = await oncalls.list_oncalls(include=["user", "escalation_level"])

    assert len(oncall_list["oncalls"]) > 0
    for oncall in oncall_list["oncalls"]:
        assert "user" in oncall
        assert "escalation_level" in oncall
        assert len(oncall.keys()) == 2

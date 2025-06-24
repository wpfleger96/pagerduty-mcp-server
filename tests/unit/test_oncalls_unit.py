"""Unit tests for the oncalls module."""

from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import oncalls, utils
from pagerduty_mcp_server.parsers.oncall_parser import parse_oncall


@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls(mock_get_api_client, mock_oncalls, mock_oncalls_parsed):
    """Test that oncalls are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_oncalls

    oncall_list = oncalls.list_oncalls()

    mock_get_api_client.list_all.assert_called_once_with(oncalls.ONCALLS_URL, params={})
    assert oncall_list == utils.api_response_handler(
        results=[parse_oncall(result=oncall) for oncall in mock_oncalls],
        resource_name="oncalls",
    )


@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls_with_earliest(
    mock_get_api_client, mock_oncalls_earliest, mock_oncalls_earliest_parsed
):
    """Test that oncalls are fetched correctly with the earliest parameter.

    This test verifies that when earliest=True:
    1. The parameter is passed correctly to the API
    2. The response is processed correctly
    3. The filtering behavior works as expected - returns the earliest on-call for each unique
       combination of user, escalation policy, and escalation level within the time range
    """
    # Mock the API to return the filtered response (what the API would return with earliest=True)
    mock_get_api_client.list_all.return_value = mock_oncalls_earliest_parsed

    # Call list_oncalls with earliest=True
    oncall_list = oncalls.list_oncalls(earliest=True)

    # Verify the API was called with the correct parameter
    mock_get_api_client.list_all.assert_called_once_with(
        oncalls.ONCALLS_URL, params={"earliest": True}
    )

    # Verify the response structure
    assert "metadata" in oncall_list
    assert "oncalls" in oncall_list
    assert "error" not in oncall_list

    # Verify that we got exactly one on-call entry for each unique combination of user/policy/level
    # This should be 4 entries:
    # 1. USER1/POLICY1/LEVEL1 (earliest shift: 2024-03-17T18:00:00Z)
    # 2. USER2/POLICY1/LEVEL2 (earliest shift: 2024-03-24T13:00:00Z)
    # 3. USER3/POLICY1/LEVEL2 (earliest shift: 2024-03-24T15:00:00Z)
    # 4. USER4/POLICY1/LEVEL3 (long-term assignment: 2021-08-04T21:52:39Z)
    assert len(oncall_list["oncalls"]) == len(mock_oncalls_earliest_parsed)

    # Verify that we got the expected entries
    expected_entries = {
        (
            entry["user"]["id"],
            entry["escalation_policy"]["id"],
            entry["escalation_level"],
        ): entry["start"]
        for entry in mock_oncalls_earliest_parsed
    }

    for oncall in oncall_list["oncalls"]:
        key = (
            oncall["user"]["id"],
            oncall["escalation_policy"]["id"],
            oncall["escalation_level"],
        )
        assert key in expected_entries, f"Unexpected entry for {key}"
        assert oncall["start"] == expected_entries[key], f"Wrong start time for {key}"

    # Verify that all entries are properly parsed
    for oncall in oncall_list["oncalls"]:
        assert "user" in oncall
        assert "escalation_policy" in oncall
        assert "schedule" in oncall
        assert "escalation_level" in oncall
        assert "start" in oncall
        assert "end" in oncall


@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls_api_error(mock_get_api_client):
    """Test that list_oncalls handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        oncalls.list_oncalls()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls_empty_response(mock_get_api_client):
    """Test that list_oncalls handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    oncall_list = oncalls.list_oncalls()
    assert oncall_list == utils.api_response_handler(
        results=[], resource_name="oncalls"
    )


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.oncalls
def test_parse_oncall(mock_oncalls, mock_oncalls_parsed):
    """Test that parse_oncall correctly parses raw oncall data."""
    parsed_oncall = parse_oncall(result=mock_oncalls[0])
    assert parsed_oncall == mock_oncalls_parsed[0]


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.oncalls
def test_parse_oncall_none():
    """Test that parse_oncall handles None input correctly."""
    assert parse_oncall(result=None) == {}


@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls_preserves_full_error_message(mock_get_api_client):
    """Test that list_oncalls preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.list_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        oncalls.list_oncalls()
    assert str(exc_info.value) == "API Error"

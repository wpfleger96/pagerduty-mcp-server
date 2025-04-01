"""Unit tests for the oncalls module."""

import pytest
from unittest.mock import MagicMock

from pagerduty_mcp_server import oncalls
from pagerduty_mcp_server.parsers.oncall_parser import parse_oncall
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls(mock_get_api_client, mock_oncalls, mock_oncalls_parsed):
    """Test that oncalls are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_oncalls

    oncall_list = oncalls.list_oncalls()

    mock_get_api_client.list_all.assert_called_once_with(oncalls.ONCALLS_URL, params={})
    assert oncall_list == utils.api_response_handler(results=[parse_oncall(result=oncall) for oncall in mock_oncalls], resource_name='oncalls')

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
    assert oncall_list == utils.api_response_handler(results=[], resource_name='oncalls')

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

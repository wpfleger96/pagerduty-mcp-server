"""Unit tests for the oncalls module."""

import pytest

from pagerduty_mcp_server import oncalls
from pagerduty_mcp_server.parsers import parse_oncall
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.oncalls
def test_list_oncalls(mock_get_api_client, mock_oncalls, mock_oncalls_parsed):
    """Test that oncalls are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_oncalls

    oncalls_list = oncalls.list_oncalls()

    mock_get_api_client.list_all.assert_called_once_with(oncalls.ONCALLS_URL, params={})
    assert oncalls_list == utils.api_response_handler(results=[parse_oncall(result=oncall) for oncall in mock_oncalls], resource_name='oncalls')

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.oncalls
def test_parse_oncall(mock_oncalls, mock_oncalls_parsed):
    """Test that oncall parsing works correctly."""
    parsed_oncall = parse_oncall(result=mock_oncalls[0])
    assert parsed_oncall == mock_oncalls_parsed[0]

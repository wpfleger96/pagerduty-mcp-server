"""Unit tests for the schedules module."""

import pytest

from pagerduty_mcp_server import schedules
from pagerduty_mcp_server.parsers import parse_schedule
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.schedules
def test_list_schedules(mock_get_api_client, mock_schedules, mock_schedules_parsed):
    """Test that schedules are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_schedules

    schedules_list = schedules.list_schedules()

    mock_get_api_client.list_all.assert_called_once_with(schedules.SCHEDULES_URL, params={})
    assert schedules_list == utils.api_response_handler(results=[parse_schedule(result=schedule) for schedule in mock_schedules], resource_name='schedules')

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.schedules
def test_parse_schedule(mock_schedules, mock_schedules_parsed):
    """Test that schedule parsing works correctly."""
    parsed_schedule = parse_schedule(result=mock_schedules[0])
    assert parsed_schedule == mock_schedules_parsed[0]

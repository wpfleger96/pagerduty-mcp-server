"""Unit tests for the incidents module."""

import pytest

from pagerduty_mcp_server import incidents
from pagerduty_mcp_server.parsers import parse_incident
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents(mock_get_api_client, mock_incidents):
    """Test that incidents are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_incidents
    params = {'statuses': incidents.DEFAULT_STATUSES, 'urgencies': incidents.DEFAULT_URGENCIES}

    incidents_list = incidents.list_incidents()

    mock_get_api_client.list_all.assert_called_once_with(incidents.INCIDENTS_URL, params=params)
    assert incidents_list == utils.api_response_handler(results=[parse_incident(result=incident) for incident in mock_incidents], resource_name='incidents')

@pytest.mark.unit
@pytest.mark.incidents
def test_parse_incident(mock_incidents, mock_incidents_parsed):
    """Test that incident parsing works correctly."""
    parsed_incident = parse_incident(result=mock_incidents[0])
    assert parsed_incident == mock_incidents_parsed[0]

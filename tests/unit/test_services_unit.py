"""Unit tests for the services module."""

import pytest

from pagerduty_mcp_server import services
from pagerduty_mcp_server.parsers.service_parser import parse_service
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.services
def test_list_services(mock_get_api_client, mock_services, mock_services_parsed):
    """Test that services are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_services

    service_list = services.list_services()

    mock_get_api_client.list_all.assert_called_once_with(services.SERVICES_URL, params={})
    assert service_list == utils.api_response_handler(results=[parse_service(result=service) for service in mock_services], resource_name='services')

@pytest.mark.unit
@pytest.mark.services
def test_fetch_service_ids(mock_get_api_client, mock_team_ids, mock_service_ids, mock_services):
    """Test that service IDs are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_services

    service_ids = services.fetch_service_ids(team_ids=mock_team_ids)

    mock_get_api_client.list_all.assert_called_once_with(services.SERVICES_URL, params={'team_ids[]': mock_team_ids})
    assert set(service_ids) == set(mock_service_ids)

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.services
def test_parse_service(mock_services, mock_services_parsed):
    """Test that parse_service correctly parses raw service data."""
    parsed_service = parse_service(result=mock_services[0])
    assert parsed_service == mock_services_parsed[0]

"""Unit tests for the services module."""

from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import services, utils
from pagerduty_mcp_server.parsers.service_parser import parse_service


@pytest.mark.unit
@pytest.mark.services
def test_list_services(mock_get_api_client, mock_services):
    """Test that services are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_services

    service_list = services.list_services()

    mock_get_api_client.list_all.assert_called_once_with(
        services.SERVICES_URL, params={}
    )
    assert service_list == utils.api_response_handler(
        results=[parse_service(result=service) for service in mock_services],
        resource_name="services",
    )


@pytest.mark.unit
@pytest.mark.services
def test_list_services_with_query(mock_get_api_client, mock_services):
    """Test that services can be filtered by query parameter."""
    query = "test"
    # Filter mock services to only include those with "test" in their name
    filtered_services = [s for s in mock_services if "test" in s["name"].lower()]
    mock_get_api_client.list_all.return_value = filtered_services

    service_list = services.list_services(query=query)

    mock_get_api_client.list_all.assert_called_once_with(
        services.SERVICES_URL, params={"query": query}
    )
    assert service_list == utils.api_response_handler(
        results=[parse_service(result=service) for service in filtered_services],
        resource_name="services",
    )


@pytest.mark.unit
@pytest.mark.services
def test_list_services_with_team_ids(mock_get_api_client, mock_services, mock_team_ids):
    """Test that services can be filtered by team IDs."""
    # Filter mock services to only include those with matching team IDs
    filtered_services = [
        s
        for s in mock_services
        if any(tid in s.get("teams", []) for tid in mock_team_ids)
    ]
    mock_get_api_client.list_all.return_value = filtered_services

    service_list = services.list_services(team_ids=mock_team_ids)

    mock_get_api_client.list_all.assert_called_once_with(
        services.SERVICES_URL, params={"team_ids[]": mock_team_ids}
    )
    assert service_list == utils.api_response_handler(
        results=[parse_service(result=service) for service in filtered_services],
        resource_name="services",
    )


@pytest.mark.unit
@pytest.mark.services
def test_list_services_api_error(mock_get_api_client):
    """Test that list_services handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        services.list_services()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.services
def test_list_services_empty_response(mock_get_api_client):
    """Test that list_services handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    service_list = services.list_services()
    assert service_list == utils.api_response_handler(
        results=[], resource_name="services"
    )


@pytest.mark.unit
@pytest.mark.services
def test_fetch_service_ids(mock_get_api_client, mock_services, mock_team_ids):
    """Test that service IDs are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_services

    service_ids = services.fetch_service_ids(team_ids=mock_team_ids)

    mock_get_api_client.list_all.assert_called_once_with(
        services.SERVICES_URL, params={"team_ids[]": mock_team_ids}
    )
    assert set(service_ids) == set([service["id"] for service in mock_services])


@pytest.mark.unit
@pytest.mark.services
def test_fetch_service_ids_api_error(mock_get_api_client, mock_team_ids):
    """Test that fetch_service_ids handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        services.fetch_service_ids(team_ids=mock_team_ids)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.services
def test_fetch_service_ids_empty_response(mock_get_api_client, mock_team_ids):
    """Test that fetch_service_ids handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    service_ids = services.fetch_service_ids(team_ids=mock_team_ids)
    assert service_ids == []


@pytest.mark.unit
@pytest.mark.services
def test_show_service(mock_get_api_client, mock_services):
    """Test that a single service is fetched correctly."""
    service_id = mock_services[0]["id"]
    mock_get_api_client.jget.return_value = {"service": mock_services[0]}

    service = services.show_service(service_id=service_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{services.SERVICES_URL}/{service_id}"
    )
    assert service == utils.api_response_handler(
        results=parse_service(result=mock_services[0]), resource_name="service"
    )


@pytest.mark.unit
@pytest.mark.services
def test_show_service_invalid_id(mock_get_api_client):
    """Test that show_service raises ValueError for invalid service ID."""
    with pytest.raises(ValueError) as exc_info:
        services.show_service(service_id="")
    assert str(exc_info.value) == "service_id cannot be empty"


@pytest.mark.unit
@pytest.mark.services
def test_show_service_api_error(mock_get_api_client):
    """Test that show_service handles API errors correctly."""
    service_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        services.show_service(service_id=service_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.services
def test_show_service_invalid_response(mock_get_api_client):
    """Test that show_service handles invalid API response correctly."""
    service_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'service' key

    with pytest.raises(RuntimeError) as exc_info:
        services.show_service(service_id=service_id)
    assert (
        str(exc_info.value)
        == "Failed to fetch service 123: Response missing 'service' field"
    )


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.services
def test_parse_service(mock_services, mock_services_parsed):
    """Test that parse_service correctly parses raw service data."""
    parsed_service = parse_service(result=mock_services[0])
    assert parsed_service == mock_services_parsed[0]


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.services
def test_parse_service_none():
    """Test that parse_service handles None input correctly."""
    assert parse_service(result=None) == {}


@pytest.mark.unit
@pytest.mark.services
def test_list_services_preserves_full_error_message(mock_get_api_client):
    """Test that list_services preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.list_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        services.list_services()
    assert str(exc_info.value) == "API Error"

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

    expected_metadata = incidents._calculate_incident_metadata(mock_incidents)
    parsed_incidents = [parse_incident(result=incident) for incident in mock_incidents]

    expected_response = utils.api_response_handler(
        results=parsed_incidents,
        resource_name='incidents',
        additional_metadata=expected_metadata
    )
    assert incidents_list == expected_response

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.incidents
def test_parse_incident(mock_incidents, mock_incidents_parsed):
    """Test that incident parsing works correctly."""
    parsed_incident = parse_incident(result=mock_incidents[0])
    assert parsed_incident == mock_incidents_parsed[0]

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_empty():
    """Test metadata calculation with an empty list of incidents."""
    metadata = incidents._calculate_incident_metadata([])
    assert metadata == {
        'status_counts': {
            'triggered': 0,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_single_incident():
    """Test metadata calculation with a single incident."""
    incident = {
        'id': '123',
        'status': 'triggered',
        'urgency': 'high',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }
    metadata = incidents._calculate_incident_metadata([incident])
    assert metadata == {
        'status_counts': {
            'triggered': 1,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_multiple_incidents():
    """Test metadata calculation with multiple incidents of different statuses."""
    incident_list = [
        {
            'id': '123',
            'status': 'triggered',
            'urgency': 'high',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'id': '456',
            'status': 'acknowledged',
            'urgency': 'high',
            'created_at': '2024-01-01T01:00:00Z',
            'updated_at': '2024-01-01T01:00:00Z'
        },
        {
            'id': '789',
            'status': 'resolved',
            'urgency': 'low',
            'created_at': '2024-01-01T02:00:00Z',
            'updated_at': '2024-01-01T02:00:00Z'
        }
    ]
    metadata = incidents._calculate_incident_metadata(incident_list)
    assert metadata == {
        'status_counts': {
            'triggered': 1,
            'acknowledged': 1,
            'resolved': 1
        },
        'autoresolve_count': 0,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_duplicate_statuses():
    """Test metadata calculation with multiple incidents of the same status."""
    incident_list = [
        {
            'id': '123',
            'status': 'triggered',
            'urgency': 'high',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'id': '456',
            'status': 'triggered',
            'urgency': 'low',
            'created_at': '2024-01-01T01:00:00Z',
            'updated_at': '2024-01-01T01:00:00Z'
        }
    ]
    metadata = incidents._calculate_incident_metadata(incident_list)
    assert metadata == {
        'status_counts': {
            'triggered': 2,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_invalid_status():
    """Test metadata calculation with an incident having an invalid status."""
    incident = {
        'id': '123',
        'status': 'invalid_status',
        'urgency': 'high',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }
    metadata = incidents._calculate_incident_metadata([incident])
    assert metadata == {
        'status_counts': {
            'triggered': 0,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_autoresolve():
    """Test metadata calculation includes autoresolve count."""
    auto_resolved = {
        'id': '123',
        'status': 'resolved',
        'urgency': 'high',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T01:00:00Z',
        'last_status_change_by': {
            'type': incidents.AUTORESOLVE_TYPE,
            'id': 'service-1'
        }
    }

    manual_resolved = {
        'id': '456',
        'status': 'resolved',
        'urgency': 'high',
        'created_at': '2024-01-01T02:00:00Z',
        'updated_at': '2024-01-01T03:00:00Z',
        'last_status_change_by': {
            'type': 'user_reference',
            'id': 'user-1'
        }
    }

    missing_status_change = {
        'id': '789',
        'status': 'resolved',
        'urgency': 'high',
        'created_at': '2024-01-01T04:00:00Z',
        'updated_at': '2024-01-01T05:00:00Z'
    }

    triggered = {
        'id': '101',
        'status': 'triggered',
        'urgency': 'low',
        'created_at': '2024-01-01T06:00:00Z',
        'updated_at': '2024-01-01T06:00:00Z',
        'last_status_change_by': {
            'type': 'user_reference',
            'id': 'user-2'
        }
    }

    incident_list = [auto_resolved, manual_resolved, missing_status_change, triggered]
    metadata = incidents._calculate_incident_metadata(incident_list)

    assert metadata == {
        'status_counts': {
            'triggered': 1,
            'acknowledged': 0,
            'resolved': 3
        },
        'autoresolve_count': 1,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_no_data():
    """Test metadata calculation includes no data count."""
    no_data_incident = {
        'id': '123',
        'status': 'triggered',
        'urgency': 'high',
        'title': 'No Data: Test Incident',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }

    regular_incident = {
        'id': '456',
        'status': 'triggered',
        'urgency': 'high',
        'title': 'Regular Incident',
        'created_at': '2024-01-01T01:00:00Z',
        'updated_at': '2024-01-01T01:00:00Z'
    }

    incident_list = [no_data_incident, regular_incident]
    metadata = incidents._calculate_incident_metadata(incident_list)

    assert metadata == {
        'status_counts': {
            'triggered': 2,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 1
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents_status_filter(mock_get_api_client):
    """Test that incidents can be filtered by status."""
    test_incidents = [
        {
            'id': '123',
            'status': 'triggered',
            'urgency': 'high',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z'
        },
        {
            'id': '456',
            'status': 'acknowledged',
            'urgency': 'high',
            'created_at': '2024-01-01T01:00:00Z',
            'updated_at': '2024-01-01T01:00:00Z'
        }
    ]

    mock_get_api_client.list_all.return_value = test_incidents
    statuses = ['triggered', 'acknowledged']
    params = {'statuses': statuses, 'urgencies': incidents.DEFAULT_URGENCIES}

    incidents_list = incidents.list_incidents(statuses=statuses)

    mock_get_api_client.list_all.assert_called_once_with(incidents.INCIDENTS_URL, params=params)

    expected_metadata = incidents._calculate_incident_metadata(test_incidents)
    parsed_incidents = [parse_incident(result=incident) for incident in test_incidents]

    expected_response = utils.api_response_handler(
        results=parsed_incidents,
        resource_name='incidents',
        additional_metadata=expected_metadata
    )
    assert incidents_list == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents_invalid_status(mock_get_api_client):
    """Test that invalid status values raise a ValueError."""
    invalid_statuses = ['invalid_status']

    with pytest.raises(ValueError) as exc_info:
        incidents.list_incidents(statuses=invalid_statuses)

    assert "Invalid status values" in str(exc_info.value)
    assert "Valid values are" in str(exc_info.value)
    assert all(status in str(exc_info.value) for status in incidents.VALID_STATUSES)

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_no_data_count():
    """Test metadata calculation includes no_data_count for incidents with titles starting with 'No Data:'."""
    no_data_incident = {
        'id': '123',
        'status': 'triggered',
        'urgency': 'high',
        'title': 'No Data: Test Incident',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z'
    }

    regular_incident = {
        'id': '456',
        'status': 'triggered',
        'urgency': 'high',
        'title': 'Regular Incident',
        'created_at': '2024-01-01T01:00:00Z',
        'updated_at': '2024-01-01T01:00:00Z'
    }

    incident_list = [no_data_incident, regular_incident]
    metadata = incidents._calculate_incident_metadata(incident_list)

    assert metadata == {
        'status_counts': {
            'triggered': 2,
            'acknowledged': 0,
            'resolved': 0
        },
        'autoresolve_count': 0,
        'no_data_count': 1
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident(mock_get_api_client, mock_incidents):
    """Test that a single incident is fetched correctly."""
    incident_id = '123'
    mock_incident = mock_incidents[0]
    mock_get_api_client.jget.return_value = {'incident': mock_incident}

    incident = incidents.show_incident(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(f"{incidents.INCIDENTS_URL}/{incident_id}")

    expected_response = utils.api_response_handler(
        results=parse_incident(result=mock_incident),
        resource_name='incident'
    )
    assert incident == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident_invalid_id(mock_get_api_client):
    """Test that show_incident raises ValueError for invalid incident ID."""
    with pytest.raises(ValueError) as exc_info:
        incidents.show_incident(incident_id='')
    assert str(exc_info.value) == "incident_id cannot be empty"

@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident_api_error(mock_get_api_client):
    """Test that show_incident handles API errors correctly."""
    incident_id = '123'
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        incidents.show_incident(incident_id=incident_id)
    assert str(exc_info.value) == f"Failed to fetch or process incident {incident_id}: API Error"

@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident_invalid_response(mock_get_api_client):
    """Test that show_incident handles invalid API response correctly."""
    incident_id = '123'
    mock_get_api_client.jget.return_value = {}  # Missing 'incident' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents.show_incident(incident_id=incident_id)
    assert str(exc_info.value) == f"Failed to fetch or process incident {incident_id}: 'incident'"

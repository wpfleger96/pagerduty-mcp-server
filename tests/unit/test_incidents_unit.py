"""Unit tests for the incidents module."""

import pytest
from unittest.mock import MagicMock

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
    assert str(exc_info.value) == "API Error"

@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident_invalid_response(mock_get_api_client):
    """Test that show_incident handles invalid API response correctly."""
    incident_id = '123'
    mock_get_api_client.jget.return_value = {}  # Missing 'incident' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents.show_incident(incident_id=incident_id)
    assert str(exc_info.value) == f"Failed to fetch or process incident {incident_id}: 'incident'"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents(mock_get_api_client):
    """Test that past incidents are fetched correctly."""
    incident_id = '123'
    mock_past_incidents = [
        {
            'incident': {
                'id': 'Q1QKZKKE2FC88M',
                'created_at': '2025-02-08T19:34:42Z',
                'self': 'https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M',
                'title': 'Test Incident 1'
            },
            'score': 190.21751
        },
        {
            'incident': {
                'id': 'Q2O8AO7WALN4N5',
                'created_at': '2025-03-25T20:34:59Z',
                'self': 'https://api.pagerduty.com/incidents/Q2O8AO7WALN4N5',
                'title': 'Test Incident 2'
            },
            'score': 187.90202
        }
    ]
    mock_get_api_client.jget.return_value = {'past_incidents': mock_past_incidents}

    past_incidents = incidents.list_past_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/past_incidents",
        params={'limit': None, 'total': None}
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                **parse_incident(result=item['incident']),
                'similarity_score': item['score']
            }
            for item in mock_past_incidents
        ],
        resource_name='incidents'
    )
    assert past_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_with_params(mock_get_api_client):
    """Test that past incidents can be fetched with limit and total parameters."""
    incident_id = '123'
    mock_past_incidents = [
        {
            'incident': {
                'id': 'Q1QKZKKE2FC88M',
                'created_at': '2025-02-08T19:34:42Z',
                'self': 'https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M',
                'title': 'Test Incident 1'
            },
            'score': 190.21751
        }
    ]
    mock_get_api_client.jget.return_value = {'past_incidents': mock_past_incidents}

    past_incidents = incidents.list_past_incidents(
        incident_id=incident_id,
        limit=1,
        total=True
    )

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/past_incidents",
        params={'limit': 1, 'total': True}
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                **parse_incident(result=item['incident']),
                'similarity_score': item['score']
            }
            for item in mock_past_incidents
        ],
        resource_name='incidents'
    )
    assert past_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_invalid_id(mock_get_api_client):
    """Test that list_past_incidents raises ValueError for invalid incident ID."""
    with pytest.raises(ValueError) as exc_info:
        incidents.list_past_incidents(incident_id='')
    assert str(exc_info.value) == "incident_id cannot be empty"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_api_error(mock_get_api_client):
    """Test that list_past_incidents handles API errors correctly."""
    incident_id = '123'
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        incidents.list_past_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_invalid_response(mock_get_api_client):
    """Test that list_past_incidents handles invalid API response correctly."""
    incident_id = '123'
    mock_get_api_client.jget.return_value = {}  # Missing 'past_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents.list_past_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "Failed to fetch past incidents for 123: Response missing 'past_incidents' field"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents(mock_get_api_client):
    """Test that related incidents are fetched correctly."""
    incident_id = '123'
    mock_related_incidents = [
        {
            'incident': {
                'id': 'Q1QKZKKE2FC88M',
                'created_at': '2025-02-08T19:34:42Z',
                'self': 'https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M',
                'title': 'Test Incident 1'
            },
            'relationships': [{
                'type': 'machine_learning_inferred',
                'metadata': {
                    'grouping_classification': 'prior_feedback',
                    'user_feedback': {
                        'negative_feedback_count': 0,
                        'positive_feedback_count': 0
                    }
                }
            }]
        },
        {
            'incident': {
                'id': 'Q2O8AO7WALN4N5',
                'created_at': '2025-03-25T20:34:59Z',
                'self': 'https://api.pagerduty.com/incidents/Q2O8AO7WALN4N5',
                'title': 'Test Incident 2'
            },
            'relationships': [{
                'type': 'machine_learning_inferred',
                'metadata': {
                    'grouping_classification': 'prior_feedback',
                    'user_feedback': {
                        'negative_feedback_count': 1,
                        'positive_feedback_count': 2
                    }
                }
            }]
        }
    ]
    mock_get_api_client.jget.return_value = {'related_incidents': mock_related_incidents}

    related_incidents = incidents.list_related_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/related_incidents"
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                **parse_incident(result=item['incident']),
                'relationship_type': item['relationships'][0]['type'],
                'relationship_metadata': item['relationships'][0]['metadata']
            }
            for item in mock_related_incidents
        ],
        resource_name='incidents'
    )
    assert related_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_invalid_id(mock_get_api_client):
    """Test that list_related_incidents raises ValueError for invalid incident ID."""
    with pytest.raises(ValueError) as exc_info:
        incidents.list_related_incidents(incident_id='')
    assert str(exc_info.value) == "incident_id cannot be empty"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_api_error(mock_get_api_client):
    """Test that list_related_incidents handles API errors correctly."""
    incident_id = '123'
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        incidents.list_related_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_invalid_response(mock_get_api_client):
    """Test that list_related_incidents handles invalid API response correctly."""
    incident_id = '123'
    mock_get_api_client.jget.return_value = {}  # Missing 'related_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents.list_related_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "Failed to fetch related incidents for 123: Response missing 'related_incidents' field"

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_empty_list(mock_get_api_client):
    """Test that list_related_incidents handles empty list response correctly."""
    incident_id = '123'
    mock_get_api_client.jget.return_value = {'related_incidents': []}

    related_incidents = incidents.list_related_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/related_incidents"
    )

    expected_response = utils.api_response_handler(
        results=[],
        resource_name='incidents'
    )
    assert related_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_missing_relationships(mock_get_api_client):
    """Test that list_related_incidents handles incidents with missing relationships correctly."""
    incident_id = '123'
    mock_related_incidents = [
        {
            'incident': {
                'id': 'Q1QKZKKE2FC88M',
                'created_at': '2025-02-08T19:34:42Z',
                'self': 'https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M',
                'title': 'Test Incident 1'
            },
            'relationships': []
        }
    ]
    mock_get_api_client.jget.return_value = {'related_incidents': mock_related_incidents}

    related_incidents = incidents.list_related_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/related_incidents"
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                **parse_incident(result=item['incident']),
                'relationship_type': None,
                'relationship_metadata': None
            }
            for item in mock_related_incidents
        ],
        resource_name='incidents'
    )
    assert related_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_missing_fields(mock_get_api_client):
    """Test that list_past_incidents handles missing fields in response items correctly."""
    incident_id = '123'
    mock_past_incidents = [
        {
            'incident': {
                'id': 'Q1QKZKKE2FC88M',
                'created_at': '2025-02-08T19:34:42Z',
                'self': 'https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M',
                'title': 'Test Incident 1'
            }
            # Missing 'score' field
        },
        {
            # Missing 'incident' field
            'score': 187.90202
        }
    ]
    mock_get_api_client.jget.return_value = {'past_incidents': mock_past_incidents}

    past_incidents = incidents.list_past_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/past_incidents",
        params={'limit': None, 'total': None}
    )

    expected_incidents = [
        {
            **parse_incident(result=mock_past_incidents[1].get('incident', {})),
            'similarity_score': mock_past_incidents[1].get('score', 0.0)
        },
        {
            **parse_incident(result=mock_past_incidents[0].get('incident', {})),
            'similarity_score': mock_past_incidents[0].get('score', 0.0)
        }
    ]

    expected_response = utils.api_response_handler(
        results=expected_incidents,
        resource_name='incidents'
    )
    assert past_incidents == expected_response

@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_autoresolve_edge_cases():
    """Test metadata calculation includes autoresolve count with edge cases."""
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

    missing_type = {
        'id': '101',
        'status': 'resolved',
        'urgency': 'high',
        'created_at': '2024-01-01T06:00:00Z',
        'updated_at': '2024-01-01T07:00:00Z',
        'last_status_change_by': {
            'id': 'service-2'
        }
    }

    triggered = {
        'id': '102',
        'status': 'triggered',
        'urgency': 'low',
        'created_at': '2024-01-01T08:00:00Z',
        'updated_at': '2024-01-01T08:00:00Z',
        'last_status_change_by': {
            'type': 'user_reference',
            'id': 'user-2'
        }
    }

    incident_list = [auto_resolved, manual_resolved, missing_status_change, missing_type, triggered]
    metadata = incidents._calculate_incident_metadata(incident_list)

    assert metadata == {
        'status_counts': {
            'triggered': 1,
            'acknowledged': 0,
            'resolved': 4
        },
        'autoresolve_count': 1,
        'no_data_count': 0
    }

@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents_preserves_full_error_message(mock_get_api_client):
    """Test that list_incidents preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.list_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        incidents.list_incidents()
    assert str(exc_info.value) == "API Error"

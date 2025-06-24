"""Unit tests for the incidents module."""

from unittest.mock import patch

import pytest

from pagerduty_mcp_server import incidents, utils
from pagerduty_mcp_server.parsers import parse_incident


@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents(mock_get_api_client, mock_incidents):
    """Test that incidents are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_incidents
    params = {
        "statuses": incidents.DEFAULT_STATUSES,
        "urgencies": incidents.DEFAULT_URGENCIES,
    }

    incidents_list = incidents.list_incidents()

    mock_get_api_client.jget.assert_not_called()
    mock_get_api_client.list_all.assert_called_once_with(
        incidents.INCIDENTS_URL, params=params
    )

    expected_metadata = incidents._calculate_incident_metadata(mock_incidents)
    parsed_incidents = [parse_incident(result=incident) for incident in mock_incidents]

    expected_response = utils.api_response_handler(
        results=parsed_incidents,
        resource_name="incidents",
        additional_metadata=expected_metadata,
    )
    assert incidents_list == expected_response


@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "case",
    [
        {
            "name": "status_filter",
            "params": {"statuses": ["triggered", "acknowledged"]},
            "expected_params": {
                "statuses": ["triggered", "acknowledged"],
                "urgencies": incidents.DEFAULT_URGENCIES,
            },
        },
        {
            "name": "service_ids_filter",
            "params": {"service_ids": ["SERVICE-1", "SERVICE-2"]},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "service_ids": ["SERVICE-1", "SERVICE-2"],
            },
        },
        {
            "name": "team_ids_filter",
            "params": {"team_ids": ["TEAM-1", "TEAM-2"]},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "team_ids": ["TEAM-1", "TEAM-2"],
            },
        },
        {
            "name": "date_range_filter",
            "params": {
                "since": "2024-01-01T00:00:00Z",
                "until": "2024-01-31T23:59:59Z",
            },
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "since": "2024-01-01T00:00:00Z",
                "until": "2024-01-31T23:59:59Z",
            },
        },
        {
            "name": "limit_filter",
            "params": {"limit": 10},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "limit": 10,
            },
        },
    ],
)
def test_list_incidents_with_filters(mock_get_api_client, case):
    """Test that incidents can be filtered by various parameters."""
    test_incidents = [
        {
            "id": "123",
            "status": "triggered",
            "urgency": "high",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
    ]
    mock_get_api_client.list_all.return_value = test_incidents

    incidents.list_incidents(**case["params"])

    mock_get_api_client.list_all.assert_called_once_with(
        incidents.INCIDENTS_URL, params=case["expected_params"]
    )


@pytest.mark.unit
@pytest.mark.incidents
def test_list_incidents_invalid_status(mock_get_api_client):
    """Test that invalid status values raise a ValueError."""
    invalid_statuses = ["invalid_status"]

    with pytest.raises(ValueError) as exc_info:
        incidents.list_incidents(statuses=invalid_statuses)

    assert "Invalid status values" in str(exc_info.value)
    assert "Valid values are" in str(exc_info.value)
    assert all(status in str(exc_info.value) for status in incidents.VALID_STATUSES)


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.incidents
def test_parse_incident(mock_incidents, mock_incidents_parsed):
    """Test that incident parsing works correctly."""
    parsed_incident = parse_incident(result=mock_incidents[0])
    assert parsed_incident == mock_incidents_parsed[0]


@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "empty_list",
            "incidents": [],
            "expected": {
                "status_counts": {"triggered": 0, "acknowledged": 0, "resolved": 0},
                "autoresolve_count": 0,
                "no_data_count": 0,
            },
        },
        {
            "name": "single_incident",
            "incidents": [
                {
                    "id": "123",
                    "status": "triggered",
                    "urgency": "high",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ],
            "expected": {
                "status_counts": {"triggered": 1, "acknowledged": 0, "resolved": 0},
                "autoresolve_count": 0,
                "no_data_count": 0,
            },
        },
        {
            "name": "multiple_incidents",
            "incidents": [
                {
                    "id": "123",
                    "status": "triggered",
                    "urgency": "high",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                {
                    "id": "456",
                    "status": "acknowledged",
                    "urgency": "high",
                    "created_at": "2024-01-01T01:00:00Z",
                    "updated_at": "2024-01-01T01:00:00Z",
                },
                {
                    "id": "789",
                    "status": "resolved",
                    "urgency": "low",
                    "created_at": "2024-01-01T02:00:00Z",
                    "updated_at": "2024-01-01T02:00:00Z",
                },
            ],
            "expected": {
                "status_counts": {"triggered": 1, "acknowledged": 1, "resolved": 1},
                "autoresolve_count": 0,
                "no_data_count": 0,
            },
        },
        {
            "name": "duplicate_statuses",
            "incidents": [
                {
                    "id": "123",
                    "status": "triggered",
                    "urgency": "high",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                {
                    "id": "456",
                    "status": "triggered",
                    "urgency": "low",
                    "created_at": "2024-01-01T01:00:00Z",
                    "updated_at": "2024-01-01T01:00:00Z",
                },
            ],
            "expected": {
                "status_counts": {"triggered": 2, "acknowledged": 0, "resolved": 0},
                "autoresolve_count": 0,
                "no_data_count": 0,
            },
        },
        {
            "name": "invalid_status",
            "incidents": [
                {
                    "id": "123",
                    "status": "invalid_status",
                    "urgency": "high",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ],
            "expected": {
                "status_counts": {"triggered": 0, "acknowledged": 0, "resolved": 0},
                "autoresolve_count": 0,
                "no_data_count": 0,
            },
        },
    ],
)
def test_calculate_incident_metadata_basic(test_case):
    """Test metadata calculation with various incident lists."""
    metadata = incidents._calculate_incident_metadata(test_case["incidents"])
    assert metadata == test_case["expected"]


@pytest.mark.unit
@pytest.mark.incidents
def test_calculate_incident_metadata_special_cases():
    """Test metadata calculation for special cases (autoresolve and no_data)."""
    # Test autoresolve count
    auto_resolved = {
        "id": "123",
        "status": "resolved",
        "urgency": "high",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T01:00:00Z",
        "last_status_change_by": {
            "type": incidents.AUTORESOLVE_TYPE,
            "id": "service-1",
        },
    }

    manual_resolved = {
        "id": "456",
        "status": "resolved",
        "urgency": "high",
        "created_at": "2024-01-01T02:00:00Z",
        "updated_at": "2024-01-01T03:00:00Z",
        "last_status_change_by": {"type": "user_reference", "id": "user-1"},
    }

    # Test no_data count
    no_data_incident = {
        "id": "789",
        "status": "triggered",
        "urgency": "high",
        "title": "No Data: Test Incident",
        "created_at": "2024-01-01T04:00:00Z",
        "updated_at": "2024-01-01T05:00:00Z",
    }

    regular_incident = {
        "id": "101",
        "status": "triggered",
        "urgency": "low",
        "title": "Regular Incident",
        "created_at": "2024-01-01T06:00:00Z",
        "updated_at": "2024-01-01T06:00:00Z",
    }

    incident_list = [auto_resolved, manual_resolved, no_data_incident, regular_incident]
    metadata = incidents._calculate_incident_metadata(incident_list)

    assert metadata == {
        "status_counts": {"triggered": 2, "acknowledged": 0, "resolved": 2},
        "autoresolve_count": 1,
        "no_data_count": 1,
    }


@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "test_case",
    [
        {"name": "basic", "flags": {}, "expected_calls": []},
        {
            "name": "with_past_incidents",
            "flags": {"include_past_incidents": True},
            "expected_calls": ["_list_past_incidents"],
        },
        {
            "name": "with_related_incidents",
            "flags": {"include_related_incidents": True},
            "expected_calls": ["_list_related_incidents"],
        },
        {
            "name": "with_notes",
            "flags": {"include_notes": True},
            "expected_calls": ["_list_notes"],
        },
        {
            "name": "with_all_flags",
            "flags": {
                "include_past_incidents": True,
                "include_related_incidents": True,
                "include_notes": True,
            },
            "expected_calls": [
                "_list_past_incidents",
                "_list_related_incidents",
                "_list_notes",
            ],
        },
    ],
)
def test_show_incident(mock_get_api_client, mock_incidents, test_case):
    """Test that a single incident is fetched correctly with various flag combinations."""
    incident_id = "123"
    mock_incident = mock_incidents[0]
    mock_get_api_client.jget.return_value = {"incident": mock_incident}

    # Mock responses for the various enrichment functions
    mock_past_incidents = {
        "incidents": [
            {"id": "PAST-1", "summary": "Past Incident 1", "similarity_score": 90.5}
        ]
    }

    mock_related_incidents = {
        "incidents": [
            {
                "id": "RELATED-1",
                "summary": "Related Incident 1",
                "relationship_type": "machine_learning_inferred",
            }
        ]
    }

    mock_notes = {
        "notes": [
            {
                "id": "NOTE-1",
                "content": "Test note",
                "created_at": "2024-01-01T00:00:00Z",
                "user": {"id": "USER-1", "name": "Test User", "type": "user_reference"},
                "channel": {"summary": "The PagerDuty website or APIs", "type": "web"},
            }
        ]
    }

    # Set up patches for all the enrichment functions
    with (
        patch("pagerduty_mcp_server.incidents._list_past_incidents") as mock_list_past,
        patch(
            "pagerduty_mcp_server.incidents._list_related_incidents"
        ) as mock_list_related,
        patch("pagerduty_mcp_server.incidents._list_notes") as mock_list_notes,
    ):
        mock_list_past.return_value = mock_past_incidents
        mock_list_related.return_value = mock_related_incidents
        mock_list_notes.return_value = mock_notes

        # Call show_incident with the test case flags
        incident = incidents.show_incident(
            incident_id=incident_id, **test_case["flags"]
        )

        # Verify the main API call was made
        mock_get_api_client.jget.assert_called_once_with(
            f"{incidents.INCIDENTS_URL}/{incident_id}", params={"include[]": "body"}
        )

        # Verify the expected enrichment functions were called
        if "_list_past_incidents" in test_case["expected_calls"]:
            mock_list_past.assert_called_once_with(incident_id=incident_id)
        else:
            mock_list_past.assert_not_called()

        if "_list_related_incidents" in test_case["expected_calls"]:
            mock_list_related.assert_called_once_with(incident_id=incident_id)
        else:
            mock_list_related.assert_not_called()

        if "_list_notes" in test_case["expected_calls"]:
            mock_list_notes.assert_called_once_with(incident_id=incident_id)
        else:
            mock_list_notes.assert_not_called()

        parsed_main_incident = parse_incident(result=mock_incident)
        expected_metadata = {}

        if test_case["flags"].get("include_past_incidents"):
            parsed_main_incident["past_incidents"] = mock_past_incidents["incidents"]
            expected_metadata["past_incidents_count"] = len(
                mock_past_incidents["incidents"]
            )

        if test_case["flags"].get("include_related_incidents"):
            parsed_main_incident["related_incidents"] = mock_related_incidents[
                "incidents"
            ]
            expected_metadata["related_incidents_count"] = len(
                mock_related_incidents["incidents"]
            )

        if test_case["flags"].get("include_notes"):
            parsed_main_incident["notes"] = mock_notes["notes"]
            expected_metadata["notes_count"] = len(mock_notes["notes"])

        expected_response = utils.api_response_handler(
            results=parsed_main_incident,
            resource_name="incident",
            additional_metadata=expected_metadata,
        )
        assert incident == expected_response


@pytest.mark.unit
@pytest.mark.incidents
def test_show_incident_error_handling(mock_get_api_client, mock_incidents, caplog):
    """Test error handling in show_incident for various scenarios."""
    incident_id = "123"

    # Test case 1: Empty incident_id
    with pytest.raises(ValueError) as exc_info:
        incidents.show_incident(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"

    # Test case 2: API error
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")
    with pytest.raises(RuntimeError) as exc_info:
        incidents.show_incident(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"

    # Test case 3: Invalid API response
    mock_get_api_client.jget.side_effect = None
    mock_get_api_client.jget.return_value = {}  # Missing 'incident' key
    with pytest.raises(RuntimeError) as exc_info:
        incidents.show_incident(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch or process incident {incident_id}: 'incident'"
    )


@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "params, expected_api_params, mock_response_slice",
    [
        ({}, {"limit": None, "total": None}, slice(None)),  # Basic call, full response
        (
            {"limit": 1, "total": True},
            {"limit": 1, "total": True},
            slice(0, 1),
        ),  # With limit and total, first item only
    ],
)
def test_list_past_incidents_success(
    mock_get_api_client, params, expected_api_params, mock_response_slice
):
    """Test that past incidents are fetched correctly with various parameters."""
    incident_id = "123"
    mock_past_incidents = [
        {
            "incident": {
                "id": "Q1QKZKKE2FC88M",
                "created_at": "2025-02-08T19:34:42Z",
                "self": "https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M",
                "title": "Test Incident 1",
            },
            "score": 190.21751,
        },
        {
            "incident": {
                "id": "Q2O8AO7WALN4N5",
                "created_at": "2025-03-25T20:34:59Z",
                "self": "https://api.pagerduty.com/incidents/Q2O8AO7WALN4N5",
                "title": "Test Incident 2",
            },
            "score": 187.90202,
        },
    ]

    # Set up the mock response based on the slice parameter
    mock_get_api_client.jget.return_value = {
        "past_incidents": mock_past_incidents[mock_response_slice]
    }

    past_incidents = incidents._list_past_incidents(incident_id=incident_id, **params)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/past_incidents",
        params=expected_api_params,
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                **parse_incident(result=item["incident"]),
                "similarity_score": item["score"],
            }
            for item in mock_past_incidents[mock_response_slice]
        ],
        resource_name="incidents",
    )
    assert past_incidents == expected_response


@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_error_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        incidents._list_past_incidents(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"


@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_error_api(mock_get_api_client):
    """Test that API errors are properly propagated."""
    incident_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        incidents._list_past_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.incidents
def test_list_past_incidents_error_invalid_response(mock_get_api_client):
    """Test that invalid API responses are properly handled."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'past_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents._list_past_incidents(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch past incidents for {incident_id}: Response missing 'past_incidents' field"
    )


@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "test_case",
    [
        {
            "name": "with_relationships",
            "mock_data": [
                {
                    "incident": {
                        "id": "Q1QKZKKE2FC88M",
                        "created_at": "2025-02-08T19:34:42Z",
                        "self": "https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M",
                        "title": "Test Incident 1",
                    },
                    "relationships": [
                        {
                            "type": "machine_learning_inferred",
                            "metadata": {
                                "grouping_classification": "prior_feedback",
                                "user_feedback": {
                                    "negative_feedback_count": 0,
                                    "positive_feedback_count": 0,
                                },
                            },
                        }
                    ],
                },
                {
                    "incident": {
                        "id": "Q2O8AO7WALN4N5",
                        "created_at": "2025-03-25T20:34:59Z",
                        "self": "https://api.pagerduty.com/incidents/Q2O8AO7WALN4N5",
                        "title": "Test Incident 2",
                    },
                    "relationships": [
                        {
                            "type": "machine_learning_inferred",
                            "metadata": {
                                "grouping_classification": "prior_feedback",
                                "user_feedback": {
                                    "negative_feedback_count": 1,
                                    "positive_feedback_count": 2,
                                },
                            },
                        }
                    ],
                },
            ],
            "expected_transform": lambda item: {
                **parse_incident(result=item["incident"]),
                "relationship_type": item["relationships"][0]["type"],
                "relationship_metadata": item["relationships"][0]["metadata"],
            },
        },
        {
            "name": "empty_relationships",
            "mock_data": [
                {
                    "incident": {
                        "id": "Q1QKZKKE2FC88M",
                        "created_at": "2025-02-08T19:34:42Z",
                        "self": "https://api.pagerduty.com/incidents/Q1QKZKKE2FC88M",
                        "title": "Test Incident 1",
                    },
                    "relationships": [],
                }
            ],
            "expected_transform": lambda item: {
                **parse_incident(result=item["incident"]),
                "relationship_type": None,
                "relationship_metadata": None,
            },
        },
    ],
)
def test_list_related_incidents_success(mock_get_api_client, test_case):
    """Test that related incidents are fetched correctly with various relationship structures."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {
        "related_incidents": test_case["mock_data"]
    }

    related_incidents = incidents._list_related_incidents(incident_id=incident_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/related_incidents"
    )

    expected_response = utils.api_response_handler(
        results=[
            test_case["expected_transform"](item) for item in test_case["mock_data"]
        ],
        resource_name="incidents",
    )
    assert related_incidents == expected_response


@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_error_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        incidents._list_related_incidents(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"


@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_error_api(mock_get_api_client):
    """Test that API errors are properly propagated."""
    incident_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        incidents._list_related_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.incidents
def test_list_related_incidents_error_invalid_response(mock_get_api_client):
    """Test that invalid API responses are properly handled."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'related_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        incidents._list_related_incidents(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch related incidents for {incident_id}: Response missing 'related_incidents' field"
    )

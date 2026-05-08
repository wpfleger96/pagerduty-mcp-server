"""Unit tests for the incidents module."""

from unittest.mock import AsyncMock, patch

import pytest

from pagerduty_mcp_server import incidents, utils

MOCK_USER_EMAIL = "test@example.com"


@pytest.fixture
def mock_user_email_patch():
    """Mock _get_current_user_email for write operation tests."""
    with patch(
        "pagerduty_mcp_server.incidents._get_current_user_email",
        new_callable=AsyncMock,
        return_value=MOCK_USER_EMAIL,
    ) as mock:
        yield mock


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents(
    mock_get_api_client, mock_incidents, mock_incidents_parsed
):
    """Test that incidents are fetched correctly."""
    mock_get_api_client.iter_all.return_value = mock_incidents

    incident_list = await incidents.list_incidents()

    mock_get_api_client.iter_all.assert_called_once_with(
        incidents.INCIDENTS_URL,
        params={
            "statuses": incidents.DEFAULT_STATUSES,
            "urgencies": incidents.DEFAULT_URGENCIES,
        },
        page_size=100,
    )
    expected_metadata = incidents._calculate_incident_metadata(mock_incidents)
    assert incident_list == utils.api_response_handler(
        results=mock_incidents_parsed,
        resource_name="incidents",
        additional_metadata=expected_metadata,
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_with_status(
    mock_get_api_client, mock_incidents, mock_incidents_parsed
):
    """Test that incidents can be filtered by status."""
    status = "triggered"
    mock_get_api_client.iter_all.return_value = mock_incidents

    incident_list = await incidents.list_incidents(statuses=[status])

    mock_get_api_client.iter_all.assert_called_once_with(
        incidents.INCIDENTS_URL,
        params={"statuses": [status], "urgencies": incidents.DEFAULT_URGENCIES},
        page_size=100,
    )
    assert incident_list["incidents"] == mock_incidents_parsed
    assert "metadata" in incident_list
    assert "count" in incident_list["metadata"]


@pytest.mark.asyncio
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
            "expected_page_size": 100,
        },
        {
            "name": "service_ids_filter",
            "params": {"service_ids": ["SERVICE-1", "SERVICE-2"]},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "service_ids": ["SERVICE-1", "SERVICE-2"],
            },
            "expected_page_size": 100,
        },
        {
            "name": "team_ids_filter",
            "params": {"team_ids": ["TEAM-1", "TEAM-2"]},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
                "team_ids": ["TEAM-1", "TEAM-2"],
            },
            "expected_page_size": 100,
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
            "expected_page_size": 100,
        },
        {
            # `limit` is enforced via paginate()'s max_records cap, NOT passed
            # as a query parameter (the SDK would treat it as page_size).
            "name": "limit_filter",
            "params": {"limit": 10},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": incidents.DEFAULT_URGENCIES,
            },
            "expected_page_size": 10,
        },
        {
            "name": "urgencies_filter",
            "params": {"urgencies": ["high"]},
            "expected_params": {
                "statuses": incidents.DEFAULT_STATUSES,
                "urgencies": ["high"],
            },
            "expected_page_size": 100,
        },
    ],
)
async def test_list_incidents_with_filters(mock_get_api_client, case):
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
    mock_get_api_client.iter_all.return_value = test_incidents

    await incidents.list_incidents(**case["params"])

    mock_get_api_client.iter_all.assert_called_once_with(
        incidents.INCIDENTS_URL,
        params=case["expected_params"],
        page_size=case["expected_page_size"],
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_invalid_status(mock_get_api_client):
    """Test that invalid status values raise a ValueError."""
    invalid_statuses = ["invalid_status"]

    with pytest.raises(ValueError) as exc_info:
        await incidents.list_incidents(statuses=invalid_statuses)

    assert "Invalid status values" in str(exc_info.value)
    assert "Valid values are" in str(exc_info.value)
    assert all(status in str(exc_info.value) for status in incidents.VALID_STATUSES)


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_invalid_urgency(mock_get_api_client):
    """Test that invalid urgency values raise a ValueError."""
    with pytest.raises(ValueError) as exc_info:
        await incidents.list_incidents(urgencies=["invalid_urgency"])

    assert "Invalid urgency values" in str(exc_info.value)
    assert "Valid values are" in str(exc_info.value)


@pytest.mark.asyncio
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
async def test_calculate_incident_metadata_basic(test_case):
    """Test metadata calculation with various incident lists."""
    metadata = incidents._calculate_incident_metadata(test_case["incidents"])
    assert metadata == test_case["expected"]


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_calculate_incident_metadata_special_cases():
    """Test metadata calculation for special cases (autoresolve and no_data)."""
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


@pytest.mark.asyncio
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
async def test_show_incident(
    mock_get_api_client, mock_incidents, mock_incidents_parsed, test_case
):
    """Test that a single incident is fetched correctly with various flag combinations."""
    incident_id = mock_incidents[0]["id"]
    mock_get_api_client.jget.return_value = {"incident": mock_incidents[0]}

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

        incident = await incidents.show_incident(
            incident_id=incident_id, **test_case["flags"]
        )

        mock_get_api_client.jget.assert_called_once_with(
            f"{incidents.INCIDENTS_URL}/{incident_id}", params={"include[]": "body"}
        )

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

        parsed_main_incident = dict(mock_incidents_parsed[0])
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


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_show_incident_error_handling(
    mock_get_api_client, mock_incidents, caplog
):
    """Test error handling in show_incident for various scenarios."""
    incident_id = "123"

    with pytest.raises(ValueError) as exc_info:
        await incidents.show_incident(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"

    mock_get_api_client.jget.side_effect = RuntimeError("API Error")
    with pytest.raises(RuntimeError) as exc_info:
        await incidents.show_incident(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"

    mock_get_api_client.jget.side_effect = None
    mock_get_api_client.jget.return_value = {}  # Missing 'incident' key
    with pytest.raises(RuntimeError) as exc_info:
        await incidents.show_incident(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch or process incident {incident_id}: 'incident'"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize(
    "params, expected_api_params, mock_response_slice",
    [
        ({}, {"limit": None, "total": None}, slice(None)),
        (
            {"limit": 1, "total": True},
            {"limit": 1, "total": True},
            slice(0, 1),
        ),
    ],
)
async def test_list_past_incidents_success(
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

    mock_get_api_client.jget.return_value = {
        "past_incidents": mock_past_incidents[mock_response_slice]
    }

    past_incidents = await incidents._list_past_incidents(
        incident_id=incident_id, **params
    )

    mock_get_api_client.jget.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/past_incidents",
        params=expected_api_params,
    )

    expected_response = utils.api_response_handler(
        results=[
            {
                "id": item["incident"]["id"],
                "created_at": item["incident"]["created_at"],
                "title": item["incident"]["title"],
                "similarity_score": item["score"],
            }
            for item in mock_past_incidents[mock_response_slice]
        ],
        resource_name="incidents",
    )
    assert past_incidents == expected_response


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_past_incidents_error_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        await incidents._list_past_incidents(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_past_incidents_error_api(mock_get_api_client):
    """Test that API errors are properly propagated."""
    incident_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_past_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_past_incidents_error_invalid_response(mock_get_api_client):
    """Test that invalid API responses are properly handled."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'past_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_past_incidents(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch past incidents for {incident_id}: Response missing 'past_incidents' field"
    )


@pytest.mark.asyncio
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
                "id": item["incident"]["id"],
                "created_at": item["incident"]["created_at"],
                "title": item["incident"]["title"],
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
                "id": item["incident"]["id"],
                "created_at": item["incident"]["created_at"],
                "title": item["incident"]["title"],
                "relationship_type": None,
                "relationship_metadata": None,
            },
        },
    ],
)
async def test_list_related_incidents_success(mock_get_api_client, test_case):
    """Test that related incidents are fetched correctly with various relationship structures."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {
        "related_incidents": test_case["mock_data"]
    }

    related_incidents = await incidents._list_related_incidents(incident_id=incident_id)

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


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_related_incidents_error_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        await incidents._list_related_incidents(incident_id="")
    assert str(exc_info.value) == "incident_id cannot be empty"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_related_incidents_error_api(mock_get_api_client):
    """Test that API errors are properly propagated."""
    incident_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_related_incidents(incident_id=incident_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_related_incidents_error_invalid_response(mock_get_api_client):
    """Test that invalid API responses are properly handled."""
    incident_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'related_incidents' key

    with pytest.raises(RuntimeError) as exc_info:
        await incidents._list_related_incidents(incident_id=incident_id)
    assert (
        str(exc_info.value)
        == f"Failed to fetch related incidents for {incident_id}: Response missing 'related_incidents' field"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_with_include_single_field(
    mock_get_api_client, mock_incidents
):
    """Test that incidents can be filtered to include only specific fields."""
    mock_get_api_client.iter_all.return_value = mock_incidents

    incident_list = await incidents.list_incidents(include=["id"])

    mock_get_api_client.iter_all.assert_called_once_with(
        incidents.INCIDENTS_URL,
        params={
            "statuses": incidents.DEFAULT_STATUSES,
            "urgencies": incidents.DEFAULT_URGENCIES,
        },
        page_size=100,
    )

    assert len(incident_list["incidents"]) > 0
    for incident in incident_list["incidents"]:
        assert "id" in incident
        assert len(incident.keys()) == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_with_include_multiple_fields(
    mock_get_api_client, mock_incidents
):
    """Test that incidents can be filtered to include multiple specific fields."""
    mock_get_api_client.iter_all.return_value = mock_incidents

    incident_list = await incidents.list_incidents(include=["id", "title", "status"])

    assert len(incident_list["incidents"]) > 0
    for incident in incident_list["incidents"]:
        assert "id" in incident
        assert "title" in incident
        assert "status" in incident
        assert len(incident.keys()) == 3


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_list_incidents_with_include_nonexistent_field(
    mock_get_api_client, mock_incidents
):
    """Test that including non-existent fields doesn't break the response."""
    mock_get_api_client.iter_all.return_value = mock_incidents

    incident_list = await incidents.list_incidents(include=["id", "nonexistent_field"])

    assert len(incident_list["incidents"]) > 0
    for incident in incident_list["incidents"]:
        assert "id" in incident
        assert "nonexistent_field" not in incident
        assert len(incident.keys()) == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_show_incident_with_include_single_field(
    mock_get_api_client, mock_incidents
):
    """Test that a single incident can be filtered to include only specific fields."""
    incident_id = mock_incidents[0]["id"]
    mock_get_api_client.jget.return_value = {"incident": mock_incidents[0]}

    incident = await incidents.show_incident(incident_id=incident_id, include=["id"])

    assert "id" in incident["incident"][0]
    assert len(incident["incident"][0].keys()) == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_show_incident_with_include_multiple_fields(
    mock_get_api_client, mock_incidents
):
    """Test that a single incident can be filtered to include multiple specific fields."""
    incident_id = mock_incidents[0]["id"]
    mock_get_api_client.jget.return_value = {"incident": mock_incidents[0]}

    incident = await incidents.show_incident(
        incident_id=incident_id, include=["id", "title", "status", "created_at"]
    )

    incident_data = incident["incident"][0]
    assert "id" in incident_data
    assert "title" in incident_data
    assert "status" in incident_data
    assert "created_at" in incident_data
    assert len(incident_data.keys()) == 4


"""
Write Operation Tests
"""


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
@pytest.mark.parametrize("status", ["acknowledged", "resolved"])
async def test_update_incident_status(
    mock_get_api_client, mock_user_email_patch, mock_incidents, status
):
    """Test that incident status can be updated (acknowledge/resolve)."""
    incident_id = mock_incidents[0]["id"]
    updated_incident = {**mock_incidents[0], "status": status}
    mock_get_api_client.jput.return_value = {"incident": updated_incident}

    result = await incidents.update_incident_status(
        incident_id=incident_id, status=status
    )

    mock_get_api_client.jput.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}",
        json={"incident": {"type": "incident_reference", "status": status}},
        headers={"From": MOCK_USER_EMAIL},
    )
    assert "incident" in result
    assert "metadata" in result
    assert result["metadata"]["count"] == 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_update_incident_status_with_include(
    mock_get_api_client, mock_user_email_patch, mock_incidents
):
    """Test that update_incident_status respects include parameter."""
    incident_id = mock_incidents[0]["id"]
    mock_get_api_client.jput.return_value = {"incident": mock_incidents[0]}

    result = await incidents.update_incident_status(
        incident_id=incident_id, status="acknowledged", include=["id", "status"]
    )

    incident_data = result["incident"][0]
    assert "id" in incident_data
    assert len(incident_data.keys()) <= 2


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_update_incident_status_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError, match="incident_id cannot be empty"):
        await incidents.update_incident_status(incident_id="", status="acknowledged")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_update_incident_status_invalid_status():
    """Test that invalid status raises ValueError."""
    with pytest.raises(ValueError, match="Invalid status"):
        await incidents.update_incident_status(incident_id="123", status="triggered")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_update_incident_status_api_error(
    mock_get_api_client, mock_user_email_patch
):
    """Test that API errors are propagated."""
    mock_get_api_client.jput.side_effect = RuntimeError("API Error")
    with pytest.raises(RuntimeError, match="API Error"):
        await incidents.update_incident_status(incident_id="123", status="acknowledged")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_update_incident_status_invalid_response(
    mock_get_api_client, mock_user_email_patch
):
    """Test that invalid API responses are handled."""
    mock_get_api_client.jput.return_value = {}
    with pytest.raises(RuntimeError, match="Response missing 'incident' field"):
        await incidents.update_incident_status(incident_id="123", status="acknowledged")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_create_incident_note(mock_get_api_client, mock_user_email_patch):
    """Test that a note can be added to an incident."""
    incident_id = "123"
    content = "Investigating root cause"
    mock_note = {
        "id": "NOTE-1",
        "content": content,
        "created_at": "2024-03-14T12:00:00Z",
        "user": {"id": "USER-1", "summary": "Test User"},
        "channel": {"summary": "The PagerDuty website or APIs"},
    }
    mock_get_api_client.jpost.return_value = {"note": mock_note}

    result = await incidents.create_incident_note(
        incident_id=incident_id, content=content
    )

    mock_get_api_client.jpost.assert_called_once_with(
        f"{incidents.INCIDENTS_URL}/{incident_id}/notes",
        json={"note": {"content": content}},
        headers={"From": MOCK_USER_EMAIL},
    )
    assert "note" in result
    assert "metadata" in result
    assert result["metadata"]["count"] == 1
    assert result["note"][0]["id"] == "NOTE-1"
    assert result["note"][0]["content"] == content


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_create_incident_note_empty_id():
    """Test that empty incident_id raises ValueError."""
    with pytest.raises(ValueError, match="incident_id cannot be empty"):
        await incidents.create_incident_note(incident_id="", content="test")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_create_incident_note_empty_content():
    """Test that empty content raises ValueError."""
    with pytest.raises(ValueError, match="content cannot be empty"):
        await incidents.create_incident_note(incident_id="123", content="")

    with pytest.raises(ValueError, match="content cannot be empty"):
        await incidents.create_incident_note(incident_id="123", content="   ")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_create_incident_note_api_error(
    mock_get_api_client, mock_user_email_patch
):
    """Test that API errors are propagated."""
    mock_get_api_client.jpost.side_effect = RuntimeError("API Error")
    with pytest.raises(RuntimeError, match="API Error"):
        await incidents.create_incident_note(incident_id="123", content="test")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_create_incident_note_invalid_response(
    mock_get_api_client, mock_user_email_patch
):
    """Test that invalid API responses are handled."""
    mock_get_api_client.jpost.return_value = {}
    with pytest.raises(RuntimeError, match="Response missing 'note' field"):
        await incidents.create_incident_note(incident_id="123", content="test")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_get_current_user_email_env_var(monkeypatch):
    """Test that PAGERDUTY_USER_EMAIL env var is used as fallback."""
    import pagerduty_mcp_server.incidents as inc_module

    monkeypatch.setenv("PAGERDUTY_USER_EMAIL", "env@example.com")
    inc_module._cached_user_email = None
    email = await inc_module._get_current_user_email()
    assert email == "env@example.com"
    inc_module._cached_user_email = None


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_get_current_user_email_cached():
    """Test that cached email is returned without API calls."""
    import pagerduty_mcp_server.incidents as inc_module

    inc_module._cached_user_email = "cached@example.com"
    email = await inc_module._get_current_user_email()
    assert email == "cached@example.com"
    inc_module._cached_user_email = None


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.incidents
async def test_get_current_user_email_failure(monkeypatch):
    """Test RuntimeError when email cannot be determined."""
    import pagerduty_mcp_server.incidents as inc_module
    from unittest.mock import AsyncMock

    monkeypatch.delenv("PAGERDUTY_USER_EMAIL", raising=False)
    inc_module._cached_user_email = None
    with patch(
        "pagerduty_mcp_server.users.build_user_context",
        new_callable=AsyncMock,
        return_value={"email": ""},
    ):
        with pytest.raises(RuntimeError, match="Cannot determine current user email"):
            await inc_module._get_current_user_email()
    inc_module._cached_user_email = None


@pytest.mark.unit
@pytest.mark.incidents
def test_validate_incident_id_valid():
    """Test valid incident IDs are accepted."""
    incidents._validate_incident_id("Q1ABC123")
    incidents._validate_incident_id("P12345")
    incidents._validate_incident_id("ABC")


@pytest.mark.unit
@pytest.mark.incidents
def test_validate_incident_id_invalid():
    """Test invalid incident IDs are rejected."""
    with pytest.raises(ValueError, match="Invalid incident_id format"):
        incidents._validate_incident_id("../../etc/passwd")
    with pytest.raises(ValueError, match="Invalid incident_id format"):
        incidents._validate_incident_id("Q1 ABC")
    with pytest.raises(ValueError, match="Invalid incident_id format"):
        incidents._validate_incident_id("Q1/ABC")

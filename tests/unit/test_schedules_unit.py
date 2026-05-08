"""Unit tests for the schedules module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import schedules, utils
from pagerduty_mcp_server.models.user import User
from tests.helpers import ApiRuntimeError


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules(
    mock_get_api_client, mock_schedules, mock_schedules_parsed
):
    """Test that schedules are fetched correctly."""
    mock_get_api_client.iter_all.return_value = mock_schedules

    schedule_list = await schedules.list_schedules()

    mock_get_api_client.iter_all.assert_called_once_with(
        schedules.SCHEDULES_URL, params={}, page_size=100
    )
    assert schedule_list == utils.api_response_handler(
        results=mock_schedules_parsed,
        resource_name="schedules",
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules_with_query(
    mock_get_api_client, mock_schedules, mock_schedules_parsed
):
    """Test that schedules can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.iter_all.return_value = mock_schedules

    schedule_list = await schedules.list_schedules(query=query)

    mock_get_api_client.iter_all.assert_called_once_with(
        schedules.SCHEDULES_URL, params={"query": query}, page_size=100
    )
    assert schedule_list == utils.api_response_handler(
        results=mock_schedules_parsed,
        resource_name="schedules",
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules_api_error(mock_get_api_client):
    """Test that list_schedules handles API errors correctly."""
    mock_get_api_client.iter_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await schedules.list_schedules()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules_empty_response(mock_get_api_client):
    """Test that list_schedules handles empty response correctly."""
    mock_get_api_client.iter_all.return_value = []

    schedule_list = await schedules.list_schedules()
    assert schedule_list == utils.api_response_handler(
        results=[], resource_name="schedules"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule(
    mock_get_api_client, mock_schedules, mock_schedules_parsed
):
    """Test that a single schedule is fetched correctly."""
    schedule_id = mock_schedules[0]["id"]
    since = "2024-01-01T00:00:00Z"
    until = "2024-02-01T00:00:00Z"
    mock_get_api_client.jget.return_value = {"schedule": mock_schedules[0]}

    schedule = await schedules.show_schedule(
        schedule_id=schedule_id, since=since, until=until
    )

    mock_get_api_client.jget.assert_called_once_with(
        f"{schedules.SCHEDULES_URL}/{schedule_id}",
        params={"since": since, "until": until},
    )
    assert schedule == utils.api_response_handler(
        results=mock_schedules_parsed[0], resource_name="schedule"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule_no_date_params(
    mock_get_api_client, mock_schedules, mock_schedules_parsed
):
    """Test that a single schedule is fetched correctly without date parameters."""
    schedule_id = mock_schedules[0]["id"]
    mock_get_api_client.jget.return_value = {"schedule": mock_schedules[0]}

    schedule = await schedules.show_schedule(schedule_id=schedule_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{schedules.SCHEDULES_URL}/{schedule_id}", params={}
    )
    assert schedule == utils.api_response_handler(
        results=mock_schedules_parsed[0], resource_name="schedule"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule_invalid_id(mock_get_api_client):
    """Test that show_schedule raises ValueError for invalid schedule ID."""
    with pytest.raises(ValueError) as exc_info:
        await schedules.show_schedule(schedule_id="")
    assert str(exc_info.value) == "schedule_id cannot be empty"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule_invalid_response(mock_get_api_client):
    """Test that show_schedule handles invalid API response correctly."""
    schedule_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'schedule' key

    with pytest.raises(RuntimeError) as exc_info:
        await schedules.show_schedule(schedule_id=schedule_id)
    assert (
        str(exc_info.value)
        == "Failed to fetch schedule 123: Response missing 'schedule' field"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_users_oncall(mock_get_api_client, mock_schedules):
    """Test that users on call for a schedule are fetched correctly."""
    schedule_id = mock_schedules[0]["id"]
    mock_users_data = [
        {"id": "P789012", "summary": "John Doe", "email": "john.doe@example.com"},
        {"id": "P345678", "summary": "Jane Smith", "email": "jane.smith@example.com"},
    ]
    mock_get_api_client.jget.return_value = {"users": mock_users_data}

    users_list = await schedules.list_users_oncall(schedule_id=schedule_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{schedules.SCHEDULES_URL}/{schedule_id}/users", params={}
    )
    expected_users = [User.model_validate(u).to_clean_dict() for u in mock_users_data]
    assert users_list == utils.api_response_handler(
        results=expected_users, resource_name="users"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_users_oncall_with_date_range(mock_get_api_client, mock_schedules):
    """Test that users on call can be fetched with date range parameters."""
    schedule_id = mock_schedules[0]["id"]
    since = (datetime.now() - timedelta(days=7)).isoformat()
    until = datetime.now().isoformat()
    mock_users_data = [
        {"id": "P789012", "summary": "John Doe", "email": "john.doe@example.com"}
    ]
    mock_get_api_client.jget.return_value = {"users": mock_users_data}

    users_list = await schedules.list_users_oncall(
        schedule_id=schedule_id, since=since, until=until
    )

    mock_get_api_client.jget.assert_called_once_with(
        f"{schedules.SCHEDULES_URL}/{schedule_id}/users",
        params={"since": since, "until": until},
    )
    expected_users = [User.model_validate(u).to_clean_dict() for u in mock_users_data]
    assert users_list == utils.api_response_handler(
        results=expected_users, resource_name="users"
    )


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_users_oncall_empty_schedule_id(mock_get_api_client):
    """Test that list_users_oncall raises ValueError for empty schedule ID."""
    with pytest.raises(ValueError) as exc_info:
        await schedules.list_users_oncall(schedule_id="")
    assert str(exc_info.value) == "schedule_id cannot be empty"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_users_oncall_api_error(mock_get_api_client):
    """Test that list_users_oncall handles API errors correctly."""
    schedule_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await schedules.list_users_oncall(schedule_id=schedule_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_users_oncall_empty_response(mock_get_api_client):
    """Test that list_users_oncall handles empty response correctly."""
    schedule_id = "123"
    mock_get_api_client.jget.return_value = {"users": []}

    users_list = await schedules.list_users_oncall(schedule_id=schedule_id)
    assert users_list == utils.api_response_handler(results=[], resource_name="users")


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules_preserves_full_error_message(mock_get_api_client):
    """Test that list_schedules preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = ApiRuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.iter_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        await schedules.list_schedules()
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule_api_error(mock_get_api_client):
    """Test that show_schedule handles API errors correctly."""
    schedule_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        await schedules.show_schedule(schedule_id=schedule_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_list_schedules_with_include(mock_get_api_client, mock_schedules):
    """Test that schedules can be filtered to include only specific fields."""
    mock_get_api_client.iter_all.return_value = mock_schedules

    schedule_list = await schedules.list_schedules(include=["id", "name"])

    assert len(schedule_list["schedules"]) > 0
    for schedule in schedule_list["schedules"]:
        assert "id" in schedule
        assert "name" in schedule
        assert len(schedule.keys()) == 2


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.schedules
async def test_show_schedule_with_include(mock_get_api_client, mock_schedules):
    """Test that a single schedule can be filtered to include only specific fields."""
    schedule_id = mock_schedules[0]["id"]
    mock_get_api_client.jget.return_value = {"schedule": mock_schedules[0]}

    schedule = await schedules.show_schedule(schedule_id=schedule_id, include=["id"])

    assert "id" in schedule["schedule"][0]
    assert len(schedule["schedule"][0].keys()) == 1

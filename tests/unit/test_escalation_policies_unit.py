from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import escalation_policies, utils
from pagerduty_mcp_server.parsers.escalation_policy_parser import (
    parse_escalation_policy,
)


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies(mock_get_api_client, mock_escalation_policies):
    """Test that escalation policies are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_escalation_policies

    policy_list = escalation_policies.list_escalation_policies()

    mock_get_api_client.list_all.assert_called_once_with(
        escalation_policies.ESCALATION_POLICIES_URL, params={}
    )
    assert policy_list == utils.api_response_handler(
        results=[
            parse_escalation_policy(result=policy)
            for policy in mock_escalation_policies
        ],
        resource_name="escalation_policies",
    )


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies_with_query(
    mock_get_api_client, mock_escalation_policies
):
    """Test that escalation policies can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.list_all.return_value = mock_escalation_policies

    policy_list = escalation_policies.list_escalation_policies(query=query)

    mock_get_api_client.list_all.assert_called_once_with(
        escalation_policies.ESCALATION_POLICIES_URL, params={"query": query}
    )
    assert policy_list == utils.api_response_handler(
        results=[
            parse_escalation_policy(result=policy)
            for policy in mock_escalation_policies
        ],
        resource_name="escalation_policies",
    )


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies_api_error(mock_get_api_client):
    """Test that list_escalation_policies handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        escalation_policies.list_escalation_policies()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies_empty_response(mock_get_api_client):
    """Test that list_escalation_policies handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    policy_list = escalation_policies.list_escalation_policies()
    assert policy_list == utils.api_response_handler(
        results=[], resource_name="escalation_policies"
    )


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_list_escalation_policies_preserves_full_error_message(mock_get_api_client):
    """Test that list_escalation_policies preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.list_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        escalation_policies.list_escalation_policies()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_fetch_escalation_policy_ids(
    mock_get_api_client, mock_escalation_policies, mock_user
):
    """Test that escalation policy IDs are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_escalation_policies

    policy_ids = escalation_policies.fetch_escalation_policy_ids(
        user_id=mock_user["id"]
    )

    mock_get_api_client.list_all.assert_called_once_with(
        escalation_policies.ESCALATION_POLICIES_URL,
        params={"user_ids[]": [mock_user["id"]]},
    )
    assert set(policy_ids) == set([policy["id"] for policy in mock_escalation_policies])


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_fetch_escalation_policy_ids_api_error(mock_get_api_client, mock_user):
    """Test that fetch_escalation_policy_ids handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        escalation_policies.fetch_escalation_policy_ids(user_id=mock_user["id"])
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_show_escalation_policy(mock_get_api_client, mock_escalation_policies):
    """Test that a single escalation policy is fetched correctly."""
    policy_id = mock_escalation_policies[0]["id"]
    mock_get_api_client.jget.return_value = {
        "escalation_policy": mock_escalation_policies[0]
    }

    policy = escalation_policies.show_escalation_policy(policy_id=policy_id)

    mock_get_api_client.jget.assert_called_once_with(
        f"{escalation_policies.ESCALATION_POLICIES_URL}/{policy_id}"
    )
    assert policy == utils.api_response_handler(
        results=parse_escalation_policy(result=mock_escalation_policies[0]),
        resource_name="escalation_policy",
    )


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_show_escalation_policy_invalid_id(mock_get_api_client):
    """Test that show_escalation_policy raises ValueError for invalid policy ID."""
    with pytest.raises(ValueError) as exc_info:
        escalation_policies.show_escalation_policy(policy_id="")
    assert str(exc_info.value) == "policy_id cannot be empty"


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_show_escalation_policy_api_error(mock_get_api_client):
    """Test that show_escalation_policy handles API errors correctly."""
    policy_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        escalation_policies.show_escalation_policy(policy_id=policy_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.escalation_policies
def test_show_escalation_policy_invalid_response(mock_get_api_client):
    """Test that show_escalation_policy handles invalid API response correctly."""
    policy_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'escalation_policy' key

    with pytest.raises(RuntimeError) as exc_info:
        escalation_policies.show_escalation_policy(policy_id=policy_id)
    assert (
        str(exc_info.value)
        == "Failed to fetch escalation policy 123: Response missing 'escalation_policy' field"
    )


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.escalation_policies
def test_parse_escalation_policy(
    mock_escalation_policies, mock_escalation_policies_parsed
):
    """Test that parse_escalation_policy correctly parses raw escalation policy data."""
    parsed_policy = parse_escalation_policy(result=mock_escalation_policies[0])
    assert parsed_policy == mock_escalation_policies_parsed[0]


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.escalation_policies
def test_parse_escalation_policy_none():
    """Test that parse_escalation_policy handles None input correctly."""
    assert parse_escalation_policy(result=None) == {}

"""Unit tests for the teams module."""

from unittest.mock import MagicMock

import pytest

from pagerduty_mcp_server import teams, utils
from pagerduty_mcp_server.parsers.team_parser import parse_team


@pytest.mark.unit
@pytest.mark.teams
def test_list_teams(mock_get_api_client, mock_teams):
    """Test that teams are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_teams

    team_list = teams.list_teams()

    mock_get_api_client.list_all.assert_called_once_with(teams.TEAMS_URL, params={})
    assert team_list == utils.api_response_handler(
        results=[parse_team(result=team) for team in mock_teams], resource_name="teams"
    )


@pytest.mark.unit
@pytest.mark.teams
def test_list_teams_with_query(mock_get_api_client, mock_teams):
    """Test that teams can be filtered by query parameter."""
    query = "test"
    mock_get_api_client.list_all.return_value = mock_teams

    team_list = teams.list_teams(query=query)

    mock_get_api_client.list_all.assert_called_once_with(
        teams.TEAMS_URL, params={"query": query}
    )
    assert team_list == utils.api_response_handler(
        results=[parse_team(result=team) for team in mock_teams], resource_name="teams"
    )


@pytest.mark.unit
@pytest.mark.teams
def test_list_teams_api_error(mock_get_api_client):
    """Test that list_teams handles API errors correctly."""
    mock_get_api_client.list_all.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        teams.list_teams()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.teams
def test_list_teams_empty_response(mock_get_api_client):
    """Test that list_teams handles empty response correctly."""
    mock_get_api_client.list_all.return_value = []

    team_list = teams.list_teams()
    assert team_list == utils.api_response_handler(results=[], resource_name="teams")


@pytest.mark.unit
@pytest.mark.teams
def test_list_teams_preserves_full_error_message(mock_get_api_client):
    """Test that list_teams preserves the full error message from the API response."""
    mock_response = MagicMock()
    mock_response.text = '{"error":{"message":"Invalid Input Provided","code":2001,"errors":["Invalid team ID format"]}}'
    mock_error = RuntimeError("API Error")
    mock_error.response = mock_response
    mock_get_api_client.list_all.side_effect = mock_error

    with pytest.raises(RuntimeError) as exc_info:
        teams.list_teams()
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.teams
def test_fetch_team_ids(mock_team_ids, mock_user):
    """Test that team IDs are fetched correctly."""
    team_ids = teams.fetch_team_ids(user=mock_user)

    assert set(team_ids) == set(mock_team_ids)


@pytest.mark.unit
@pytest.mark.teams
def test_fetch_team_ids_empty_user(mock_user):
    """Test that fetch_team_ids handles empty user data correctly."""
    mock_user["teams"] = []
    team_ids = teams.fetch_team_ids(user=mock_user)
    assert team_ids == []


@pytest.mark.unit
@pytest.mark.teams
def test_show_team(mock_get_api_client, mock_teams):
    """Test that a single team is fetched correctly."""
    team_id = mock_teams[0]["id"]
    mock_get_api_client.jget.return_value = {"team": mock_teams[0]}

    team = teams.show_team(team_id=team_id)

    mock_get_api_client.jget.assert_called_once_with(f"{teams.TEAMS_URL}/{team_id}")
    assert team == utils.api_response_handler(
        results=parse_team(result=mock_teams[0]), resource_name="team"
    )


@pytest.mark.unit
@pytest.mark.teams
def test_show_team_invalid_id(mock_get_api_client):
    """Test that show_team raises ValueError for invalid team ID."""
    with pytest.raises(ValueError) as exc_info:
        teams.show_team(team_id=None)
    assert str(exc_info.value) == "team_id must be specified"


@pytest.mark.unit
@pytest.mark.teams
def test_show_team_api_error(mock_get_api_client):
    """Test that show_team handles API errors correctly."""
    team_id = "123"
    mock_get_api_client.jget.side_effect = RuntimeError("API Error")

    with pytest.raises(RuntimeError) as exc_info:
        teams.show_team(team_id=team_id)
    assert str(exc_info.value) == "API Error"


@pytest.mark.unit
@pytest.mark.teams
def test_show_team_invalid_response(mock_get_api_client):
    """Test that show_team handles invalid API response correctly."""
    team_id = "123"
    mock_get_api_client.jget.return_value = {}  # Missing 'team' key

    with pytest.raises(RuntimeError) as exc_info:
        teams.show_team(team_id=team_id)
    assert (
        str(exc_info.value) == "Failed to fetch team 123: Response missing 'team' field"
    )


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.teams
def test_parse_team(mock_teams, mock_teams_parsed):
    """Test that parse_team correctly parses raw team data."""
    parsed_team = parse_team(result=mock_teams[0])
    assert parsed_team == mock_teams_parsed[0]


@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.teams
def test_parse_team_none():
    """Test that parse_team handles None input correctly."""
    assert parse_team(result=None) == {}

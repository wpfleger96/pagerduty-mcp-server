"""Unit tests for the teams module."""

import pytest

from pagerduty_mcp_server import teams
from pagerduty_mcp_server.parsers.team_parser import parse_team
from pagerduty_mcp_server import utils

@pytest.mark.unit
@pytest.mark.teams
def test_list_teams(mock_get_api_client, mock_teams, mock_teams_parsed):
    """Test that teams are fetched correctly."""
    mock_get_api_client.list_all.return_value = mock_teams

    team_list = teams.list_teams()

    mock_get_api_client.list_all.assert_called_once_with(teams.TEAMS_URL, params={})
    assert team_list == utils.api_response_handler(results=[parse_team(result=team) for team in mock_teams], resource_name='teams')

@pytest.mark.unit
@pytest.mark.teams
def test_fetch_team_ids(mock_team_ids, mock_user):
    """Test that team IDs are fetched correctly."""
    team_ids = teams.fetch_team_ids(user=mock_user)

    assert set(team_ids) == set(mock_team_ids)

@pytest.mark.unit
@pytest.mark.parsers
@pytest.mark.teams
def test_parse_team(mock_teams, mock_teams_parsed):
    """Test that parse_team correctly parses raw team data."""
    parsed_team = parse_team(result=mock_teams[0])
    assert parsed_team == mock_teams_parsed[0]

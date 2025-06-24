"""PagerDuty team operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .client import create_client
from .parsers import parse_team

logger = logging.getLogger(__name__)

TEAMS_URL = "/teams"

"""
Teams API Helpers
"""


def list_teams(
    *, query: Optional[str] = None, limit: Optional[int] = None
) -> Dict[str, Any]:
    """List teams in your PagerDuty account. Exposed as MCP server tool.

    Args:
        query (str): Filter teams whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of teams with their configuration and member information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    params = {}
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(TEAMS_URL, params=params)
        parsed_response = [parse_team(result=team) for team in response]
        return utils.api_response_handler(
            results=parsed_response, resource_name="teams"
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_team(*, team_id: str) -> Dict[str, Any]:
    """Get detailed information about a given team. Exposed as MCP server tool.

    Args:
        team_id (str): The ID of the team to get

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single team with detailed configuration and member information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if team_id is None:
        raise ValueError("team_id must be specified")

    pd_client = create_client()

    try:
        response = pd_client.jget(f"{TEAMS_URL}/{team_id}")
        try:
            team_data = response["team"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch team {team_id}: Response missing 'team' field"
            )

        return utils.api_response_handler(
            results=parse_team(result=team_data), resource_name="team"
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Teams Helpers
"""


def fetch_team_ids(*, user: Dict[str, Any]) -> List[str]:
    """Get the team IDs for a user. Internal helper function.

    Args:
        user (Dict[str, Any]): The user object containing a teams field with team information

    Returns:
        List[str]: A list of team IDs from the user's teams. Returns an empty list if user is None or has no teams.

    Note:
        This is an internal helper function used by other modules to extract team IDs from a user object.
        It should not be called directly by external code.

    Raises:
        KeyError: If user is None or missing the 'teams' field
    """

    return [team["id"] for team in user["teams"]]

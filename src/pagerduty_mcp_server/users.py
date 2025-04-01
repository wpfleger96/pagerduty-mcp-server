"""PagerDuty user operations."""

import logging
from typing import List, Dict, Any, Optional

from . import client
from . import escalation_policies
from . import services
from . import teams
from . import utils
from .parsers import parse_user

USERS_URL = '/users'

logger = logging.getLogger(__name__)

def build_user_context() -> Dict[str, Any]:
    """Validate and build the current user's context into a dictionary with the following format:
        {
            "user_id": str,
            "name": str,
            "email": str,
            "team_ids": List[str],
            "service_ids": List[str],
            "escalation_policy_ids": List[str]
        }
    The MCP server tools use this user context to filter the following resources:
        - Escalation policies
        - Incidents
        - Oncalls
        - Services
        - Users

    Returns:
        Dict[str, Any]: A dictionary containing:
            - user_id (str): The current user's PagerDuty ID
            - name (str): The current user's full name
            - email (str): The current user's email address
            - team_ids (List[str]): List of team IDs the user belongs to
            - service_ids (List[str]): List of service IDs associated with the user's teams
            - escalation_policy_ids (List[str]): List of escalation policy IDs the user is part of

    Raises:
        RuntimeError: If there are API errors while fetching user data or related resources
        KeyError: If the API response is missing required fields
        ValueError: If the user data is invalid or missing required fields
    """
    try:
        user = show_current_user()
        if not user:
            raise ValueError("Failed to get current user data")

        context = {
            "user_id": str(user.get('id', '')).strip(),
            "name": user.get('name', ''),
            "email": user.get('email', ''),
            "team_ids": [],
            "service_ids": [],
            "escalation_policy_ids": []
        }

        if not context["user_id"]:
            raise ValueError("Invalid user data: missing or empty user ID")

        team_ids = teams.fetch_team_ids(user=user)
        context["team_ids"] = [str(tid).strip() for tid in team_ids if tid and str(tid).strip()]

        if context["team_ids"]:
            service_ids = services.fetch_service_ids(team_ids=context["team_ids"])
            context["service_ids"] = [str(sid).strip() for sid in service_ids if sid and str(sid).strip()]

        escalation_policy_ids = escalation_policies.fetch_escalation_policy_ids(user_id=context["user_id"])
        context["escalation_policy_ids"] = [str(epid).strip() for epid in escalation_policy_ids if epid and str(epid).strip()]

        return context

    except Exception as e:
        utils.handle_api_error(e)

"""
Users API Helpers
"""

def show_current_user() -> Dict[str, Any]:
    """Get the current user's PagerDuty profile including their teams, contact methods, and notification rules.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - user (Dict[str, Any]): The user object containing profile information (non-exhaustive list of fields):
                - name (str): User's full name
                - email (str): User's email address
                - role (str): User's role in PagerDuty
                - description (str): User's description
                - job_title (str): User's job title
                - teams (List[Dict[str, Any]]): List of teams with id and summary
                - contact_methods (List[Dict[str, Any]]): List of contact methods with id and summary
                - notification_rules (List[Dict[str, Any]]): List of notification rules with id and summary
                - id (str): User's PagerDuty ID
                Note: Additional fields may be present in the response.
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Always 1 for single resource responses
                - description (str): Description of the result
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        RuntimeError: If the API request fails or response processing fails
        KeyError: If the API response is missing required fields
        ValueError: If the user object is missing an ID
    """
    pd_client = client.get_api_client()
    try:
        response = pd_client.jget(USERS_URL + '/me')['user']
        user = parse_user(result=response)
        if not user or 'id' not in user or not user['id']:
            raise ValueError("Invalid user object: missing ID")
        return user
    except Exception as e:
        utils.handle_api_error(e)

def list_users(*,
               team_ids: Optional[List[str]] = None,
               query: Optional[str] = None,
               limit: Optional[int] = None) -> Dict[str, Any]:
    """List users in PagerDuty.

    Args:
        team_ids (List[str]): Filter results to only users assigned to teams with the given IDs (optional)
        query (str): Filter users whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        Dict[str, Any]: A dictionary containing:
            - users (List[Dict[str, Any]]): List of user objects matching the specified criteria
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Total number of results
                - description (str): Description of the results
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        ValueError: If team_ids is an empty list
        RuntimeError: If the API request fails or response processing fails
        KeyError: If the API response is missing required fields
    """

    pd_client = client.get_api_client()
    params = {}

    if team_ids:
        params['team_ids[]'] = team_ids
    if query:
        params['query'] = query
    if limit:
        params['limit'] = limit

    try:
        response = pd_client.list_all(USERS_URL, params=params)
        parsed_response = [parse_user(result=result) for result in response]
        return utils.api_response_handler(results=parsed_response, resource_name='users')
    except Exception as e:
        utils.handle_api_error(e)

def show_user(*,
              user_id: str) -> Dict[str, Any]:
    """Get detailed information about a given user.

    Args:
        user_id (str): The ID of the user to fetch

    Returns:
        Dict[str, Any]: A dictionary containing:
            - user (Dict[str, Any]): User object with detailed information
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Always 1 for single resource responses
                - description (str): Description of the result
            - error (Optional[Dict[str, Any]]): Error information if the API request fails

    Raises:
        ValueError: If user_id is None or empty
        RuntimeError: If the API request fails or response processing fails
        KeyError: If the API response is missing required fields
    """

    if not user_id:
        raise ValueError("User ID is required")

    pd_client = client.get_api_client()
    try:
        response = pd_client.jget(f"{USERS_URL}/{user_id}")
        try:
            user_data = response['user']
        except KeyError:
            raise RuntimeError(f"Failed to fetch user {user_id}: Response missing 'user' field")
            
        return utils.api_response_handler(
            results=parse_user(result=user_data),
            resource_name='user'
        )
    except Exception as e:
        utils.handle_api_error(e)

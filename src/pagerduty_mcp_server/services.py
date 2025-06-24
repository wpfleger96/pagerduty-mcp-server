"""PagerDuty service operations."""

import logging
from typing import Any, Dict, List, Optional

from . import utils
from .client import create_client
from .parsers import parse_service

logger = logging.getLogger(__name__)

SERVICES_URL = "/services"

"""
Services API Helpers
"""


def list_services(
    *,
    team_ids: Optional[List[str]] = None,
    query: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """List existing PagerDuty services. Exposed as MCP server tool.

    Args:
        team_ids (List[str]): Filter results to only services assigned to teams with the given IDs (optional)
        query (str): Filter services whose names contain the search query (optional)
        limit (int): Limit the number of results returned (optional)

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a list of services with their configuration and team assignments.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    pd_client = create_client()

    if team_ids is not None and not team_ids:
        raise ValueError("team_ids cannot be an empty list")

    params = {}
    if team_ids:
        params["team_ids[]"] = (
            team_ids  # PagerDuty API expects array parameters with [] suffix
        )
    if query:
        params["query"] = query
    if limit:
        params["limit"] = limit

    try:
        response = pd_client.list_all(SERVICES_URL, params=params)
        parsed_response = [parse_service(result=result) for result in response]
        return utils.api_response_handler(
            results=parsed_response, resource_name="services"
        )
    except Exception as e:
        utils.handle_api_error(e)


def show_service(*, service_id: str) -> Dict[str, Any]:
    """Get detailed information about a given service. Exposed as MCP server tool.

    Args:
        service_id (str): The ID of the service to get

    Returns:
        See the "Standard Response Format" section in `tools.md` for the complete standard response structure.
        The response will contain a single service with detailed configuration and team information.

    Raises:
        See the "Error Handling" section in `tools.md` for common error scenarios.
    """

    if not service_id:
        raise ValueError("service_id cannot be empty")

    pd_client = create_client()

    try:
        response = pd_client.jget(f"{SERVICES_URL}/{service_id}")
        try:
            service_data = response["service"]
        except KeyError:
            raise RuntimeError(
                f"Failed to fetch service {service_id}: Response missing 'service' field"
            )

        return utils.api_response_handler(
            results=parse_service(result=service_data), resource_name="service"
        )
    except Exception as e:
        utils.handle_api_error(e)


"""
Services Helpers
"""


def fetch_service_ids(*, team_ids: List[str]) -> List[str]:
    """Get the service IDs for a list of team IDs. Internal helper function.

    Args:
        team_ids (List[str]): A list of team IDs

    Returns:
        List[str]: A list of service IDs. Returns an empty list if no services are found.

    Note:
        This is an internal helper function used by other modules to fetch service IDs.
        The PagerDuty API expects array parameters with [] suffix (e.g., 'team_ids[]').

    Raises:
        ValueError: If team_ids is empty or None
        RuntimeError: If the API request fails or response processing fails
        KeyError: If the API response is missing required fields
    """
    if not team_ids:
        raise ValueError("Team IDs must be specified")

    pd_client = create_client()

    params = {
        "team_ids[]": team_ids
    }  # PagerDuty API expects array parameters with [] suffix
    try:
        services_response = pd_client.list_all(SERVICES_URL, params=params)
        parsed_response = [parse_service(result=result) for result in services_response]
        return [service["id"] for service in parsed_response]
    except Exception as e:
        utils.handle_api_error(e)

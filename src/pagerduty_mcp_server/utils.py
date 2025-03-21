"""Pagerduty helper utilities"""

from typing import List, Dict, Any, Optional, Union
import logging

from . import users, escalation_policies, teams, services

logger = logging.getLogger(__name__)

RESPONSE_LIMIT = 400

class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

"""
Utils public methods
"""

def build_user_context() -> Dict[str, Any]:
    """Validate and build the current user's context into a dictionary with the following format:
        {
            "user_id": str,
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
        Dict[str, Any]: Dictionary containing the current user's ID, team IDs, and service IDs.
            If the user context cannot be built (e.g., API errors or invalid user), returns a dictionary
            with empty strings for user_id and empty lists for all other fields.

    Raises:
        RuntimeError: If there are API errors while fetching user data
    """
    empty_context = {
        "user_id": "",
        "team_ids": [],
        "service_ids": [],
        "escalation_policy_ids": []
    }

    try:
        user = users.show_current_user()
        if not user or 'id' not in user or not user['id']:
            return empty_context

        user_id = str(user['id'])
        context = {**empty_context, "user_id": user_id}

        try:
            team_ids = teams.fetch_team_ids(user=user)
            team_ids = [str(tid) for tid in team_ids if tid and isinstance(tid, str) and str(tid).strip()]
            context["team_ids"] = team_ids
        except Exception as e:
            logger.error(f"Failed to fetch team IDs: {e}")
            return context

        try:
            service_ids = services.fetch_service_ids(team_ids=team_ids) if team_ids else []
            service_ids = [str(sid) for sid in service_ids if sid and isinstance(sid, str) and str(sid).strip()]
            context["service_ids"] = service_ids
        except Exception as e:
            logger.error(f"Failed to fetch service IDs: {e}")
            return context

        try:
            escalation_policy_ids = escalation_policies.fetch_escalation_policy_ids(user_id=user_id)
            escalation_policy_ids = [str(epid) for epid in escalation_policy_ids if epid and isinstance(epid, str) and str(epid).strip()]
            context["escalation_policy_ids"] = escalation_policy_ids
        except Exception as e:
            logger.error(f"Failed to fetch escalation policy IDs: {e}")
            return context

        return context
    except Exception as e:
        logger.error(f"Failed to build user context: {e}")
        return empty_context

def api_response_handler(*,
                        results: Union[Dict[str, Any], List[Dict[str, Any]]],
                        resource_name: str,
                        limit: Optional[int] = RESPONSE_LIMIT,
                        additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process API response and return a standardized format.

    Example response:
    {
        "metadata": {
            "count": 2,
            "description": "Found 2 results for resource type <resource_name>",
            # Additional metadata fields can be included here
        },
        "<resource_name>": [
            ...
        ]
    }

    Args:
        results (Union[Dict[str, Any], List[Dict[str, Any]]]): The API response results
        resource_name (str): The name of the resource (e.g., 'services', 'incidents').
            Use plural form for list operations, singular for single-item operations.
        limit (int): The maximum number of results allowed (optional, default is 400)
        additional_metadata (Dict[str, Any]): Optional additional metadata to include in the response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - {resource_name} (List[Dict[str, Any]]): The processed results as a list
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit

    Raises:
        ValidationError: If the results format is invalid or resource_name is empty
    """
    if not resource_name or not resource_name.strip():
        raise ValidationError("resource_name cannot be empty")

    if isinstance(results, dict):
        results = [results]

    if len(results) > limit:
        return {
            "metadata": {
                "count": len(results),
                "description": f"Query returned {len(results)} {resource_name}, which exceeds the limit of {limit}"
            },
            "error": {
                "code": "LIMIT_EXCEEDED",
                "message": f"Query returned {len(results)} {resource_name}, which exceeds the limit of {limit}"
            }
        }

    metadata = {
        "count": len(results),
        "description": f"Found {len(results)} {'result' if len(results) == 1 else 'results'} for resource type {resource_name}"
    }

    if additional_metadata:
        metadata.update(additional_metadata)

    return {
        "metadata": metadata,
        f"{resource_name}": results
    }

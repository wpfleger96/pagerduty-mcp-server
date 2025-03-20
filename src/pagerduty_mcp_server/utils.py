"""Pagerduty helper utilities"""

from typing import List, Dict, Any, Optional, Union
import logging

from . import users, escalation_policies, teams, services

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

def safe_get(obj: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with a default.
    
    Example:
        >>> data = {"name": "John", "age": 30}
        >>> safe_get(data, "name")  # Returns "John"
        >>> safe_get(data, "email")  # Returns None
        >>> safe_get(data, "email", "")  # Returns ""
        >>> safe_get(None, "name")  # Returns None
    """
    return obj.get(key, default) if obj and isinstance(obj, dict) else default

def safe_nested_get(obj: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary.
    
    Example:
        >>> data = {"user": {"profile": {"name": "John"}}}
        >>> safe_nested_get(data, "user", "profile", "name")  # Returns "John"
        >>> safe_nested_get(data, "user", "email")  # Returns None
        >>> safe_nested_get(data, "invalid", "path")  # Returns None
        >>> safe_nested_get(None, "user", "name")  # Returns None
    """
    for key in keys:
        obj = safe_get(obj, key, {})
    return obj if obj != {} else default

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
    user = users.show_current_user()
    if not user or 'id' not in user:
        return {
            "user_id": "",
            "team_ids": [],
            "service_ids": [],
            "escalation_policy_ids": []
        }
    
    user_id = user['id']
    team_ids = teams.fetch_team_ids(user=user)
    service_ids = services.fetch_service_ids(team_ids=team_ids)
    escalation_policy_ids = escalation_policies.fetch_escalation_policy_ids(user_id=user_id)
    
    return {
        "user_id": str(user_id),
        "team_ids": [str(tid) for tid in team_ids],
        "service_ids": [str(sid) for sid in service_ids],
        "escalation_policy_ids": [str(epid) for epid in escalation_policy_ids]
    }

def api_response_handler(*,
                        results: Union[Dict[str, Any], List[Dict[str, Any]]],
                        resource_name: str,
                        limit: Optional[int] = 100,
                        additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process API response and return a standardized format.
    
    Example response:
    {
        "metadata": {
            "count": 2,
            "description": "Found 2 results for resource type escalation_policies",
            # Additional metadata fields can be included here
        },
        "escalation_policies": [
            ...
        ]
    }

    Args:
        results (Union[Dict[str, Any], List[Dict[str, Any]]]): The API response results
        resource_name (str): The name of the resource (e.g., 'services', 'incidents').
            Use plural form for list operations, singular for single-item operations.
        limit (int): The maximum number of results allowed (optional, default is 100)
        additional_metadata (Dict[str, Any]): Optional additional metadata to include in the response
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - {resource_name} (List[Dict[str, Any]]): The processed results as a list
            - metadata (Dict[str, Any]): Metadata about the response including total count and pagination info
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit
    
    Raises:
        ValidationError: If the results format is invalid
    """
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

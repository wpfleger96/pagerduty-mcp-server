"""Pagerduty helper utilities"""

from typing import List, Dict, Any, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

RESPONSE_LIMIT = 500

class ValidationError(Exception):
    """Raised when data validation fails."""
    pass

"""
Utils public methods
"""

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
        limit (int): The maximum number of results allowed (optional, default is {pagerduty_mcp_server.utils.RESPONSE_LIMIT})
        additional_metadata (Dict[str, Any]): Optional additional metadata to include in the response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - {resource_name} (List[Dict[str, Any]]): The processed results as a list
            - metadata (Dict[str, Any]): Metadata about the response including:
                - count (int): Total number of results
                - description (str): Description of the results
                - Additional fields from additional_metadata if provided
            - error (Optional[Dict[str, Any]]): Error information if the query exceeds the limit, containing:
                - code (str): Error code (e.g., "LIMIT_EXCEEDED")
                - message (str): Human-readable error message

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

def validate_iso8601_timestamp(timestamp: str, param_name: str) -> None:
    """Validate that a string is a valid ISO8601 timestamp.

    Args:
        timestamp (str): The timestamp string to validate
        param_name (str): The name of the parameter being validated (for error messages)

    Note:
        Accepts both UTC timestamps (ending in 'Z') and timestamps with timezone offsets.
        UTC timestamps are automatically converted to the equivalent offset format.

    Raises:
        ValidationError: If the timestamp is not a valid ISO8601 format
    """
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValidationError(f"Invalid ISO8601 timestamp for {param_name}: {timestamp}. Error: {str(e)}")

def handle_api_error(e: Exception) -> None:
    """Log the error and re-raise the original exception.

    Args:
        e (Exception): The exception that was raised

    Raises:
        Exception: The original exception without modification
    """
    # Get the full error message from the response if available
    if hasattr(e, 'response') and e.response is not None:
        error_message = e.response.text
    else:
        error_message = str(e)

    logger.error(error_message)
    raise e

"""Pagerduty helper utilities"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from . import prompts

logger = logging.getLogger(__name__)

RESPONSE_CHAR_LIMIT = 400000  # characters
RESPONSE_SIZE_LIMIT = 400000  # bytes


class ValidationError(Exception):
    """Raised when data validation fails."""

    pass


"""
Utils public methods
"""


def api_response_handler(
    *,
    results: Union[Dict[str, Any], List[Dict[str, Any]]],
    resource_name: str,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
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

    char_count = count_object_chars(results)
    byte_size = count_object_size(results)

    exceeded_limits = []
    if char_count > RESPONSE_CHAR_LIMIT:
        exceeded_limits.append(f"{RESPONSE_CHAR_LIMIT} characters")
    if byte_size > RESPONSE_SIZE_LIMIT:
        exceeded_limits.append(f"{RESPONSE_SIZE_LIMIT} bytes")

    if exceeded_limits:
        limits_exceeded_str = " and ".join(exceeded_limits)
        return {
            "error": {
                "code": "LIMIT_EXCEEDED",
                "message": prompts.handle_large_results(
                    resource_name=resource_name, limits_exceeded=limits_exceeded_str
                ),
            }
        }

    metadata = {
        "count": len(results),
        "description": f"Found {len(results)} {'result' if len(results) == 1 else 'results'} for resource type {resource_name}",
    }

    if additional_metadata:
        metadata.update(additional_metadata)

    return {"metadata": metadata, f"{resource_name}": results}


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
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise ValidationError(
            f"Invalid ISO8601 timestamp value `{timestamp}` for parameter `{param_name}`. Try using a valid ISO8601 timestamp (for example `2025-02-26T00:00:00Z`)."
        )


def handle_api_error(e: Exception) -> None:
    """Log the error and re-raise the original exception.

    Args:
        e (Exception): The exception that was raised

    Raises:
        Exception: The original exception without modification
    """
    # Get the full error message from the response if available
    if hasattr(e, "response") and e.response is not None:
        error_message = e.response.text
    else:
        error_message = str(e)

    logger.error(error_message)
    raise e


def count_object_size(obj: Any) -> int:
    """Recursively count the size of a Python object in bytes.

    This function traverses nested structures like dictionaries and lists
    to estimate the total memory footprint of complex objects.

    Args:
        obj (Any): The Python object to measure

    Returns:
        int: The approximate size of the object in bytes
    """
    # Track visited objects to handle circular references
    visited = set()

    def _count_size(obj):
        if id(obj) in visited:
            return 0

        visited.add(id(obj))

        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            for k, v in obj.items():
                size += _count_size(k)
                size += _count_size(v)
        elif isinstance(obj, (list, tuple, set)):
            for item in obj:
                size += _count_size(item)
        elif isinstance(obj, str):
            # String size is already accounted for in sys.getsizeof
            pass

        return size

    return _count_size(obj)


def count_object_chars(obj: Any) -> int:
    """Recursively count the character length of a Python object.

    This function traverses nested structures like dictionaries and lists
    to calculate the total character count when the object is represented as text.

    Args:
        obj (Any): The Python object to measure

    Returns:
        int: The total character count of the object
    """
    # Track visited objects to handle circular references
    visited = set()

    def _count_chars(obj):
        if id(obj) in visited:
            return 0

        visited.add(id(obj))

        if isinstance(obj, dict):
            count = 0
            for k, v in obj.items():
                count += _count_chars(k)
                count += _count_chars(v)
            return count
        elif isinstance(obj, (list, tuple, set)):
            count = 0
            for item in obj:
                count += _count_chars(item)
            return count
        elif isinstance(obj, str):
            return len(obj)
        else:
            return len(str(obj))

    return _count_chars(obj)

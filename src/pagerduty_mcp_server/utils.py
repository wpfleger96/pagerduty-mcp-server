"""Pagerduty helper utilities"""

import logging
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, NoReturn, Optional, Type, Union

from . import prompts
from .errors import PagerDutyError, PagerDutyResponseLimitError
from .models.common import PagerDutyBaseModel

logger = logging.getLogger(__name__)

RESPONSE_CHAR_LIMIT = 400000  # characters
RESPONSE_SIZE_LIMIT = 400000  # bytes


class ValidationError(PagerDutyError):
    """Raised when data validation fails."""


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
        prompt_message = prompts.handle_large_results(
            resource_name=resource_name, limits_exceeded=limits_exceeded_str
        )
        content = getattr(prompt_message, "content", None)
        message = getattr(content, "text", str(prompt_message))
        raise PagerDutyResponseLimitError(message)

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


def validate_timestamp_range(since: str, until: str) -> None:
    """Validate that a timestamp range is a valid query range in the PagerDuty API.

    The PagerDuty API doesn't allow query ranges longer than 6 months, or querying where since == until, but the API doesn't actually return a helpful error message in either case so LLMs are unable to recover.

    This function validates the range and raises a ValidationError if it's not valid.

    Args:
        since (str): The start of the date range
        until (str): The end of the date range

    Raises:
        ValidationError: If the date range is not valid
    """
    if since and until:
        since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
        until_dt = datetime.fromisoformat(until.replace("Z", "+00:00"))

        if since_dt > until_dt:
            raise ValidationError("`since` must be before `until`")
        if since_dt == until_dt:
            raise ValidationError(
                "`since` and `until` cannot be the exact same timestamp."
            )
        if (until_dt - since_dt) > timedelta(days=180):
            raise ValidationError(
                "The maximum query range is 6 months. Try narrowing your query range."
            )


def handle_api_error(e: Exception) -> NoReturn:
    """Log the error and re-raise the original exception.

    Args:
        e (Exception): The exception that was raised

    Raises:
        Exception: The original exception without modification
    """
    # Get the full error message from the response if available
    response = getattr(e, "response", None)
    if response is not None:
        error_message = response.text
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


def parse_list_response(
    response: List[Dict[str, Any]],
    model_class: Type[PagerDutyBaseModel],
    resource_name: str,
    include: Optional[List[str]] = None,
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Parse a paginated list response into a standardized API response.

    Args:
        response (List[Dict[str, Any]]): Raw list of items from the PagerDuty API
        model_class: Pydantic model class with model_validate and to_clean_dict methods
        resource_name (str): The name of the resource (e.g., 'services', 'incidents')
        include (List[str]): Optional list of fields to include in each item
        additional_metadata (Dict[str, Any]): Optional extra metadata to merge into the response

    Returns:
        Dict[str, Any]: Standardized API response via api_response_handler
    """
    parsed = []
    for item in response:
        if not item:
            continue
        model = model_class.model_validate(item)
        parsed.append(model.to_clean_dict(include_fields=include))
    return api_response_handler(
        results=parsed,
        resource_name=resource_name,
        additional_metadata=additional_metadata,
    )

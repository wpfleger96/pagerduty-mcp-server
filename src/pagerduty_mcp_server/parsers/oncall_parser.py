"""Parser for PagerDuty on-calls."""

from typing import Dict, Any

def parse_oncall(*,
                 result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw on-call API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw on-call API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - escalation_policy (Optional[Dict]): Policy information with id, summary, and html_url (None if not present)
            - escalation_level (Optional[int]): Level in the escalation policy (None if not present)
            - schedule (Optional[Dict]): Schedule information with id, summary, and html_url (None if not present)
            - user (Optional[Dict]): User information with id, summary, and html_url (None if not present)
            - start (Optional[str]): Start time in ISO 8601 format (None if not present)
            - end (Optional[str]): End time in ISO 8601 format (None if not present)

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    return {
        "escalation_policy": {
            "id": result.get("escalation_policy", {}).get("id"),
            "summary": result.get("escalation_policy", {}).get("summary"),
            "html_url": result.get("escalation_policy", {}).get("html_url")
        } if result.get("escalation_policy") else None,
        "escalation_level": result.get("escalation_level"),
        "schedule": {
            "id": result.get("schedule", {}).get("id"),
            "summary": result.get("schedule", {}).get("summary"),
            "html_url": result.get("schedule", {}).get("html_url")
        } if result.get("schedule") else None,
        "user": {
            "id": result.get("user", {}).get("id"),
            "summary": result.get("user", {}).get("summary"),
            "html_url": result.get("user", {}).get("html_url")
        } if result.get("user") else None,
        "start": result.get("start"),
        "end": result.get("end")
    }

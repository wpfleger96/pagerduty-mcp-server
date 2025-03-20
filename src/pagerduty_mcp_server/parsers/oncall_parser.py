"""Parser for PagerDuty on-calls."""

from typing import Dict, Any, Optional

def parse_oncall(*,
                 result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw on-call API response into a structured format without unneeded fields.
    
    Args:
        result (Dict[str, Any]): The raw on-call API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - escalation_policy (Optional[Dict]): Policy information with id and summary
            - escalation_level (Optional[int]): Level in the escalation policy
            - schedule (Optional[Dict]): Schedule information with id and summary
            - user (Optional[Dict]): User information with id and summary
            - start (Optional[str]): Start time in ISO 8601 format
            - end (Optional[str]): End time in ISO 8601 format
    
    Note:
        Returns an empty dictionary if the input is None or not a dictionary.
        All fields are optional and will be None if not present in the input.
    """

    if not result:
        return {}
    
    return {
        "escalation_policy": {
            "id": result.get("escalation_policy", {}).get("id"),
            "summary": result.get("escalation_policy", {}).get("summary")
        } if result.get("escalation_policy") else None,
        "escalation_level": result.get("escalation_level"),
        "schedule": {
            "id": result.get("schedule", {}).get("id"),
            "summary": result.get("schedule", {}).get("summary")
        } if result.get("schedule") else None,
        "user": {
            "id": result.get("user", {}).get("id"),
            "summary": result.get("user", {}).get("summary")
        } if result.get("user") else None,
        "start": result.get("start"),
        "end": result.get("end")
    }

"""Parser for PagerDuty on-calls."""

from typing import Any, Dict


def parse_oncall(*, result: Dict[str, Any]) -> Dict[str, Any]:
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
        If the input is None or not a dictionary, returns an empty dictionary.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_oncall = {}

    # Simple fields
    simple_fields = ["escalation_level", "start", "end"]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_oncall[field] = value

    # Parse escalation policy
    escalation_policy = result.get("escalation_policy")
    if escalation_policy and escalation_policy.get("id"):
        parsed_ep = {"id": escalation_policy.get("id")}
        if escalation_policy.get("summary"):
            parsed_ep["summary"] = escalation_policy.get("summary")
        parsed_oncall["escalation_policy"] = parsed_ep

    # Parse schedule
    schedule = result.get("schedule")
    if schedule and schedule.get("id"):
        parsed_schedule = {"id": schedule.get("id")}
        if schedule.get("summary"):
            parsed_schedule["summary"] = schedule.get("summary")
        parsed_oncall["schedule"] = parsed_schedule

    # Parse user
    user = result.get("user")
    if user and user.get("id"):
        parsed_user = {"id": user.get("id")}
        if user.get("summary"):
            parsed_user["summary"] = user.get("summary")
        parsed_oncall["user"] = parsed_user

    return parsed_oncall

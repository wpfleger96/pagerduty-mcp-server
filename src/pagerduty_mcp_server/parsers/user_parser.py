"""Parser for PagerDuty users."""

from typing import Any, Dict


def parse_user(*, result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw user API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw user API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The user ID
            - name (str): The user's name
            - email (str): The user's email
            - description (str): The user's description
            - type (str): The user's type
            - teams (List[Dict]): List of teams with id, type, and summary
            - contact_methods (List[Dict]): List of contact methods with id, type, and summary
            - notification_rules (List[Dict]): List of notification rules with id, type

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_user = {}

    # Simple fields
    simple_fields = [
        "id",
        "name",
        "email",
        "description",
        "type",
    ]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_user[field] = value

    # Parse teams
    teams = result.get("teams", [])
    if teams:
        parsed_teams = []
        for team in teams:
            if not team:
                continue

            parsed_team = {}
            for field in ["id", "type", "summary"]:
                value = team.get(field)
                if value is not None:
                    parsed_team[field] = value

            if parsed_team:  # Only add if we have fields
                parsed_teams.append(parsed_team)

        if parsed_teams:
            parsed_user["teams"] = parsed_teams

    # Parse contact methods
    contact_methods = result.get("contact_methods", [])
    if contact_methods:
        parsed_methods = []
        for method in contact_methods:
            if not method:
                continue

            parsed_method = {}
            for field in ["id", "type", "summary"]:
                value = method.get(field)
                if value is not None:
                    parsed_method[field] = value

            if parsed_method:  # Only add if we have fields
                parsed_methods.append(parsed_method)

        if parsed_methods:
            parsed_user["contact_methods"] = parsed_methods

    # Parse notification rules
    notification_rules = result.get("notification_rules", [])
    if notification_rules:
        parsed_rules = []
        for rule in notification_rules:
            if not rule:
                continue

            parsed_rule = {}
            for field in ["id", "type"]:
                value = rule.get(field)
                if value is not None:
                    parsed_rule[field] = value

            if parsed_rule:  # Only add if we have fields
                parsed_rules.append(parsed_rule)

        if parsed_rules:
            parsed_user["notification_rules"] = parsed_rules

    return parsed_user

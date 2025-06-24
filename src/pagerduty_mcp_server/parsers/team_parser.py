"""Parser for PagerDuty teams."""

from typing import Any, Dict


def parse_team(*, result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw team API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw team API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The team ID
            - name (str): The team name
            - description (str): The team description
            - parent (Dict): Parent team information if this is a sub-team, containing:
                - id (str): Parent team ID
                - type (str): Parent team type

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.
        The parent field will be None if the team is not a sub-team.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_team = {}

    # Simple fields
    simple_fields = ["id", "name", "description"]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_team[field] = value

    # Parse parent team
    parent = result.get("parent")
    if parent and parent.get("id"):
        parsed_parent = {}

        # Add parent fields
        for field in ["id", "type"]:
            value = parent.get(field)
            if value is not None:
                parsed_parent[field] = value

        if parsed_parent:  # Only add if we have fields
            parsed_team["parent"] = parsed_parent

    return parsed_team

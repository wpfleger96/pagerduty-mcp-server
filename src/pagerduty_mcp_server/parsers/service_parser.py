"""Parser for PagerDuty services."""

from typing import Any, Dict


def parse_service(*, result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw service API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw service API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The service ID
            - name (str): The service name
            - description (str): The service description
            - status (str): Current status of the service
            - created_at (str): Creation timestamp
            - updated_at (str): Last update timestamp
            - teams (List[Dict]): List of teams with id and summary
            - integrations (List[Dict]): List of integrations with id and summary

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_service = {}

    # Simple fields
    simple_fields = ["id", "name", "description", "status", "created_at", "updated_at"]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_service[field] = value

    # Parse teams
    teams = result.get("teams", [])
    if teams:
        parsed_teams = []
        for team in teams:
            if not team:
                continue

            team_id = team.get("id")
            if team_id:
                parsed_team = {"id": team_id}
                if team.get("summary"):
                    parsed_team["summary"] = team.get("summary")
                parsed_teams.append(parsed_team)

        if parsed_teams:
            parsed_service["teams"] = parsed_teams

    # Parse integrations
    integrations = result.get("integrations", [])
    if integrations:
        parsed_integrations = []
        for integration in integrations:
            if not integration:
                continue

            integration_id = integration.get("id")
            if integration_id:
                parsed_integration = {"id": integration_id}
                if integration.get("summary"):
                    parsed_integration["summary"] = integration.get("summary")
                parsed_integrations.append(parsed_integration)

        if parsed_integrations:
            parsed_service["integrations"] = parsed_integrations

    return parsed_service

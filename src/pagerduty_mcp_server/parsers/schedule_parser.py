"""Parser for PagerDuty schedules."""

from typing import Any, Dict


def parse_schedule(*, result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw schedule API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw schedule API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The schedule ID
            - name (str): The schedule name
            - summary (str): The schedule summary
            - description (str): The schedule description
            - time_zone (str): The schedule's time zone
            - escalation_policies (List[Dict]): List of escalation policies with id, summary
            - teams (List[Dict]): List of teams with id, summary
            - schedule_layers (List[Dict]): List of schedule layers, each containing:
                - id (str): Layer ID
                - name (str): Layer name
                - start (str): Start time
                - end (str): End time
                - users (List[Dict]): List of users with id, summary

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_schedule = {}

    # Simple fields
    simple_fields = ["id", "name", "summary", "description", "time_zone"]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_schedule[field] = value

    # Parse escalation policies
    escalation_policies = result.get("escalation_policies", [])
    if escalation_policies:
        parsed_policies = []
        for policy in escalation_policies:
            if not policy.get("id"):
                continue

            parsed_policy = {"id": policy.get("id")}
            if policy.get("summary"):
                parsed_policy["summary"] = policy.get("summary")
            parsed_policies.append(parsed_policy)

        if parsed_policies:
            parsed_schedule["escalation_policies"] = parsed_policies

    # Parse teams
    teams = result.get("teams", [])
    if teams:
        parsed_teams = []
        for team in teams:
            if not team.get("id"):
                continue

            parsed_team = {"id": team.get("id")}
            if team.get("summary"):
                parsed_team["summary"] = team.get("summary")
            parsed_teams.append(parsed_team)

        if parsed_teams:
            parsed_schedule["teams"] = parsed_teams

    # Parse schedule layers
    schedule_layers = result.get("schedule_layers", [])
    if schedule_layers:
        parsed_layers = []
        for layer in schedule_layers:
            if not layer:
                continue

            parsed_layer = {}

            # Add simple layer fields
            for field in ["id", "name", "start", "end"]:
                value = layer.get(field)
                if value is not None:
                    parsed_layer[field] = value

            # Parse users
            users = layer.get("users", [])
            if users:
                parsed_users = []
                for user_entry in users:
                    user_data = user_entry.get("user", {})
                    user_id = user_data.get("id")
                    if user_id:
                        parsed_user = {"id": user_id}
                        if user_data.get("summary"):
                            parsed_user["summary"] = user_data.get("summary")
                        parsed_users.append(parsed_user)

                if parsed_users:
                    parsed_layer["users"] = parsed_users

            if parsed_layer:  # Only add non-empty layers
                parsed_layers.append(parsed_layer)

        if parsed_layers:
            parsed_schedule["schedule_layers"] = parsed_layers

    return parsed_schedule

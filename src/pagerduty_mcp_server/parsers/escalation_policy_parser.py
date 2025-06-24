"""Parser for PagerDuty escalation policies."""

from typing import Any, Dict


def parse_escalation_policy(*, result: Dict[str, Any]) -> Dict[str, Any]:
    """Parses a raw escalation policy API response into a structured format without unneeded fields.

    Args:
        result (Dict[str, Any]): The raw escalation policy API response

    Returns:
        Dict[str, Any]: A dictionary containing:
            - id (str): The policy ID
            - name (str): The policy name
            - escalation_rules (List[Dict]): List of escalation rules, each containing:
                - id (str): Rule ID
                - escalation_delay_in_minutes (int): Delay before escalation
                - targets (List[Dict]): List of targets with id, type, and summary
            - services (List[Dict]): List of services with id
            - teams (List[Dict]): List of teams with id and summary
            - description (str): Policy description

    Note:
        If the input is None or not a dictionary, returns an empty dictionary.
        All fields are optional and will be None if not present in the input.

    Raises:
        KeyError: If accessing nested dictionary fields fails
    """

    if not result:
        return {}

    parsed_policy = {}

    # Simple fields
    simple_fields = ["id", "name", "description"]
    for field in simple_fields:
        value = result.get(field)
        if value is not None:
            parsed_policy[field] = value

    # Parse escalation rules
    escalation_rules = result.get("escalation_rules", [])
    if escalation_rules:
        parsed_rules = []
        for rule in escalation_rules:
            if not rule:
                continue

            parsed_rule = {}

            # Add rule fields
            for field in ["id", "escalation_delay_in_minutes"]:
                value = rule.get(field)
                if value is not None:
                    parsed_rule[field] = value

            # Parse targets
            targets = rule.get("targets", [])
            if targets:
                parsed_targets = []
                for target in targets:
                    if not target:
                        continue

                    target_id = target.get("id")
                    if target_id:
                        parsed_target = {"id": target_id}

                        # Include type and summary if available
                        target_type = target.get("type")
                        if target_type:
                            parsed_target["type"] = target_type

                        target_summary = target.get("summary")
                        if target_summary:
                            parsed_target["summary"] = target_summary

                        parsed_targets.append(parsed_target)

                if parsed_targets:
                    parsed_rule["targets"] = parsed_targets

            if parsed_rule:  # Only add non-empty rules
                parsed_rules.append(parsed_rule)

        if parsed_rules:
            parsed_policy["escalation_rules"] = parsed_rules

    # Parse services
    services = result.get("services", [])
    if services:
        parsed_services = []
        for service in services:
            if not service:
                continue

            service_id = service.get("id")
            if service_id:
                parsed_services.append({"id": service_id})

        if parsed_services:
            parsed_policy["services"] = parsed_services

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

                # Include summary if available
                team_summary = team.get("summary")
                if team_summary:
                    parsed_team["summary"] = team_summary

                parsed_teams.append(parsed_team)

        if parsed_teams:
            parsed_policy["teams"] = parsed_teams

    return parsed_policy

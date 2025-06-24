"""Parsers for PagerDuty resources.

This module provides standardized parsers for all PagerDuty API responses.
Each parser transforms raw API responses into a consistent format by:
- Removing unnecessary fields
- Standardizing field names and types
- Handling missing or null values
- Providing type hints for all fields

Available parsers:
- parse_incident: Parses incident responses
- parse_oncall: Parses on-call assignment responses
- parse_schedule: Parses schedule responses
- parse_service: Parses service responses
- parse_team: Parses team responses
- parse_user: Parses user responses
- parse_escalation_policy: Parses escalation policy responses

All parsers return a Dict[str, Any] with consistent structure and optional fields.
"""

from .escalation_policy_parser import parse_escalation_policy
from .incident_parser import parse_incident
from .oncall_parser import parse_oncall
from .schedule_parser import parse_schedule
from .service_parser import parse_service
from .team_parser import parse_team
from .user_parser import parse_user

__all__ = [
    "parse_escalation_policy",
    "parse_incident",
    "parse_oncall",
    "parse_schedule",
    "parse_service",
    "parse_team",
    "parse_user",
]

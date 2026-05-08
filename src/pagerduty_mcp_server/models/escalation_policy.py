"""Pydantic models for PagerDuty Escalation Policies."""

from typing import List, Optional

from pydantic import Field

from .common import IdOnly, PagerDutyBaseModel, Reference, TypedReference


class EscalationRuleTarget(TypedReference):
    """A target in an escalation rule.

    Inherits from TypedReference which includes 'type' field for target identification.
    Additional API fields are documented in the base class.
    """


class EscalationRule(PagerDutyBaseModel):
    """An escalation rule within a policy.

    Contains the essential escalation rule configuration needed for MCP responses.
    Additional API fields are intentionally excluded for response optimization.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str
    escalation_delay_in_minutes: int

    # Collections - present but can be empty
    targets: List[EscalationRuleTarget] = []

    # API fields excluded from MCP responses for size optimization:
    # Note: Currently no additional fields are excluded at the escalation rule level,
    # but this pattern is established for consistency and future API changes


class EscalationPolicy(PagerDutyBaseModel):
    """A Pydantic model for a PagerDuty Escalation Policy.

    Contains all fields available in the PagerDuty API response.
    Fields marked as excluded are intentionally omitted from MCP responses
    to optimize response size while maintaining clarity about available data.
    """

    # Essential fields for MCP responses - always present in PagerDuty API responses
    id: str
    name: str

    # Optional fields included in MCP responses
    description: Optional[str] = None

    # Collections - present but can be empty
    escalation_rules: List[EscalationRule] = []
    services: List[IdOnly] = []
    teams: List[Reference] = []

    # API fields excluded from MCP responses for size optimization:
    # These fields are available in the PagerDuty API but excluded to reduce response size
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: Always 'escalation_policy'"
    )
    summary: Optional[str] = Field(
        None, exclude=True, description="Excluded: Usually same as name"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )
    num_loops: Optional[int] = Field(
        None, exclude=True, description="Excluded: Number of escalation loops"
    )
    on_call_handoff_notifications: Optional[str] = Field(
        None, exclude=True, description="Excluded: Handoff notification setting"
    )
    privilege: Optional[str] = Field(
        None, exclude=True, description="Excluded: Permission level (usually null)"
    )

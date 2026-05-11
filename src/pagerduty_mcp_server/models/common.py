"""Common Pydantic models for PagerDuty resources."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PagerDutyBaseModel(BaseModel):
    """Base model for all PagerDuty resources with clean serialization."""

    model_config = ConfigDict(
        use_enum_values=True,
    )

    def to_clean_dict(
        self, include_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Serialize to dictionary with empty fields excluded, optionally filtering to specific fields.

        Args:
            include_fields: Optional list of field names to include. If provided, only these fields
                           will be included in the output. If None, all fields are included.

        Returns:
            Dict with None values and empty collections omitted, optionally filtered to specific fields.
        """
        # Get the full clean dict first
        full_dict = self.model_dump(
            by_alias=True, exclude_none=True, exclude_defaults=True, exclude_unset=True
        )

        # If no include_fields specified, return the full dict
        if include_fields is None:
            return full_dict

        # Filter to only the requested fields
        filtered_dict = {}
        for field in include_fields:
            if field in full_dict:
                filtered_dict[field] = full_dict[field]

        return filtered_dict


class Reference(PagerDutyBaseModel):
    """A base model for a reference to another PagerDuty object (e.g., a Team).

    Contains only the essential fields needed for MCP responses.
    Additional API fields like 'type', 'self', 'html_url' are intentionally excluded
    to optimize response size but are documented below for reference.
    """

    # Essential fields for MCP responses
    id: str
    summary: Optional[str] = None

    # API fields excluded from MCP responses for size optimization:
    # - type: str (e.g., "user_reference", "team_reference")
    # - self: str (API URL for this resource)
    # - html_url: str (Web UI URL for this resource)
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: API resource type"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )


class TypedReference(Reference):
    """A reference that also includes a 'type' field (e.g., a Target).

    Unlike the base Reference class, this includes the 'type' field in responses
    as it's often essential for understanding the target type in escalation rules.
    """

    # Override to include type in responses for this specific use case
    type: Optional[str] = Field(
        None, exclude=False, description="Included: Type of referenced resource"
    )


class IdOnly(PagerDutyBaseModel):
    """A model for a reference that only contains an ID (e.g., a Service).

    Contains only the essential ID field needed for MCP responses.
    Additional API fields are intentionally excluded to optimize response size.
    """

    # Essential field for MCP responses
    id: str

    # API fields excluded from MCP responses for size optimization:
    # - type: str (e.g., "service_reference")
    # - summary: str (Human-readable name)
    # - self: str (API URL for this resource)
    # - html_url: str (Web UI URL for this resource)
    type: Optional[str] = Field(
        None, exclude=True, description="Excluded: API resource type"
    )
    summary: Optional[str] = Field(
        None, exclude=True, description="Excluded: Human-readable name"
    )
    self: Optional[str] = Field(None, exclude=True, description="Excluded: API URL")
    html_url: Optional[str] = Field(
        None, exclude=True, description="Excluded: Web UI URL"
    )

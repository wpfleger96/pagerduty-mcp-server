import difflib
import functools
import logging
from typing import List, Optional, Type

from .models.common import PagerDutyBaseModel

logger = logging.getLogger(__name__)


def validate_include_parameter(
    model_class: Type[PagerDutyBaseModel],
    extra_fields: Optional[List[str]] = None,
):
    """Decorator to validate that a list of 'include' fields is valid for a given model.

    Args:
        model_class (Type[PagerDutyBaseModel]): The model class to validate against
        extra_fields (Optional[List[str]]): Additional virtual fields not on the model (e.g. notes, past_incidents)
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            include = kwargs.get("include")
            if include is not None:
                kwargs["include"] = validate_include_fields(
                    include, model_class, extra_fields=extra_fields
                )
            return await func(*args, **kwargs)

        return async_wrapper

    return decorator


def validate_include_fields(
    include: Optional[List[str]],
    model_class: Type[PagerDutyBaseModel],
    extra_fields: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """Validate that a list of fields is valid for a given model.

    Args:
        include (List[str]): The list of fields to validate
        model_class (Type[PagerDutyBaseModel]): The model class to validate against
        extra_fields (Optional[List[str]]): Additional virtual fields not on the model (e.g. notes, past_incidents)
    """
    if include is None:
        return None

    all_fields = set(model_class.model_fields.keys())

    try:
        schema = model_class.model_json_schema()
        schema_fields = set(schema.get("properties", {}).keys())
        valid_fields = all_fields | schema_fields
    except Exception as e:
        raise RuntimeError(
            f"Cannot determine valid fields for {model_class.__name__}: {e}"
        ) from e

    if extra_fields:
        valid_fields = valid_fields | set(extra_fields)

    invalid_fields = set(include) - set(valid_fields)

    if invalid_fields:
        invalid_list = sorted(invalid_fields)
        suggestions = []

        for invalid_field in invalid_list:
            matches = difflib.get_close_matches(
                invalid_field, valid_fields, n=2, cutoff=0.6
            )
            if matches:
                suggestions.append(f"'{invalid_field}' -> {matches}")

        error_parts = [f"Invalid include fields: {invalid_list}"]

        if suggestions:
            error_parts.append(f"Did you mean: {'; '.join(suggestions)}")

        error_parts.append(
            "See `docs://tools` for more information on the `include` parameter."
        )
        raise ValueError("\n".join(error_parts))

    return include

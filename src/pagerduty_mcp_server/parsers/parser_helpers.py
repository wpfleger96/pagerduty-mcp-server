"""Helper functions for parsing PagerDuty API responses."""

from typing import Any, Callable, Dict, List, Optional


def parse_sub_dictionary(
    data: Optional[Dict[str, Any]], keys: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Parses a sub-dictionary, including only specified keys with non-None values.

    Args:
        data: The input dictionary to parse.
        keys: A list of keys to include in the parsed dictionary.

    Returns:
        A new dictionary containing only the specified keys that had non-None values,
        or None if the input data is None/not a dict or the resulting dict is empty.
    """
    if not data or not isinstance(data, dict):
        return None

    parsed_dict = {}
    for key in keys:
        value = data.get(key)
        if value is not None:
            parsed_dict[key] = value
    return parsed_dict if parsed_dict else None


def parse_complex_item(
    item_data: Optional[Dict[str, Any]], principal_key: str, fields: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Parses a complex item, typically an object with a nested principal object (e.g., assignee, acknowledger)
    and an 'at' timestamp.

    Args:
        item_data: The dictionary representing the item.
        principal_key: The key for the nested principal object (e.g., "assignee", "acknowledger").
        fields: The fields to extract from the principal object (e.g., ["id", "summary"]).

    Returns:
        A parsed dictionary for the item, or None if the item_data is None/not a dict
        or the resulting item is empty.
    """
    if not item_data or not isinstance(item_data, dict):
        return None

    current_item = {}
    principal_obj_data = item_data.get(principal_key)
    # Parse the nested principal object, keeping the specified fields
    parsed_principal_obj = parse_sub_dictionary(principal_obj_data, fields)
    if parsed_principal_obj:
        current_item[principal_key] = parsed_principal_obj

    at_timestamp = item_data.get("at")
    if at_timestamp is not None:
        current_item["at"] = at_timestamp

    return current_item if current_item else None


def parse_list_of_items(
    raw_list: Optional[List[Dict[str, Any]]],
    item_parser_func: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]],
) -> Optional[List[Dict[str, Any]]]:
    """
    Parses a list of dictionary items using a provided item parser function.

    Args:
        raw_list: The list of raw dictionary items.
        item_parser_func: A callable that takes a raw item dictionary and returns
                          a parsed item dictionary or None.

    Returns:
        A list of parsed items, or None if the raw_list is None/not a list
        or the resulting list is empty.
    """
    if not raw_list or not isinstance(raw_list, list):
        return None

    processed_list = []
    for item_data in raw_list:
        parsed_item = item_parser_func(item_data)
        if parsed_item:
            processed_list.append(parsed_item)
    return processed_list if processed_list else None

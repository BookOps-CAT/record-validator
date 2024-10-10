"""This module contains functions that are used in the record_validator package to
validate data"""

from itertools import chain
from typing import Any, Dict, List, Union
from pymarc import Leader
from pymarc import Field as MarcField
from pydantic import ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails
from record_validator.adapters import get_adapter
from record_validator.utils import (
    get_record_type,
    field2dict,
    dict2subfield,
)
from record_validator.constants import AllFields, ValidOrderItems


def validate_all(
    fields: List[Union[MarcField, Dict[str, Any]]]
) -> List[Union[MarcField, Dict[str, Any]]]:
    """
    Validate MARC record fields. This function validates validates the fields of a
    MARC record based on the record type. It first validates the existence of all
    required fields and identifies extra fields. It then validates the fields with
    an adapter that will identify the correct model for the field based on the
    record type. Finally, if the record is for a monograph, it validates the
    combination of order location, item location and item type. If any errors are
    found, a `ValidationError` is raised.

    Args:
        fields: A list of MARC fields to validate.

    Returns:
        a list containing the validated fields

    Raises:
        ValidationError: If any errors are found during validation.

    """
    errors = []
    record_type = get_record_type(fields)
    errors.extend(validate_fields(fields, record_type=record_type))
    adapter = get_adapter(record_type)
    for field in fields:
        try:
            adapter.validate_python(field, from_attributes=True)
        except ValidationError as e:
            errors.extend(e.errors())  # type: ignore
    error_locs = [str(i["loc"][-1]) for i in errors if "loc" in i]
    if "monograph" in record_type:
        errors.extend(validate_order_items(fields, error_locs))
    if len(errors) > 0:
        raise ValidationError.from_exception_data(
            title=fields.__class__.__name__, line_errors=errors
        )
    else:
        return fields


def validate_fields(
    fields: List[Union[MarcField, Dict[str, Any]]], record_type: str
) -> List[InitErrorDetails]:
    """Validate the existence of all required fields and identify extra fields."""
    tag_list = [next(iter(field2dict(i))) for i in fields]
    required_tags = AllFields.required_fields()
    extra_tags = []
    if record_type == "auxam_other":
        extra_tags.append("949")
    elif "other" in record_type:
        extra_tags.extend(AllFields.monograph_fields())
    elif "monograph" in record_type:
        required_tags.extend(AllFields.monograph_fields())
    extra_fields = [i for i in extra_tags if i in tag_list]
    missing_fields = [i for i in required_tags if i not in tag_list]
    repeated_fields = [
        i for i in AllFields.non_repeatable_fields() if tag_list.count(i) > 1
    ]
    extra_field_errors = [
        InitErrorDetails(
            type=PydanticCustomError("extra_forbidden", f"Extra field: {tag}"),
            input=tag,
        )
        for tag in extra_fields + repeated_fields
    ]
    missing_field_errors = [
        InitErrorDetails(
            type=PydanticCustomError("missing", f"Field required: {tag}"), input=tag
        )
        for tag in missing_fields
    ]
    return extra_field_errors + missing_field_errors


def validate_leader(input: Union[str, Leader]) -> str:
    """Validate the leader"""
    return str(input)


def validate_order_items(
    fields: List[Union[MarcField, Dict[str, Any]]], error_locs: List[str]
) -> List[InitErrorDetails]:
    """Validate the combination of order location, item location and item type."""
    field_list = [field2dict(i) for i in fields]
    tag_list = [next(iter(i)) for i in field_list]
    if (
        any(i not in tag_list for i in ["960", "949"])
        or any(tag_list.count(i) > 1 for i in AllFields.non_repeatable_fields())
        or any(
            i in error_locs for i in ["item_location", "item_type", "order_location"]
        )
    ):
        return []
    errors = []
    order_locs = [dict2subfield(i, "t") for i in field_list if "960" in i]
    item_locs = [dict2subfield(i, "l") for i in field_list if "949" in i]
    item_types = [dict2subfield(i, "t") for i in field_list if "949" in i]
    assert len(order_locs) == 1, f"Expected 1 order location, got {len(order_locs)}"
    order_items = [
        {
            "order_location": list(chain(*order_locs))[0],
            "item_location": il,
            "item_type": it,
        }
        for il, it in zip(list(chain(*item_locs)), list(chain(*item_types)))
    ]
    invalid_combos = [i for i in order_items if i not in ValidOrderItems.to_list()]
    error_msg = "Invalid combination of item_type, order_location and item_location"

    for order_item in invalid_combos:
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError(
                    "order_item_mismatch", f"{error_msg}: {order_item}"
                ),
                input=order_item,
            )
        )
    return errors

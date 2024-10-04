from typing import Any, Dict, List, Union
from pymarc import Field as MarcField
from pymarc import Leader
from pydantic import ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails
from record_validator.adapters import get_adapter
from record_validator.constants import AllFields, ValidOrderItems


def validate_all(fields: list) -> list:
    """Validate MARC record fields."""
    errors = []
    tags = get_tag_list(fields)
    record_type, adapter = get_adapter(fields)
    errors.extend(validate_fields(tags, record_type=record_type))
    for field in fields:
        try:
            adapter.validate_python(field, from_attributes=True)
        except ValidationError as e:
            errors.extend(e.errors())

    if "monograph" in record_type and "960" in tags and "949" in tags:
        error_locs = [i["loc"][-1] for i in errors if "loc" in i and len(i["loc"]) > 1]
        if not any(
            [
                i
                for i in ["item_location", "item_type", "order_location"]
                if i in error_locs
            ]
        ):
            errors.extend(validate_order_items(fields))

    if len(errors) > 0:
        raise ValidationError.from_exception_data(
            title=fields.__class__.__name__, line_errors=errors
        )
    else:
        return fields


def validate_fields(tag_list: list, record_type: str) -> list:
    match record_type.lower():
        case "evp_other" | "leila_other":
            extra_tags = AllFields.monograph_fields()
            required_tags = AllFields.required_fields()
        case "auxam_other":
            extra_tags = ["949"]
            required_tags = AllFields.required_fields()
        case record_type if "other" in record_type:
            extra_tags = AllFields.monograph_fields()
            required_tags = AllFields.required_fields()
        case record_type if "monograph" in record_type:
            extra_tags = []
            required_tags = AllFields.required_fields() + AllFields.monograph_fields()
        case _:
            extra_tags = []
            required_tags = AllFields.required_fields()
    extra_fields = [i for i in extra_tags if i in tag_list]
    missing_fields = [i for i in required_tags if i not in tag_list]
    extra_field_errors = [
        InitErrorDetails(
            type=PydanticCustomError("extra_forbidden", f"Extra field: {tag}"),
            input=tag,
        )
        for tag in extra_fields
    ]
    missing_field_errors = [
        InitErrorDetails(
            type=PydanticCustomError("missing", f"Field required: {tag}"), input=tag
        )
        for tag in missing_fields
    ]
    return extra_field_errors + missing_field_errors


def validate_leader(input: Union[str, Leader]) -> str:
    """Validate the leader."""
    return str(input)


def validate_order_items(fields: List[Union[MarcField, Dict[str, Any]]]) -> list:
    error_msg = "Invalid combination of item_type, order_location and item_location"
    errors = []
    order_items = get_order_item_list(fields)
    invalid_order_items = [i for i in order_items if i not in ValidOrderItems.to_list()]

    for order_item in invalid_order_items:
        errors.append(
            InitErrorDetails(
                type=PydanticCustomError(
                    "order_item_mismatch", f"{error_msg}: {order_item}"
                ),
                input=order_item,
            )
        )
    return errors

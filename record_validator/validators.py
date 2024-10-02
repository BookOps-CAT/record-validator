from typing import Any, Dict, List, Union
from pymarc import Field as MarcField
from pymarc import Leader
from pydantic import ValidationError
from pydantic_core import PydanticCustomError, InitErrorDetails
from record_validator.adapters import get_adapter
from record_validator.constants import AllFields, ValidOrderItems
from record_validator.utils import get_subfield_from_code


def get_extra_fields(tag_list: list, material_type: str) -> List[str]:
    if material_type == "monograph":
        return []
    monograph_fields = AllFields.monograph_fields()
    return [i for i in monograph_fields if i in tag_list]


def get_missing_fields(tag_list: list, material_type: str) -> List[str]:
    if material_type == "monograph":
        required_fields = AllFields.monograph_fields() + AllFields.required_fields()
    else:
        required_fields = AllFields.required_fields()
    return [i for i in required_fields if i not in tag_list]


def get_order_item_list(
    fields: List[Union[MarcField, Dict[str, Any]]]
) -> List[Dict[str, Union[str, None]]]:
    order_locations: List[Union[str, None]] = []
    item_locations: List[Union[str, None]] = []
    item_types: List[Union[str, None]] = []
    for field in fields:
        if (isinstance(field, MarcField) and field.tag == "960") or (
            isinstance(field, dict)
            and ("960" in field or ("tag" in field and field["tag"] == "960"))
        ):
            order_locations.extend(
                get_subfield_from_code(field=field, code="t", tag="960")
            )
        elif (isinstance(field, MarcField) and field.tag == "949") or (
            isinstance(field, dict)
            and ("949" in field or ("tag" in field and field["tag"] == "949"))
        ):
            item_locations.extend(
                get_subfield_from_code(field=field, code="l", tag="949")
            )
            item_types.extend(get_subfield_from_code(field=field, code="t", tag="949"))
    order_count = len(order_locations)
    assert order_count == 1, f"Expected 1 order location, got {order_count}"
    result = [
        {"order_location": order_locations[0], "item_location": il, "item_type": it}
        for il, it in zip(item_locations, item_types)
    ]
    return result


def get_tag_list(fields: list) -> list:
    all_fields = []
    if all(isinstance(i, dict) for i in fields):
        all_fields.extend([key for i in fields for key in i.keys()])
    elif all(isinstance(i, MarcField) for i in fields):
        all_fields.extend([i.tag for i in fields])
    return all_fields


def validate_field_list(tag_list: list, material_type: str) -> list:
    extra_fields = [
        InitErrorDetails(
            type=PydanticCustomError("extra_forbidden", f"Extra field: {tag}"),
            input=tag,
        )
        for tag in get_extra_fields(tag_list, material_type)
    ]
    missing_fields = [
        InitErrorDetails(
            type=PydanticCustomError("missing", f"Field required: {tag}"), input=tag
        )
        for tag in get_missing_fields(tag_list, material_type)
    ]
    return extra_fields + missing_fields


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

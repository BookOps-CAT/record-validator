from typing import Annotated, Any, Dict, List, Union
from pymarc import Field as MarcField
from pydantic import Discriminator, Tag, TypeAdapter
from pydantic_core import PydanticCustomError, ValidationError, InitErrorDetails
from record_validator.field_models import (
    BibCallNo,
    BibVendorCode,
    ControlField001,
    ControlField003,
    ControlField005,
    ControlField006,
    ControlField007,
    ControlField008,
    InvoiceField,
    ItemField,
    LCClass,
    LibraryField,
    OrderField,
    OtherDataField,
)


CONTROL_FIELDS = ["001", "003", "005", "006", "007", "008"]
REQUIRED_FIELDS = ["852", "901", "050", "910", "960", "980", "949"]
VALID_ORDER_ITEMS = [
    {"order_location": "MAB", "item_location": "rcmb2", "item_type": "2"},
    {"order_location": "MAS", "item_location": "rcmb2", "item_type": "2"},
    {"order_location": "MAF", "item_location": "rcmf2", "item_type": "55"},
    {"order_location": "MAF", "item_location": "rcmf2", "item_type": None},
    {"order_location": "MAG", "item_location": "rcmg2", "item_type": "55"},
    {"order_location": "MAG", "item_location": "rcmg2", "item_type": None},
    {"order_location": "MAL", "item_location": "rc2ma", "item_type": "55"},
    {"order_location": "MAL", "item_location": None, "item_type": "55"},
    {"order_location": "MAL", "item_location": "rc2ma", "item_type": None},
    {"order_location": "MAL", "item_location": None, "item_type": None},
    {"order_location": "MAP", "item_location": "rcmp2", "item_type": "2"},
    {"order_location": "PAH", "item_location": "rcph2", "item_type": "55"},
    {"order_location": "PAH", "item_location": "rcph2", "item_type": None},
    {"order_location": "PAM", "item_location": "rcpm2", "item_type": "55"},
    {"order_location": "PAM", "item_location": "rcpm2", "item_type": None},
    {"order_location": "PAT", "item_location": "rcpt2", "item_type": "55"},
    {"order_location": "PAT", "item_location": "rcpt2", "item_type": None},
    {"order_location": "SC", "item_location": "rc2cf", "item_type": "55"},
    {"order_location": "SC", "item_location": "rc2cf", "item_type": None},
]


def get_examples_from_schema(field: tuple) -> Union[List[str], None]:
    if len(field) == 2:
        model = field[0]
        model_field = field[1]
        by_alias = False
    elif field[0] == "fields" and field[2] == "subfields":
        model = field[1]
        model_field = f"subfields.{field[4]}"
        by_alias = True
    else:
        model = field[1]
        model_field = field[2]
        by_alias = False

    match model:
        case "001":
            schema = ControlField001.model_json_schema(by_alias=by_alias)
        case "003":
            schema = ControlField003.model_json_schema(by_alias=by_alias)
        case "005":
            schema = ControlField005.model_json_schema(by_alias=by_alias)
        case "006":
            schema = ControlField006.model_json_schema(by_alias=by_alias)
        case "007":
            schema = ControlField007.model_json_schema(by_alias=by_alias)
        case "008":
            schema = ControlField008.model_json_schema(by_alias=by_alias)
        case "050":
            schema = LCClass.model_json_schema(by_alias=by_alias)
        case "852":
            schema = BibCallNo.model_json_schema(by_alias=by_alias)
        case "980":
            schema = InvoiceField.model_json_schema(by_alias=by_alias)
        case "949":
            schema = ItemField.model_json_schema(by_alias=by_alias)

        case "960":
            schema = OrderField.model_json_schema(by_alias=by_alias)

        case _:
            return None
    return schema["properties"][model_field]["examples"]


def get_field_tag(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in REQUIRED_FIELDS or tag in CONTROL_FIELDS:
        return tag
    else:
        return "data_field"


def get_missing_field_list(fields: list) -> list:
    if all(isinstance(i, dict) for i in fields):
        all_fields = [key for i in fields for key in i.keys()]
    elif all(isinstance(i, MarcField) for i in fields):
        all_fields = [i.tag for i in fields]
    else:
        all_fields = []
    return [tag for tag in REQUIRED_FIELDS if tag not in all_fields]


def get_order_item_from_field(
    input: List[Union[MarcField, Dict[str, Any]]]
) -> List[Dict[str, Union[str, None]]]:
    order_locations = []
    item_locations = []
    item_types = []
    for field in input:
        if (isinstance(field, MarcField) and field.tag == "960") or (
            isinstance(field, dict)
            and ("960" in field or ("tag" in field and field["tag"] == "960"))
        ):
            order_locations.append(
                get_subfield_from_code(field=field, code="t", tag="960")
            )
        elif (isinstance(field, MarcField) and field.tag == "949") or (
            isinstance(field, dict)
            and ("949" in field or ("tag" in field and field["tag"] == "949"))
        ):
            item_locations.append(
                get_subfield_from_code(field=field, code="l", tag="949")
            )
            item_types.append(get_subfield_from_code(field=field, code="t", tag="949"))
    order_count = len(order_locations)
    assert order_count == 1, f"Expected 1 order location, got {order_count}"
    result = [
        {"order_location": order_locations[0], "item_location": il, "item_type": it}
        for il, it in zip(item_locations, item_types)
    ]
    return result


def get_subfield_from_code(
    field: Union[MarcField, dict],
    tag: str,
    code: str,
) -> Union[str, None]:
    if not isinstance(field, (MarcField, dict)):
        return None
    elif isinstance(field, MarcField):
        subfields = [i[1] for i in field.subfields if code == i[0]]
    else:
        all_subfields = (
            field.get("subfields") if "tag" in field else field[tag].get("subfields")
        )
        subfields = [i[code] for i in all_subfields if code in i.keys()]
    if subfields == []:
        return None
    assert len(subfields) == 1
    return subfields[0]


def validate_fields(self: list) -> list:
    validation_errors = []
    field_validation_errors = validate_field_values(self)
    validation_errors.extend(field_validation_errors)
    missing_fields = get_missing_field_list(self)
    for tag in missing_fields:
        validation_errors.append(
            InitErrorDetails(
                type=PydanticCustomError("missing", f"Field required: {tag}"),
                input=tag,
            )
        )
    if "949" in missing_fields or "960" in missing_fields:
        pass
    elif len(field_validation_errors) > 0 and any(
        loc in [i["loc"][-1] for i in field_validation_errors]
        for loc in ["item_location", "item_type", "order_location"]
    ):
        pass
    else:
        order_item_errors = validate_order_item_data(self)
        validation_errors.extend(order_item_errors)
    if len(validation_errors) > 0:
        raise ValidationError.from_exception_data(
            title=self.__class__.__name__, line_errors=validation_errors
        )
    else:
        return self


def validate_field_values(fields: list) -> list:
    validation_errors = []
    FieldAdapter: TypeAdapter = TypeAdapter(
        Annotated[
            Union[
                Annotated[BibCallNo, Tag("852")],
                Annotated[BibVendorCode, Tag("901")],
                Annotated[InvoiceField, Tag("980")],
                Annotated[ItemField, Tag("949")],
                Annotated[LCClass, Tag("050")],
                Annotated[LibraryField, Tag("910")],
                Annotated[OrderField, Tag("960")],
                Annotated[OtherDataField, Tag("data_field")],
                Annotated[ControlField001, Tag("001")],
                Annotated[ControlField003, Tag("003")],
                Annotated[ControlField005, Tag("005")],
                Annotated[ControlField006, Tag("006")],
                Annotated[ControlField007, Tag("007")],
                Annotated[ControlField008, Tag("008")],
            ],
            Discriminator(get_field_tag),
        ]
    )
    for field in fields:
        try:
            FieldAdapter.validate_python(field, from_attributes=True)
        except ValidationError as e:
            validation_errors.extend(e.errors())
    return validation_errors


def validate_order_item_data(self: List[Union[MarcField, Dict[str, Any]]]) -> list:
    error_msg = "Invalid combination of item_type, order_location and item_location"
    validation_errors = []
    order_item_list = get_order_item_from_field(self)
    for order_item in order_item_list:
        if order_item not in VALID_ORDER_ITEMS:
            validation_errors.append(
                InitErrorDetails(
                    type=PydanticCustomError(
                        "order_item_mismatch",
                        f"{error_msg}: {order_item}",
                    ),
                    input=order_item,
                )
            )
    return validation_errors

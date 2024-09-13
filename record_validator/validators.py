from typing import Annotated, Any, Dict, List, Union
from pydantic import Discriminator, Field, Tag, TypeAdapter
from pydantic_core import PydanticCustomError, ValidationError, InitErrorDetails
from pymarc import Field as MarcField
from record_validator.field_models import (
    BibCallNo,
    BibVendorCode,
    ControlField,
    InvoiceField,
    ItemField,
    LCClass,
    LibraryField,
    OrderField,
    OtherDataField,
)
from record_validator.order_item_models import (
    MABMASOrderItem,
    MAFOrderItem,
    MAGOrderItem,
    MALOrderItem,
    MAPOrderItem,
    PAHOrderItem,
    PAMOrderItem,
    PATOrderItem,
    SCOrderItem,
)
from record_validator.parsers import (
    get_field_tag,
    get_missing_field_list,
    order_item_from_field,
)

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
            Annotated[ControlField, Tag("control_field")],
        ],
        Discriminator(get_field_tag),
    ]
)
OrderItemAdapter: TypeAdapter = TypeAdapter(
    Annotated[
        Union[
            MABMASOrderItem,
            MAFOrderItem,
            MAGOrderItem,
            MALOrderItem,
            MAPOrderItem,
            PAHOrderItem,
            PAMOrderItem,
            PATOrderItem,
            SCOrderItem,
        ],
        Field(discriminator="order_location"),
    ]
)


def validate_fields(self: list) -> list:
    validation_errors = []
    field_validation_errors = validate_field_values(self)
    validation_errors.extend(field_validation_errors)
    missing_fields = get_missing_field_list(self)
    for tag in missing_fields:
        validation_errors.append(
            InitErrorDetails(
                type=PydanticCustomError(
                    "missing_required_field", f"Field required: {tag}"
                ),
                input=tag,
            )
        )
    if "949" in missing_fields or "960" in missing_fields:
        pass
    elif len(validation_errors) == 0:
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
    for field in fields:
        try:
            FieldAdapter.validate_python(field, from_attributes=True)
        except ValidationError as e:
            validation_errors.extend(e.errors())
    return validation_errors


def validate_order_item_data(self: List[Union[MarcField, Dict[str, Any]]]) -> list:
    validation_errors = []
    order_item_list = order_item_from_field(self)
    for order_item in order_item_list:
        try:
            OrderItemAdapter.validate_python(order_item, from_attributes=True)
        except ValidationError as e:
            validation_errors.extend(e.errors())
    return validation_errors

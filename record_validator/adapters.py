from typing import Annotated, Union
from pydantic import Tag, Discriminator, TypeAdapter
from pymarc import Field as MarcField
from record_validator.constants import AllFields
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
    MonographOtherField,
    OrderField,
    OtherDataField,
)


def get_monograph_tag(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in AllFields:
        return tag
    else:
        return "data_field"


def get_other_tag(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in AllFields.monograph_fields():
        return "data_field"
    elif tag in AllFields and tag not in AllFields.monograph_fields():
        return tag
    else:
        return "data_field"


MonographRecordAdapter: TypeAdapter = TypeAdapter(
    Annotated[
        Union[
            Annotated[BibCallNo, Tag("852")],
            Annotated[BibVendorCode, Tag("901")],
            Annotated[InvoiceField, Tag("980")],
            Annotated[ItemField, Tag("949")],
            Annotated[LCClass, Tag("050")],
            Annotated[LibraryField, Tag("910")],
            Annotated[OrderField, Tag("960")],
            Annotated[MonographOtherField, Tag("data_field")],
            Annotated[ControlField001, Tag("001")],
            Annotated[ControlField003, Tag("003")],
            Annotated[ControlField005, Tag("005")],
            Annotated[ControlField006, Tag("006")],
            Annotated[ControlField007, Tag("007")],
            Annotated[ControlField008, Tag("008")],
        ],
        Discriminator(get_monograph_tag),
    ]
)

OtherRecordAdapter: TypeAdapter = TypeAdapter(
    Annotated[
        Union[
            Annotated[BibVendorCode, Tag("901")],
            Annotated[InvoiceField, Tag("980")],
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
        Discriminator(get_other_tag),
    ]
)

FieldAdapter: TypeAdapter = TypeAdapter(
    Union[
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
        MonographOtherField,
        OrderField,
        OtherDataField,
    ]
)

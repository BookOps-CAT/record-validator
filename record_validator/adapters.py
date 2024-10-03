from typing import Annotated, Union
from pydantic import Tag, Discriminator, TypeAdapter
from pymarc import Field as MarcField
from record_validator.constants import AllFields
from record_validator.field_models import (
    AuxBibCallNo,
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
    MonographDataField,
    OrderField,
    OtherDataField,
)


def get_adapter(record_type: Union[str, None]) -> TypeAdapter:
    fields: tuple
    discriminator = True
    match record_type:
        case "auxam_other":
            fields = AuxOtherFields
        case "evp_other" | "leila_other" | "other":
            fields = OtherFields
        case None:
            fields = FieldList
            discriminator = False
        case _:
            fields = MonographFields
    if discriminator:
        return TypeAdapter(Annotated[Union[fields], Discriminator(tag_discriminator)])
    else:
        return TypeAdapter(Union[fields])


def tag_discriminator(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in [i.value for i in AllFields]:
        return tag
    else:
        return "data_field"


AuxOtherFields = (
    Annotated[ControlField001, Tag("001")],
    Annotated[ControlField003, Tag("003")],
    Annotated[ControlField005, Tag("005")],
    Annotated[ControlField006, Tag("006")],
    Annotated[ControlField007, Tag("007")],
    Annotated[ControlField008, Tag("008")],
    Annotated[LCClass, Tag("050")],
    Annotated[AuxBibCallNo, Tag("852")],
    Annotated[BibVendorCode, Tag("901")],
    Annotated[LibraryField, Tag("910")],
    Annotated[OtherDataField, Tag("949")],
    Annotated[OrderField, Tag("960")],
    Annotated[InvoiceField, Tag("980")],
    Annotated[OtherDataField, Tag("data_field")],
)

MonographFields = (
    Annotated[ControlField001, Tag("001")],
    Annotated[ControlField003, Tag("003")],
    Annotated[ControlField005, Tag("005")],
    Annotated[ControlField006, Tag("006")],
    Annotated[ControlField007, Tag("007")],
    Annotated[ControlField008, Tag("008")],
    Annotated[LCClass, Tag("050")],
    Annotated[BibCallNo, Tag("852")],
    Annotated[BibVendorCode, Tag("901")],
    Annotated[LibraryField, Tag("910")],
    Annotated[ItemField, Tag("949")],
    Annotated[OrderField, Tag("960")],
    Annotated[InvoiceField, Tag("980")],
    Annotated[MonographDataField, Tag("data_field")],
)
OtherFields = (
    Annotated[ControlField001, Tag("001")],
    Annotated[ControlField003, Tag("003")],
    Annotated[ControlField005, Tag("005")],
    Annotated[ControlField006, Tag("006")],
    Annotated[ControlField007, Tag("007")],
    Annotated[ControlField008, Tag("008")],
    Annotated[LCClass, Tag("050")],
    Annotated[OtherDataField, Tag("852")],
    Annotated[BibVendorCode, Tag("901")],
    Annotated[LibraryField, Tag("910")],
    Annotated[OtherDataField, Tag("949")],
    Annotated[OrderField, Tag("960")],
    Annotated[InvoiceField, Tag("980")],
    Annotated[OtherDataField, Tag("data_field")],
)

FieldList = (
    AuxBibCallNo,
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
    MonographDataField,
    OrderField,
    OtherDataField,
)

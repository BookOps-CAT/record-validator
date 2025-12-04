"""
This module contains functions and types that are used in the record_validator package
to identify the correct model to validate a field against.

Functions:
    get_adapter: Return a TypeAdapter for the correct model based on the material
        type and vendor.
    tag_discriminator: Get the tag of a field to use as a discriminator for the
        TypeAdapter.

Types:
    AuxOtherFields:
        A tuple containing models of fields that are valid in an Amalivre
        non-monograph record. The models are annotated with the MARC tag of the
        field or "data_field" for fields that do not need to be validated.
    MonographFields:
        A tuple containing models of fields that are valid in a monograph record.
        The models are annotated with the MARC tag of the field or "data_field" for
        fields that do not need to be validated
    OtherFields:
        A tuple containing models of fields that are valid in a non-monograph record
        for any vendors other than Amalivre. The models are annotated with the MARC
        tag of the field or "data_field" for fields that do not need to be validated.
    FieldList:
        A tuple of all possible fields that can be present in a record.

"""

from typing import Annotated, Union

from pydantic import Discriminator, Tag, TypeAdapter
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
    """
    Return a `TypeAdapter` for the correct model based on the material type and
    vendor. The `TypeAdapter` will contain a union of models for valid fields in
    the specified record type. Certain fields require slightly different models
    based on the vendor and/or material type.

    Args:
        record_type: string that combines the material type and vendor of the record.

    Returns:
        a TypeAdapter for the correct model based on the record_type.
    """
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
    """Get the tag of a field to use as a discriminator for the TypeAdapter."""
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

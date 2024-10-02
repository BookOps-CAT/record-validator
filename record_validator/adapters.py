import re
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
from record_validator.utils import get_subfield_from_code, get_vendor_code


def get_adapter(fields: list) -> tuple[str, TypeAdapter]:
    vendor = get_vendor_code(fields)
    vendor_code = vendor.lower() if vendor is not None else None
    material_type = get_record_type(fields=fields, vendor_code=vendor_code)
    match vendor_code, material_type:
        case "auxam", "other":
            return f"{vendor_code}_other", TypeAdapter(AuxOtherFields)
        case vendor_code, "other" if isinstance(vendor_code, str):
            return f"{vendor_code}_other", TypeAdapter(OtherFields)
        case vendor_code, "other" if not isinstance(vendor_code, str):
            return "other", TypeAdapter(OtherFields)
        case vendor_code, "monograph" if isinstance(vendor_code, str):
            return f"{vendor_code}_monograph", TypeAdapter(MonographFields)
        case _:
            return "monograph", TypeAdapter(MonographFields)


def get_record_type(fields: list, vendor_code: Union[str, None]) -> str:
    if not isinstance(fields, list) or not all(
        isinstance(i, (MarcField, dict)) for i in fields
    ):
        return "other"
    phys_desc: list = []
    for field in fields:
        tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
        if (
            tag.startswith("6")
            and pattern_match(get_subfield_from_code(field, tag, "v"), "catalogues")
            is True
        ):
            return "other"
        elif (
            tag == "852"
            and vendor_code in ["AUXAM", "auxam"]
            and pattern_match(get_subfield_from_code(field, tag, "h"), "aux_call_no")
            is True
        ):
            return "other"
        elif tag == "960" and get_subfield_from_code(field, tag, "t") == ["PAD"]:
            return "other"
        elif tag == "300":
            phys_desc.extend(get_subfield_from_code(field, tag, "a"))
        else:
            continue
    if pattern_match(phys_desc, "multivol") is True:
        return "other"
    elif pattern_match(phys_desc, "pamphlet") is True:
        return "other"
    else:
        return "monograph"


def pattern_match(subfield_list: list, pattern: str) -> bool:
    match pattern:
        case "multivol":
            regex = re.compile(r"^(\d+)( v\.| volumes)( :$| ;$|$| $)")
        case "pamphlet":
            regex = re.compile(r"^(\d|[0-4][0-9])( p\.| pages)( :$| ;$|$| $)")
        case "catalogues":
            regex = re.compile(r"^[cC]atalogue(s?) [rR]aisonn[eé](s?)")
        case "aux_call_no":
            regex = re.compile(r"^ReCAP 2[345]-$")
        case _:
            return False
    return any(i is not None for i in [regex.match(str(i)) for i in subfield_list])


def tag_discriminator(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in [i.value for i in AllFields]:
        return tag
    else:
        return "data_field"


AuxOtherFields = Annotated[
    Union[
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
    ],
    Discriminator(tag_discriminator),
]

MonographFields = Annotated[
    Union[
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
    ],
    Discriminator(tag_discriminator),
]

OtherFields = Annotated[
    Union[
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
    ],
    Discriminator(tag_discriminator),
]

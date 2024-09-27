import re
from collections import defaultdict
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


def get_material_type(fields: list) -> str:
    if not isinstance(fields, list) or not all(
        isinstance(i, (MarcField, dict)) for i in fields
    ):
        return "other"
    multivol_pattern = re.compile(r"^(\d+)( v\.| volumes)( :$| ;$|$| $)")
    pamphlet_pattern = re.compile(r"^(\d|[0-4][0-9])( p\.| pages)( :$| ;$|$| $)")
    catalogues_pattern = re.compile(r"^[cC]atalogue(s?) [rR]aisonn[eé](s?)")
    phys_desc = []
    for field in fields:
        tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
        if tag.startswith("00"):
            continue
        if isinstance(field, MarcField):
            subfields = field.subfields_as_dict()
        else:
            subfield_dict = defaultdict(list)
            for s in field[tag].get("subfields"):
                for k, v in s.items():
                    subfield_dict[k].append(v)

            subfields = dict(subfield_dict)
        if "v" in subfields.keys() and any(
            match is not None
            for match in [catalogues_pattern.match(i.strip()) for i in subfields["v"]]
        ):
            return "other"
        elif tag == "960" and "t" in subfields.keys() and subfields["t"] == ["PAD"]:
            return "other"
        elif tag == "300" and "a" in subfields.keys():
            phys_desc.extend(subfields["a"])
        else:
            continue
    if any(
        match is not None
        for match in [multivol_pattern.match(i.strip()) for i in phys_desc]
    ):
        return "other"
    elif any(
        match is not None
        for match in [pamphlet_pattern.match(i.strip()) for i in phys_desc]
    ):
        return "other"
    else:
        return "monograph"


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

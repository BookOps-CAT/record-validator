from typing import get_args
from pydantic import Tag, TypeAdapter
from pymarc import Field as MarcField
import pytest
from record_validator.adapters import (
    get_adapter,
    tag_discriminator,
    AuxOtherFields,
    MonographFields,
    OtherFields,
    FieldAdapter,
)
from record_validator.field_models import (
    AuxBibCallNo,
    MonographDataField,
    OtherDataField,
)


@pytest.mark.parametrize(
    "record_type, additional_fields",
    [
        ("auxam_monograph", ["BibCallNo", "MonographDataField", "ItemField"]),
        ("evp_monograph", ["BibCallNo", "MonographDataField", "ItemField"]),
        ("leila_monograph", ["BibCallNo", "MonographDataField", "ItemField"]),
        ("monograph", ["BibCallNo", "MonographDataField", "ItemField"]),
        ("auxam_other", ["AuxBibCallNo", "OtherDataField"]),
        ("evp_other", ["OtherDataField"]),
        ("leila_other", ["OtherDataField"]),
        ("other", ["OtherDataField"]),
    ],
)
def test_get_adapter(record_type, additional_fields):
    adapter = get_adapter(record_type)
    schema = adapter.json_schema(by_alias=True)
    base_fields = [
        "BibVendorCode",
        "ControlField001",
        "ControlField003",
        "ControlField005",
        "ControlField006",
        "ControlField007",
        "ControlField008",
        "InvoiceField",
        "LCClass",
        "LibraryField",
        "OrderField",
    ]
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == sorted(
        base_fields + additional_fields
    )


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("300", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("852", "852"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_tag_discriminator_from_dict(tag, expected):
    field = {tag: {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    assert tag_discriminator(field) == expected


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("300", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("852", "852"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_tag_discriminator_from_marc(stub_record, tag, expected):
    field = stub_record.get(tag)
    assert isinstance(field, MarcField)
    assert field.tag == tag
    assert tag_discriminator(field) == expected


def test_AuxOtherFields():
    aux_other_field_names = [get_args(i)[0] for i in AuxOtherFields]
    aux_other_tags = [get_args(i)[1] for i in AuxOtherFields]
    assert isinstance(AuxOtherFields, tuple)
    assert len(aux_other_field_names) == 14
    assert AuxBibCallNo in aux_other_field_names
    assert OtherDataField in aux_other_field_names
    assert MonographDataField not in aux_other_field_names
    assert len(aux_other_tags) == 14
    assert aux_other_tags == [
        Tag(i)
        for i in [
            "001",
            "003",
            "005",
            "006",
            "007",
            "008",
            "050",
            "852",
            "901",
            "910",
            "949",
            "960",
            "980",
            "data_field",
        ]
    ]


def test_MonographFields():
    mono_field_names = [get_args(i)[0] for i in MonographFields]
    mono_tags = [get_args(i)[1] for i in MonographFields]
    assert isinstance(MonographFields, tuple)
    assert len(mono_field_names) == 14
    assert AuxBibCallNo not in mono_field_names
    assert OtherDataField not in mono_field_names
    assert MonographDataField in mono_field_names
    assert len(mono_tags) == 14
    assert mono_tags == [
        Tag(i)
        for i in [
            "001",
            "003",
            "005",
            "006",
            "007",
            "008",
            "050",
            "852",
            "901",
            "910",
            "949",
            "960",
            "980",
            "data_field",
        ]
    ]


def test_OtherFields():
    other_field_names = [get_args(i)[0] for i in OtherFields]
    other_tags = [get_args(i)[1] for i in OtherFields]
    assert isinstance(OtherFields, tuple)
    assert len(other_field_names) == 14
    assert AuxBibCallNo not in other_field_names
    assert OtherDataField in other_field_names
    assert MonographDataField not in other_field_names
    assert len(other_tags) == 14
    assert other_tags == [
        Tag(i)
        for i in [
            "001",
            "003",
            "005",
            "006",
            "007",
            "008",
            "050",
            "852",
            "901",
            "910",
            "949",
            "960",
            "980",
            "data_field",
        ]
    ]


def test_FieldAdapter():
    schema = FieldAdapter.json_schema(by_alias=True)
    assert sorted([i for i in schema["$defs"].keys()]) == sorted(
        [
            "AuxBibCallNo",
            "BibCallNo",
            "BibVendorCode",
            "ControlField001",
            "ControlField003",
            "ControlField005",
            "ControlField006",
            "ControlField007",
            "ControlField008",
            "InvoiceField",
            "ItemField",
            "LCClass",
            "LibraryField",
            "MonographDataField",
            "OrderField",
            "OtherDataField",
        ]
    )

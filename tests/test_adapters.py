from typing import get_args
from pydantic import Discriminator, Tag
from pymarc import Field as MarcField
import pytest
from record_validator.adapters import (
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
    aux_other_args = get_args(AuxOtherFields)
    assert len(aux_other_args) == 2
    assert aux_other_args[1] == Discriminator(tag_discriminator)
    union_args = [get_args(i) for i in get_args(aux_other_args[0])]
    assert len(union_args) == 14
    assert (AuxBibCallNo, Tag("852")) in union_args
    assert (OtherDataField, Tag("data_field")) in union_args
    assert (OtherDataField, Tag("949")) in union_args


def test_MonographFields():
    monograph_args = get_args(MonographFields)
    assert len(monograph_args) == 2
    assert monograph_args[1] == Discriminator(tag_discriminator)
    union_args = [get_args(i) for i in get_args(monograph_args[0])]
    assert len(union_args) == 14
    assert (MonographDataField, Tag("data_field")) in union_args


def test_OtherFields():
    other_args = get_args(OtherFields)
    assert len(other_args) == 2
    assert other_args[1] == Discriminator(tag_discriminator)
    union_args = [get_args(i) for i in get_args(other_args[0])]
    assert len(union_args) == 14
    assert (OtherDataField, Tag("data_field")) in union_args
    assert (OtherDataField, Tag("852")) in union_args
    assert (OtherDataField, Tag("949")) in union_args


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

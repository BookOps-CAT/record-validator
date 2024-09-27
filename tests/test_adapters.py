import pytest
from record_validator.adapters import (
    MonographRecordAdapter,
    OtherRecordAdapter,
    FieldAdapter,
)
from record_validator.adapters import (
    get_material_type,
    get_monograph_tag,
    get_other_tag,
)


def test_get_material_type_monograph(stub_record):
    assert get_material_type(stub_record.fields) == "monograph"


def test_get_material_type_dance(stub_dance_record):
    assert get_material_type(stub_dance_record.fields) == "other"


def test_get_material_type_pamphlet(stub_pamphlet_record):
    assert get_material_type(stub_pamphlet_record.fields) == "other"


def test_get_material_type_catalogue(stub_catalogue_record):
    assert get_material_type(stub_catalogue_record.fields) == "other"


def test_get_material_type_multivol(stub_multivol_record):
    assert get_material_type(stub_multivol_record.fields) == "other"


def test_get_material_type_dict(stub_record):
    record_dict = stub_record.as_dict()
    assert get_material_type(record_dict["fields"]) == "monograph"


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("300", "data_field"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_get_monograph_tag_from_dict(tag, expected):
    field = {tag: {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    assert get_monograph_tag(field) == expected


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("300", "data_field"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_get_monograph_tag_from_marc(stub_record, tag, expected):
    field = stub_record.get(tag, tag)
    assert get_monograph_tag(field) == expected


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "data_field"),
        ("852", "data_field"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_get_other_tag_from_dict(tag, expected):
    field = {tag: {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    assert get_other_tag(field) == expected


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "data_field"),
        ("300", "data_field"),
        ("008", "008"),
        ("001", "001"),
    ],
)
def test_get_other_tag_from_marc(stub_record, tag, expected):
    field = stub_record.get(tag, tag)
    assert get_other_tag(field) == expected


def test_FieldAdapter():
    schema = FieldAdapter.json_schema(by_alias=True)
    assert sorted([i for i in schema["$defs"].keys()]) == sorted(
        [
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
            "MonographOtherField",
            "OrderField",
            "OtherDataField",
        ]
    )


def test_MonographRecordAdapter():
    schema = MonographRecordAdapter.json_schema(by_alias=True)
    assert sorted([i for i in schema["$defs"].keys()]) == sorted(
        [
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
            "MonographOtherField",
            "OrderField",
        ]
    )


def test_OtherRecordAdapter():
    schema = OtherRecordAdapter.json_schema(by_alias=True)
    assert sorted([i for i in schema["$defs"].keys()]) == sorted(
        [
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
            "OtherDataField",
        ]
    )

from typing import get_args
from pydantic import TypeAdapter, Discriminator, Tag
from pymarc import Field as MarcField
import pytest
from record_validator.adapters import (
    get_material_type,
    get_monograph_tag,
    get_other_tag,
    MonographRecordAdapter,
    OtherRecordAdapter,
    FieldAdapter,
    get_adapter,
    get_record_type,
    get_vendor_code,
    pattern_match,
    tag_discriminator,
    AuxOtherFields,
    MonographFields,
    OtherFields,
)
from record_validator.field_models import (
    AuxBibCallNo,
    MonographDataField,
    OtherDataField,
)


def test_get_adapter(stub_record):
    record_type, adapter = get_adapter(stub_record.fields)
    assert isinstance(record_type, str)
    assert isinstance(adapter, TypeAdapter)


def test_get_adapter_monograph_evp(stub_record):
    record_type, adapter = get_adapter(stub_record.fields)
    schema = adapter.json_schema(by_alias=True)
    assert record_type == "evp_monograph"
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == [
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
    ]


def test_get_adapter_monograph_no_vendor(stub_record):
    stub_record.remove_fields("901")
    stub_record["949"].delete_subfield("v")
    record_type, adapter = get_adapter(stub_record.fields)
    schema = adapter.json_schema(by_alias=True)
    assert record_type == "monograph"
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == [
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
    ]


def test_get_adapter_other_auxam(stub_aux_other_record):
    record_type, adapter = get_adapter(stub_aux_other_record.fields)
    schema = adapter.json_schema(by_alias=True)
    assert record_type == "auxam_other"
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == [
        "AuxBibCallNo",
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


def test_get_adapter_other_evp(stub_pamphlet_record):
    record_type, adapter = get_adapter(stub_pamphlet_record.fields)
    schema = adapter.json_schema(by_alias=True)
    assert record_type == "evp_other"
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == [
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


def test_get_adapter_other_no_vendor(stub_pamphlet_record):
    stub_pamphlet_record.remove_fields("901")
    record_type, adapter = get_adapter(stub_pamphlet_record.fields)
    schema = adapter.json_schema(by_alias=True)
    assert record_type == "other"
    assert isinstance(adapter, TypeAdapter)
    assert sorted([i for i in schema["$defs"].keys()]) == [
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


def test_get_record_type_monograph(stub_record):
    assert get_record_type(fields=stub_record.fields, vendor_code="EVP") == "monograph"


def test_get_record_type_dance(stub_dance_record):
    assert (
        get_record_type(fields=stub_dance_record.fields, vendor_code="EVP") == "other"
    )


def test_get_record_type_pamphlet(stub_pamphlet_record):
    assert (
        get_record_type(fields=stub_pamphlet_record.fields, vendor_code="EVP")
        == "other"
    )


def test_get_record_type_catalogue(stub_catalogue_record):
    assert (
        get_record_type(fields=stub_catalogue_record.fields, vendor_code="EVP")
        == "other"
    )


def test_get_record_type_multivol(stub_multivol_record):
    assert (
        get_record_type(fields=stub_multivol_record.fields, vendor_code="EVP")
        == "other"
    )


def test_get_record_type_auxam_other(stub_aux_other_record):
    assert (
        get_record_type(fields=stub_aux_other_record.fields, vendor_code="AUXAM")
        == "other"
    )


def test_get_record_type_bad_input():
    assert get_record_type(fields=["foo"], vendor_code="AUXAM") == "other"


def test_get_record_type_dict(stub_record):
    record_dict = stub_record.as_dict()
    assert (
        get_record_type(fields=record_dict["fields"], vendor_code="EVP") == "monograph"
    )


def test_get_vendor_code_evp(stub_record):
    assert get_vendor_code(fields=stub_record.fields) == "EVP"


def test_get_vendor_code_auxam(stub_aux_other_record):
    assert get_vendor_code(fields=stub_aux_other_record.fields) == "AUXAM"


def test_get_vendor_code_leila(stub_leila_monograph):
    assert get_vendor_code(fields=stub_leila_monograph.fields) == "LEILA"


def test_get_vendor_code_none():
    assert get_vendor_code(fields=["foo"]) is None


def test_get_vendor_code_bad_input(stub_record):
    stub_record["901"].add_subfield("a", "foo")
    assert get_vendor_code(fields=stub_record.fields) is None


def test_get_vendor_code_dict():
    fields = [
        {"tag": "001", "value": "on1381158740"},
        {
            "tag": "901",
            "ind1": " ",
            "ind2": " ",
            "subfields": [
                {"a": "EVP"},
            ],
        },
    ]
    assert get_vendor_code(fields=fields) == "EVP"


def test_get_vendor_code_pymarc_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    assert get_vendor_code(fields=stub_record_dict["fields"]) == "EVP"


@pytest.mark.parametrize(
    "subfields, pattern, expected",
    [
        (["2 volumes :"], "multivol", True),
        (["2 volumes :"], "pamphlet", False),
        (["5 pages :", "illustrations"], "pamphlet", True),
        (["5 pages :", "illustrations"], "catalogues", False),
        (["Catalogues Raisonnes"], "catalogues", True),
        (["Catalogues Raisonnés"], "catalogues", True),
        (["Catalogue Raisonnés"], "catalogues", True),
        (["foo"], "catalogues", False),
        (["ReCAP 24-"], "aux_call_no", True),
        (["ReCAP 25-"], "aux_call_no", True),
        (["ReCAP 24-100000"], "aux_call_no", False),
        (["foo"], "aux_call_no", False),
        (None, "foo", False),
    ],
)
def test_pattern_match(subfields, pattern, expected):
    assert pattern_match(subfields, pattern) == expected


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


def test_get_material_type_monograph(stub_record):
    assert get_material_type(fields=stub_record.fields) == "monograph"


def test_get_material_type_dance(stub_dance_record):
    assert get_material_type(fields=stub_dance_record.fields) == "other"


def test_get_material_type_pamphlet(stub_pamphlet_record):
    assert get_material_type(fields=stub_pamphlet_record.fields) == "other"


def test_get_material_type_catalogue(stub_catalogue_record):
    assert get_material_type(fields=stub_catalogue_record.fields) == "other"


def test_get_material_type_multivol(stub_multivol_record):
    assert get_material_type(fields=stub_multivol_record.fields) == "other"


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
            "MonographDataField",
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

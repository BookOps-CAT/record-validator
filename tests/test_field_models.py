import pytest
from pydantic import ValidationError
from pymarc import Field as MarcField
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


@pytest.mark.parametrize(
    "ind1_value, ind2_value, field_value",
    [
        (
            "8",
            " ",
            "ReCAP 23-000000",
        ),
        (
            "8",
            "",
            "ReCAP 23-000000",
        ),
        (
            "8",
            "",
            "ReCAP 24-000000",
        ),
        (
            "8",
            "",
            "ReCAP 25-000000",
        ),
    ],
)
def test_BibCallNo_valid(ind1_value, ind2_value, field_value):
    model = BibCallNo(
        tag="852", ind1=ind1_value, ind2=ind2_value, subfields=[{"h": field_value}]
    )
    assert model.model_dump(by_alias=True) == {
        "852": {
            "ind1": ind1_value,
            "ind2": ind2_value,
            "subfields": [{"h": field_value}],
        }
    }


def test_BibCallNo_valid_from_field(stub_record):
    field = stub_record.get_fields("852")[0]
    assert isinstance(field, MarcField)
    model = BibCallNo.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "852": {
            "ind1": "8",
            "ind2": " ",
            "subfields": [{"h": "ReCAP 23-100000"}],
        }
    }


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [
        (
            "1",
            "1",
        ),
        (
            "0",
            "0",
        ),
        (
            "2",
            "2",
        ),
    ],
)
def test_BibCallNo_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        BibCallNo(
            tag="852",
            ind1=ind1_value,
            ind2=ind2_value,
            subfields=[{"h": "ReCAP 23-000000"}],
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "field_value",
    ["foo", "bar", "ReCAP 11-111111"],
)
def test_BibCallNo_invalid_call_no_pattern(field_value):
    with pytest.raises(ValidationError) as e:
        BibCallNo(tag="852", ind1="8", ind2=" ", subfields=[{"h": field_value}])
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_BibCallNo_invalid_call_no_type(field_value):
    with pytest.raises(ValidationError) as e:
        BibCallNo(tag="852", ind1="8", ind2=" ", subfields=[{"h": field_value}])
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "string_type"])
    assert sorted(error_locs) == sorted([("subfields", 0, "h"), ("call_no",)])
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "ind1_value, ind2_value, field_value",
    [
        (" ", " ", "EVP"),
        ("", "", "AUXAM"),
        (" ", "", "LEILA"),
        ("", " ", "LEILA"),
    ],
)
def test_BibVendorCode_valid(ind1_value, ind2_value, field_value):
    model = BibVendorCode(
        tag="901", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": field_value}]
    )
    assert model.model_dump(by_alias=True) == {
        "901": {
            "ind1": ind1_value,
            "ind2": ind2_value,
            "subfields": [
                {
                    "a": field_value,
                }
            ],
        }
    }


def test_BibVendorCode_valid_from_field(stub_record):
    field = stub_record.get_fields("901")[0]
    assert isinstance(field, MarcField)
    model = BibVendorCode.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "901": {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"a": "EVP"}],
        }
    }


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [
        (
            "1",
            "1",
        ),
        (
            "8",
            "0",
        ),
        (
            "1",
            "0",
        ),
    ],
)
def test_BibVendorCode_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        BibVendorCode(
            tag="901", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": "EVP"}]
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_BibVendorCode_invalid_code_type(field_value):
    with pytest.raises(ValidationError) as e:
        BibVendorCode(tag="901", ind1=" ", ind2=" ", subfields=[{"a": field_value}])
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "literal_error"])
    assert sorted(error_locs) == sorted([("subfields", 0, "a"), ("vendor_code",)])
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize("field_value", ["foo", "bar", "baz"])
def test_BibVendorCode_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        BibVendorCode(tag="901", ind1=" ", ind2=" ", subfields=[{"a": field_value}])
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


def test_ControlField001_valid():
    model = ControlField001(tag="001", value="ocn123456789")
    assert model.model_dump(by_alias=True) == {"001": "ocn123456789"}


def test_ControlField001_valid_from_field():
    field = MarcField(tag="001", data="ocn123456789")
    model = ControlField001.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "001": "ocn123456789",
    }


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField001_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField001(tag="001", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField003_valid():
    model = ControlField003(tag="003", value="OCoLC")
    assert model.model_dump(by_alias=True) == {"003": "OCoLC"}


def test_ControlField003_valid_from_field():
    field = MarcField(tag="003", data="OCoLC")
    model = ControlField003.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "003": "OCoLC",
    }


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField003_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField003(tag="003", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField005_valid():
    model = ControlField005(tag="005", value="20241111111111.0")
    assert model.model_dump(by_alias=True) == {"005": "20241111111111.0"}


def test_ControlField005_valid_from_field():
    field = MarcField(tag="005", data="20241111111111.0")
    model = ControlField005.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {"005": "20241111111111.0"}


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField005_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField005(tag="005", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField006_valid():
    model = ControlField006(tag="006", value="b     s")
    assert model.model_dump(by_alias=True) == {"006": "b     s"}


def test_ControlField006_valid_from_field():
    field = MarcField(tag="006", data="b     s")
    model = ControlField006.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {"006": "b     s"}


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField006_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField006(tag="006", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField007_valid():
    model = ControlField007(tag="007", value="cr |||||||||||")
    assert model.model_dump(by_alias=True) == {"007": "cr |||||||||||"}


def test_ControlField007_valid_from_field():
    field = MarcField(tag="007", data="cr |||||||||||")
    model = ControlField007.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {"007": "cr |||||||||||"}


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField007_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField007(tag="007", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField008_valid():
    model = ControlField008(tag="008", value="210505s2021    nyu           000 0 eng d")
    assert model.model_dump(by_alias=True) == {
        "008": "210505s2021    nyu           000 0 eng d"
    }


def test_ControlField008_valid_from_field():
    field = MarcField(tag="008", data="210505s2021    nyu           000 0 eng d")
    model = ControlField008.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "008": "210505s2021    nyu           000 0 eng d"
    }


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_ControlField008_invalid_code_value(field_value):
    with pytest.raises(ValidationError) as e:
        ControlField008(tag="008", value=field_value)
    assert e.value.errors()[0]["type"] == "string_type"
    assert e.value.errors()[0]["loc"] == ("value",)
    assert len(e.value.errors()) == 1


def test_ControlField008_invalid_code_literal():
    with pytest.raises(ValidationError) as e:
        ControlField008(tag="020", value="foo")
    assert [i["type"] for i in e.value.errors()] == [
        "literal_error",
        "string_pattern_mismatch",
    ]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [(" ", " "), ("", ""), (" ", ""), ("", " ")],
)
def test_InvoiceField_valid(ind1_value, ind2_value):
    model = InvoiceField(
        tag="980",
        ind1=ind1_value,
        ind2=ind2_value,
        subfields=[
            {"a": "240101"},
            {"b": "100"},
            {"c": "0"},
            {"d": "0"},
            {"e": "100"},
            {"f": "123456"},
            {"g": "1"},
        ],
    )
    assert model.model_dump(by_alias=True)["980"]["ind1"] == ind1_value
    assert model.model_dump(by_alias=True)["980"]["ind2"] == ind2_value
    assert model.model_dump(by_alias=True)["980"]["subfields"] == [
        {"a": "240101"},
        {"b": "100"},
        {"c": "0"},
        {"d": "0"},
        {"e": "100"},
        {"f": "123456"},
        {"g": "1"},
    ]


def test_InvoiceField_valid_from_field(stub_record):
    field = stub_record.get_fields("980")[0]
    model = InvoiceField.model_validate(field, from_attributes=True)
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["980"]
    assert model_dump["980"]["ind1"] == " "
    assert model_dump["980"]["ind2"] == " "
    assert model_dump["980"]["subfields"] == [
        {"a": "240101"},
        {"b": "100"},
        {"c": "100"},
        {"d": "000"},
        {"e": "200"},
        {"f": "123456"},
        {"g": "1"},
    ]


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [("1", "1"), ("2", "0"), ("0", "5")],
)
def test_InvoiceField_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=ind1_value,
            ind2=ind2_value,
            subfields=[
                {"a": "240101"},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": "123456"},
                {"g": "1"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "field_value",
    ["2024-01-01", "2024-01-01T00:00:00", "Jan 1, 2024", "01/01/2024", "01-01-2024"],
)
def test_InvoiceField_invalid_invoice_date_value(field_value):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": field_value},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": "123456"},
                {"g": "1"},
            ],
        )
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "field_value",
    [
        1,
        1.0,
        None,
        [],
    ],
)
def test_InvoiceField_invalid_invoice_date_type(field_value):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": field_value},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": "123456"},
                {"g": "1"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "string_type"])
    assert sorted(error_locs) == sorted([("subfields", 0, "a"), ("invoice_date",)])
    assert len(e.value.errors()) == 2


def test_InvoiceField_invalid_prices_value():
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": "240101"},
                {"b": "1.00"},
                {"c": "0.00"},
                {"d": "0.00"},
                {"e": "1.00"},
                {"f": "123456"},
                {"g": "1"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types == ["string_pattern_mismatch"] * 4
    assert len(e.value.errors()) == 4


def test_InvoiceField_invalid_invoice_prices_type():
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": "240101"},
                {"b": 1.00},
                {"c": 0.00},
                {"d": 0.00},
                {"e": 1.00},
                {"f": "123456"},
                {"g": "1"},
            ],
        )
    assert len(e.value.errors()) == 8
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert error_types == ["string_type"] * 8
    assert sorted(error_locs) == sorted(
        [
            ("subfields", 1, "b"),
            ("invoice_price",),
            ("subfields", 2, "c"),
            ("invoice_tax",),
            ("subfields", 3, "d"),
            ("invoice_shipping",),
            ("subfields", 4, "e"),
            ("invoice_net_price",),
        ]
    )


@pytest.mark.parametrize(
    "field_value",
    [1.0, 1],
)
def test_InvoiceField_invalid_invoice_number_type(field_value):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": "240101"},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": field_value},
                {"g": "1"},
            ],
        )
    error_locs = [i["loc"] for i in e.value.errors()]
    assert e.value.errors()[0]["type"] == "string_type"
    assert len(e.value.errors()) == 2
    assert sorted(error_locs) == sorted([("subfields", 5, "f"), ("invoice_number",)])


@pytest.mark.parametrize(
    "copies_field",
    ["a", "1a"],
)
def test_InvoiceField_invalid_invoice_copies_value(copies_field):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": "240101"},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": "123456"},
                {"g": copies_field},
            ],
        )
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "copies_field",
    [[], 2.0, 2],
)
def test_InvoiceField_invalid_invoice_copies_type(copies_field):
    with pytest.raises(ValidationError) as e:
        InvoiceField(
            tag="980",
            ind1=" ",
            ind2=" ",
            subfields=[
                {"a": "240101"},
                {"b": "100"},
                {"c": "0"},
                {"d": "0"},
                {"e": "100"},
                {"f": "123456"},
                {"g": copies_field},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert error_types == ["string_type", "string_type"]
    assert error_locs == [("subfields", 6, "g"), ("invoice_copies",)]
    assert len(e.value.errors()) == 2


def test_ItemField_valid():
    model = ItemField(
        tag="949",
        ind1=" ",
        ind2="1",
        subfields=[
            {"z": "8528"},
            {"a": "ReCAP 23-000000"},
            {"i": "33433123456789"},
            {"p": "1.00"},
            {"v": "EVP"},
            {"h": "43"},
            {"l": "rcmb2"},
            {"t": "2"},
        ],
    )
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["ind1"] == " "
    assert model_dump["949"]["ind2"] == "1"
    assert model_dump["949"]["subfields"] == [
        {"a": "ReCAP 23-000000"},
        {"h": "43"},
        {"i": "33433123456789"},
        {"l": "rcmb2"},
        {"p": "1.00"},
        {"t": "2"},
        {"v": "EVP"},
        {"z": "8528"},
    ]


def test_ItemField_valid_from_field(stub_record):
    field = stub_record.get_fields("949")[0]
    assert isinstance(field, MarcField)
    model = ItemField.model_validate(field, from_attributes=True)
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["ind1"] == " "
    assert model_dump["949"]["ind2"] == "1"
    assert model_dump["949"]["subfields"] == [
        {"a": "ReCAP 23-100000"},
        {"c": "1"},
        {"h": "43"},
        {"i": "33433123456789"},
        {"l": "rcmf2"},
        {"m": "bar"},
        {"p": "1.00"},
        {"t": "55"},
        {"u": "foo"},
        {"v": "AUXAM"},
        {"z": "8528"},
    ]


@pytest.mark.parametrize(
    "call_no_value",
    ["ReCAP 23-000000", "ReCAP 24-000000", "ReCAP 25-000000"],
)
def test_ItemField_valid_call_nos(call_no_value):
    model = ItemField(
        tag="949",
        ind1=" ",
        ind2="1",
        subfields=[
            {"a": call_no_value},
            {"h": "43"},
            {"i": "33433123456789"},
            {"l": "rcmb2"},
            {"p": "1.00"},
            {"t": "2"},
            {"v": "EVP"},
            {"z": "8528"},
        ],
    )
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["subfields"][0]["a"] == call_no_value


@pytest.mark.parametrize(
    "vendor_code_value",
    ["EVP", "AUXAM", "LEILA"],
)
def test_ItemField_valid_vendor_code(vendor_code_value):
    model = ItemField(
        tag="949",
        ind1=" ",
        ind2="1",
        subfields=[
            {"a": "ReCAP 23-000000"},
            {"h": "43"},
            {"i": "33433123456789"},
            {"l": "rcmb2"},
            {"p": "1.00"},
            {"t": "2"},
            {"v": vendor_code_value},
            {"z": "8528"},
        ],
    )
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["subfields"][6]["v"] == vendor_code_value


@pytest.mark.parametrize(
    "item_location_value",
    [
        "rcmb2",
        "rcmf2",
        "rcmg2",
        "rc2ma",
        "rcmp2",
        "rcmb2",
        "rcph2",
        "rcpm2",
        "rcpt2",
        "rc2cf",
    ],
)
def test_ItemField_valid_item_location(item_location_value):
    model = ItemField(
        tag="949",
        ind1=" ",
        ind2="1",
        subfields=[
            {"a": "ReCAP 23-000000"},
            {"h": "43"},
            {"i": "33433123456789"},
            {"l": item_location_value},
            {"p": "1.00"},
            {"t": "2"},
            {"v": "EVP"},
            {"z": "8528"},
        ],
    )
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["subfields"][3]["l"] == item_location_value


@pytest.mark.parametrize(
    "item_type_value",
    [
        "2",
        "55",
    ],
)
def test_ItemField_valid_item_type(item_type_value):
    model = ItemField(
        tag="949",
        ind1=" ",
        ind2="1",
        subfields=[
            {"a": "ReCAP 23-000000"},
            {"h": "43"},
            {"i": "33433123456789"},
            {"l": "rcmb2"},
            {"p": "1.00"},
            {"t": item_type_value},
            {"v": "EVP"},
            {"z": "8528"},
        ],
    )
    model_dump = model.model_dump(by_alias=True)
    assert list(model_dump.keys()) == ["949"]
    assert model_dump["949"]["subfields"][5]["t"] == item_type_value


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [("1", " "), ("2", "0"), ("0", "5")],
)
def test_ItemField_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=ind1_value,
            ind2=ind2_value,
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "call_tag_value",
    ["8520", "1111", "foo"],
)
def test_ItemField_invalid_call_tag_value(call_tag_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": call_tag_value},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "call_tag_value",
    [[], ["1111"], 8528],
)
def test_ItemField_invalid_call_tag_type(call_tag_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": call_tag_value},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "literal_error"])
    assert error_locs == [("subfields", 7, "z"), ("item_call_tag",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "call_no_value",
    ["ReCAP 23-", "ReCAP", "ReCAP 00-000000", "ReCAP 24-0"],
)
def test_ItemField_invalid_call_no_value(call_no_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            item_call_tag="8528",
            subfields=[
                {"z": "8528"},
                {"a": call_no_value},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "call_no_value",
    [1.0, ["ReCAP 23-000000"], 23],
)
def test_ItemField_invalid_call_no_type(call_no_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": call_no_value},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "string_type"])
    assert error_locs == [("subfields", 0, "a"), ("item_call_no",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "vendor_code_value",
    ["FOO", "BAR", "BAZ"],
)
def test_ItemField_invalid_vendor_code_value(vendor_code_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": vendor_code_value},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "vendor_code_value",
    [1.0, ["EVP"], 23],
)
def test_ItemField_invalid_vendor_code_type(vendor_code_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": vendor_code_value},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": "2"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["literal_error", "string_type"])
    assert error_locs == [("subfields", 6, "v"), ("item_vendor_code",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "item_location_value",
    ["MAL", "foo", "bar"],
)
def test_ItemField_invalid_item_location_value(item_location_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": item_location_value},
                {"t": "2"},
            ],
        )
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "item_location_value",
    [1.0, ["EVP"], 23],
)
def test_ItemField_invalid_item_location_type(item_location_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": item_location_value},
                {"t": "2"},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["literal_error", "string_type"])
    assert error_locs == [("subfields", 3, "l"), ("item_location",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "item_type_value",
    [
        "monograph",
        "map",
        "foo",
        "bar",
    ],
)
def test_ItemField_invalid_item_type_value(item_type_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": item_type_value},
            ],
        )
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "item_type_value",
    [1.0, ["EVP"], 23],
)
def test_ItemField_invalid_item_type_data_type(item_type_value):
    with pytest.raises(ValidationError) as e:
        ItemField(
            tag="949",
            ind1=" ",
            ind2="1",
            subfields=[
                {"z": "8528"},
                {"a": "ReCAP 23-000000"},
                {"i": "33433123456789"},
                {"p": "1.00"},
                {"v": "EVP"},
                {"h": "43"},
                {"l": "rcmb2"},
                {"t": item_type_value},
            ],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["literal_error", "string_type"])
    assert error_locs == [("subfields", 5, "t"), ("item_type",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [
        (
            " ",
            "4",
        ),
        (
            "0",
            "0",
        ),
        (
            "1",
            "0",
        ),
    ],
)
def test_LCClass_valid(ind1_value, ind2_value):
    model = LCClass(
        tag="050", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": "F00"}]
    )
    assert model.model_dump(by_alias=True) == {
        "050": {
            "ind1": ind1_value,
            "ind2": ind2_value,
            "subfields": [{"a": "F00"}],
        }
    }


def test_LCClass_valid_from_field(stub_record):
    field = stub_record.get_fields("050")[0]
    assert isinstance(field, MarcField)
    model = LCClass.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "050": {
            "ind1": " ",
            "ind2": "4",
            "subfields": [{"a": "F00"}],
        }
    }


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [
        (
            "5",
            "6",
        ),
        (
            "7",
            "8",
        ),
        (
            "9",
            "1",
        ),
    ],
)
def test_LCClass_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        LCClass(tag="050", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": "F00"}])
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [
        (
            " ",
            "0",
        ),
        (
            "0",
            "4",
        ),
        (
            "",
            "0",
        ),
    ],
)
def test_LCClass_invalid_indicator_combo(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        LCClass(tag="050", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": "F00"}])
    assert e.value.errors()[0]["type"] == "value_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "field_value",
    [1.0, ["F00"], 23],
)
def test_LCClass_invalid_lcc(field_value):
    with pytest.raises(ValidationError) as e:
        LCClass(tag="050", ind1=" ", ind2="4", subfields=[{"a": field_value}])
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert error_types == ["string_type", "string_type"]
    assert sorted(error_locs) == sorted([("lcc",), ("subfields", 0, "a")])
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "ind1_value, ind2_value, field_value",
    [
        (" ", " ", "RL"),
        ("", "", "BL"),
        (" ", "", "BPL"),
        ("", " ", "RL"),
    ],
)
def test_LibraryField_valid(ind1_value, ind2_value, field_value):
    model = LibraryField(
        tag="910", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": field_value}]
    )
    assert model.model_dump(by_alias=True) == {
        "910": {
            "ind1": ind1_value,
            "ind2": ind2_value,
            "subfields": [{"a": field_value}],
        }
    }


def test_LibraryField_valid_from_field(stub_record):
    field = stub_record.get_fields("910")[0]
    assert isinstance(field, MarcField)
    model = LibraryField.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "910": {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"a": "RL"}],
        }
    }


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [("1", "1"), ("2", "0"), ("0", "5")],
)
def test_LibraryField_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        LibraryField(
            tag="910", ind1=ind1_value, ind2=ind2_value, subfields=[{"a": "RL"}]
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "field_value",
    ["foo", "bar", "baz"],
)
def test_LibraryField_invalid_library_field_value(field_value):
    with pytest.raises(ValidationError) as e:
        LibraryField(tag="910", ind1=" ", ind2=" ", subfields=[{"a": field_value}])
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "field_value",
    [1.0, ["F00"], 23],
)
def test_LibraryField_invalid_library_field_type(field_value):
    with pytest.raises(ValidationError) as e:
        LibraryField(tag="910", ind1=" ", ind2=" ", subfields=[{"a": field_value}])
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["literal_error", "string_type"])
    assert sorted(error_locs) == sorted([("library",), ("subfields", 0, "a")])
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "tag",
    [
        "020",
        "100",
        "300",
        "336",
        "490",
        "500",
        "600",
        "650",
        "655",
        "710",
        "856",
        "880",
        "990",
        "994",
    ],
)
def test_MonographOtherField_valid_tag_literal(tag):
    model = MonographOtherField(tag=tag, ind1=" ", ind2=" ", subfields=[{"a": "foo"}])
    model.model_dump(by_alias=True) == {
        tag: {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"a": "foo"}],
        }
    }


@pytest.mark.parametrize(
    "tag",
    [
        "001",
        "003",
        "005",
        "006",
        "008",
        "050",
        "852",
        "901",
        "910",
        "949",
        "960",
        "980",
    ],
)
def test_MonographOtherField_invalid_tag_literal(tag):
    with pytest.raises(ValidationError) as e:
        MonographOtherField(tag=tag, ind1=" ", ind2=" ", subfields=[{"a": "foo"}])
    error_types = [error["type"] for error in e.value.errors()]
    assert len(e.value.errors()) == 1
    assert error_types == ["string_pattern_mismatch"]


def test_OrderField_valid():
    model = OrderField(
        tag="960",
        ind1=" ",
        ind2=" ",
        subfields=[{"s": "100"}, {"t": "MAF"}, {"u": "123"}],
    )
    assert model.model_dump(by_alias=True) == {
        "960": {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"s": "100"}, {"t": "MAF"}, {"u": "123"}],
        }
    }


def test_OrderField_valid_from_field(stub_record):
    field = stub_record.get_fields("960")[0]
    assert isinstance(field, MarcField)
    model = OrderField.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "960": {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"s": "100"}, {"t": "MAF"}, {"u": "123456apprv"}],
        }
    }


@pytest.mark.parametrize(
    "ind1_value, ind2_value",
    [("1", "1"), ("2", "0"), ("0", "5")],
)
def test_OrderField_invalid_indicators(ind1_value, ind2_value):
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=ind1_value,
            ind2=ind2_value,
            subfields=[{"s": "100"}, {"t": "MAF"}, {"u": "123"}],
        )
    error_types = [i["type"] for i in e.value.errors()]
    assert error_types.count("literal_error") == 2
    assert len(e.value.errors()) == 2


def test_OrderField_invalid_price_value():
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=" ",
            ind2=" ",
            subfields=[{"s": "1.00"}, {"t": "MAF"}, {"u": "123"}],
        )
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"
    assert len(e.value.errors()) == 1


def test_OrderField_invalid_price_type():
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=" ",
            ind2=" ",
            subfields=[{"s": 1.00}, {"t": "MAF"}, {"u": "123"}],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert error_types == ["string_type", "string_type"]
    assert error_locs == [("subfields", 0, "s"), ("order_price",)]
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "field_value",
    ["rc2ma", "foo", "bar"],
)
def test_OrderField_invalid_location_value(field_value):
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=" ",
            ind2=" ",
            subfields=[{"s": "100"}, {"t": field_value}, {"u": "123"}],
        )
    assert e.value.errors()[0]["type"] == "literal_error"
    assert len(e.value.errors()) == 1


@pytest.mark.parametrize(
    "field_value",
    [[], ["foo"], 1.0],
)
def test_OrderField_invalid_location_type(field_value):
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=" ",
            ind2=" ",
            subfields=[{"s": "100"}, {"t": field_value}, {"u": "123"}],
        )
    error_types = [i["type"] for i in e.value.errors()]
    error_locs = [i["loc"] for i in e.value.errors()]
    assert sorted(error_types) == sorted(["string_type", "literal_error"])
    assert sorted(error_locs) == sorted([("subfields", 1, "t"), ("order_location",)])
    assert len(e.value.errors()) == 2


@pytest.mark.parametrize(
    "fund_field",
    [[], 1.00, 1, {}],
)
def test_OrderField_invalid_fund(fund_field):
    with pytest.raises(ValidationError) as e:
        OrderField(
            tag="960",
            ind1=" ",
            ind2=" ",
            subfields=[{"s": "100"}, {"t": "MAF"}, {"u": fund_field}],
        )
    error_locs = [i["loc"] for i in e.value.errors()]
    assert e.value.errors()[0]["type"] == "string_type"
    assert len(e.value.errors()) == 2
    assert sorted(error_locs) == sorted([("subfields", 2, "u"), ("order_fund",)])


@pytest.mark.parametrize(
    "tag",
    ["020", "100", "300", "336", "490", "949", "852"],
)
def test_OtherDataField_valid_tag_literal(tag):
    model = OtherDataField(tag=tag, ind1=" ", ind2=" ", subfields=[{"a": "foo"}])
    model.model_dump(by_alias=True) == {
        tag: {
            "ind1": " ",
            "ind2": " ",
            "subfields": [{"a": "foo"}],
        }
    }


@pytest.mark.parametrize(
    "tag",
    [
        "001",
        "003",
        "005",
        "006",
        "008",
        "050",
        "901",
        "910",
        "960",
        "980",
    ],
)
def test_OtherDataField_invalid_tag_literal(tag):
    with pytest.raises(ValidationError) as e:
        OtherDataField(tag=tag, ind1=" ", ind2=" ", subfields=[{"a": "foo"}])
    error_types = [error["type"] for error in e.value.errors()]
    assert len(e.value.errors()) == 1
    assert error_types == ["string_pattern_mismatch"]

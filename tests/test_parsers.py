from pymarc import Field as MarcField
from pymarc import Subfield
import pytest
from record_validator.parsers import (
    get_field_tag,
    get_missing_field_list,
    order_item_from_field,
    subfield_from_code,
    parse_input,
)
from record_validator.field_models import BibCallNo, InvoiceField


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("300", "data_field"),
        ("008", "control_field"),
        ("001", "control_field"),
    ],
)
def test_get_field_tag_from_dict(tag, expected):
    field = {tag: {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    assert get_field_tag(field) == expected


@pytest.mark.parametrize(
    "tag, expected",
    [
        ("245", "data_field"),
        ("960", "960"),
        ("949", "949"),
        ("300", "data_field"),
        ("008", "control_field"),
        ("001", "control_field"),
    ],
)
def test_get_field_tag_from_marc(stub_record, tag, expected):
    field = stub_record.get(tag, tag)
    assert get_field_tag(field) == expected


@pytest.mark.parametrize(
    "delete_fields, expected",
    [
        (["008", "245"], []),
        (["960"], ["960"]),
        (["949"], ["949"]),
        (["960", "980"], ["960", "980"]),
    ],
)
def test_get_missing_field_list_from_dict(stub_record, delete_fields, expected):
    for field in delete_fields:
        stub_record.remove_fields(field)
    stub_record_dict = stub_record.as_dict()
    fields = stub_record_dict["fields"]
    missing_fields = get_missing_field_list(fields)
    assert missing_fields == expected


@pytest.mark.parametrize(
    "delete_fields, expected",
    [
        (["008", "245"], []),
        (["960"], ["960"]),
        (["949"], ["949"]),
        (["960", "980"], ["960", "980"]),
    ],
)
def test_get_missing_field_list_from_marc(stub_record, delete_fields, expected):
    for field in delete_fields:
        stub_record.remove_fields(field)
    fields = stub_record.fields
    missing_fields = get_missing_field_list(fields)
    assert missing_fields == expected


@pytest.mark.parametrize(
    "fields",
    [
        (
            "008",
            "245",
        ),
        [],
        "008, 245",
    ],
)
def test_get_missing_field_list_other(fields):
    assert get_missing_field_list(fields) == [
        "852",
        "901",
        "050",
        "910",
        "960",
        "980",
        "949",
    ]


@pytest.mark.parametrize(
    "tag, code, expected",
    [("960", "t", "MAF"), ("050", "a", "F00")],
)
def test_subfield_from_code_marc(stub_record, tag, code, expected):
    field = stub_record.get(tag)
    assert subfield_from_code(field=field, tag=tag, code=code) == expected


def test_subfield_from_code_dict():
    field = {
        "tag": "980",
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"a": "foo"}, {"b": "bar"}, {"c": "baz"}],
    }
    assert subfield_from_code(field=field, tag="980", code="a") == "foo"
    assert subfield_from_code(field=field, tag="980", code="b") == "bar"
    assert subfield_from_code(field=field, tag="980", code="c") == "baz"


def test_subfield_from_code_pymarc_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    field = stub_record_dict["fields"][-1]
    assert subfield_from_code(field=field, tag="980", code="a") == "240101"


def test_subfield_from_code_other():
    field = ("980", " ", " ", [("a", "foo"), ("b", "bar"), ("c", "baz")])
    assert subfield_from_code(field=field, tag="980", code="a") is None


def test_order_item_from_field(stub_record):
    fields = stub_record.fields
    parsed_data = order_item_from_field(fields)
    assert [i["item_type"] for i in parsed_data] == ["55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(["rcmf2"])


def test_order_item_from_field_multiple(stub_record_with_dupes):
    fields = stub_record_with_dupes.fields
    parsed_data = order_item_from_field(fields)
    assert len(parsed_data) == 2
    assert [i["item_type"] for i in parsed_data] == ["55", "55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF", "MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(
        ["rcmf2", "rc2ma"]
    )


def test_order_item_from_field_error(stub_record):
    stub_record.add_field(
        MarcField(
            tag="960",
            indicators=[" ", " "],
            subfields=[Subfield(code="t", value="MAF")],
        )
    )
    fields = stub_record.fields
    with pytest.raises(AssertionError) as e:
        order_item_from_field(fields)
    assert str(e.value) == "Expected 1 order location, got 2"


def test_order_item_from_field_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    fields = stub_record_dict["fields"]
    assert isinstance(fields, list)
    parsed_data = order_item_from_field(fields)
    assert [i["item_type"] for i in parsed_data] == ["55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(["rcmf2"])


def test_order_item_from_field_dict_multiple(stub_record_with_dupes):
    stub_record_dict = stub_record_with_dupes.as_dict()
    fields = stub_record_dict["fields"]
    parsed_data = order_item_from_field(fields)
    assert len(parsed_data) == 2
    assert [i["item_type"] for i in parsed_data] == ["55", "55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF", "MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(
        ["rcmf2", "rc2ma"]
    )


def test_order_item_from_field_dict_error():
    fields = [
        {
            "tag": "960",
            "subfields": [
                {"t": "MAF"},
            ],
        },
        {
            "tag": "960",
            "subfields": [
                {"t": "MAF"},
            ],
        },
        {
            "tag": "949",
            "subfields": [
                {"l": "rcmf2"},
                {"t": "55"},
            ],
        },
    ]
    with pytest.raises(AssertionError) as e:
        order_item_from_field(fields)
    assert str(e.value) == "Expected 1 order location, got 2"


def test_parse_input_marc(stub_record):
    field = stub_record.get("852")
    parsed_data = parse_input(field, BibCallNo)
    assert parsed_data["call_no"] == "ReCAP 23-100000"
    assert parsed_data["ind1"] == "8"
    assert parsed_data["ind2"] == " "
    assert parsed_data["tag"] == "852"
    assert parsed_data["subfields"] == [{"h": "ReCAP 23-100000"}]


def test_parse_input_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    invoice_field = stub_record_dict["fields"][-1]
    parsed_data = parse_input(invoice_field, InvoiceField)
    assert parsed_data["ind1"] == " "
    assert parsed_data["ind2"] == " "
    assert parsed_data["tag"] == "980"
    assert len(parsed_data["subfields"]) == 7
    assert parsed_data["invoice_date"] == "240101"
    assert parsed_data["invoice_price"] == "100"
    assert parsed_data["invoice_tax"] == "000"
    assert parsed_data["invoice_shipping"] == "100"
    assert parsed_data["invoice_net_price"] == "200"
    assert parsed_data["invoice_number"] == "123456"
    assert parsed_data["invoice_copies"] == "1"


@pytest.mark.parametrize(
    "data",
    [[], (960, "", ""), "960"],
)
def test_parse_input_errors(data):
    parsed_data = parse_input(data, InvoiceField)
    assert parsed_data == data

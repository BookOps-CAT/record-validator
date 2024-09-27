from contextlib import nullcontext as does_not_raise
import pytest
from pydantic import ValidationError
from pymarc import Field as MarcField
from pymarc import Subfield
from record_validator.validators import (
    get_field_tag,
    get_missing_field_list,
    get_order_item_list,
    get_subfield_from_code,
    validate_fields,
    validate_field_values,
    validate_leader,
    validate_order_item_mismatches,
)


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
        ("008", "008"),
        ("001", "001"),
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
    assert sorted(missing_fields) == sorted(expected)


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
    assert sorted(missing_fields) == sorted(expected)


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
    assert sorted(get_missing_field_list(fields)) == sorted(
        [
            "852",
            "901",
            "050",
            "910",
            "960",
            "980",
            "949",
        ]
    )


@pytest.mark.parametrize(
    "tag, code, expected",
    [("960", "t", ["MAF"]), ("050", "a", ["F00"])],
)
def test_get_subfield_from_code_marc(stub_record, tag, code, expected):
    field = stub_record.get(tag)
    assert get_subfield_from_code(field=field, tag=tag, code=code) == expected


def test_get_subfield_from_code_dict():
    field = {
        "tag": "980",
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"a": "foo"}, {"b": "bar"}, {"c": "baz"}],
    }
    assert get_subfield_from_code(field=field, tag="980", code="a") == ["foo"]
    assert get_subfield_from_code(field=field, tag="980", code="b") == ["bar"]
    assert get_subfield_from_code(field=field, tag="980", code="c") == ["baz"]


def test_get_subfield_from_code_pymarc_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    field = stub_record_dict["fields"][-1]
    assert get_subfield_from_code(field=field, tag="980", code="a") == ["240101"]


def test_get_subfield_from_code_None(stub_record):
    field = {
        "tag": "980",
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"a": "foo"}, {"b": "bar"}, {"c": "baz"}],
    }
    assert get_subfield_from_code(field=field, tag="980", code="z") == [None]


def test_get_subfield_from_code_other():
    field = ("980", " ", " ", [("a", "foo"), ("b", "bar"), ("c", "baz")])
    assert get_subfield_from_code(field=field, tag="980", code="a") is None


def test_get_order_item_list_marc(stub_record):
    fields = stub_record.fields
    parsed_data = get_order_item_list(fields)
    assert [i["item_type"] for i in parsed_data] == ["55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(["rcmf2"])


def test_get_order_item_list_multiple(stub_record_with_dupes):
    fields = stub_record_with_dupes.fields
    parsed_data = get_order_item_list(fields)
    assert len(parsed_data) == 2
    assert [i["item_type"] for i in parsed_data] == ["55", "55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF", "MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(
        ["rcmf2", "rc2ma"]
    )


def test_get_order_item_list_error(stub_record):
    stub_record.add_field(
        MarcField(
            tag="960",
            indicators=[" ", " "],
            subfields=[Subfield(code="t", value="MAF")],
        )
    )
    fields = stub_record.fields
    with pytest.raises(AssertionError) as e:
        get_order_item_list(fields)
    assert str(e.value) == "Expected 1 order location, got 2"


def test_get_order_item_list_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    fields = stub_record_dict["fields"]
    assert isinstance(fields, list)
    parsed_data = get_order_item_list(fields)
    assert [i["item_type"] for i in parsed_data] == ["55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(["rcmf2"])


def test_get_order_item_list_dict_multiple(stub_record, stub_item):
    stub_record.add_field(stub_item)
    stub_record_dict = stub_record.as_dict()
    fields = stub_record_dict["fields"]
    parsed_data = get_order_item_list(fields)
    item_fields = [i for i in fields if "949" in i]
    assert len(item_fields) == 2
    assert len(parsed_data) == 2
    assert [i["item_type"] for i in parsed_data] == ["55", "55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF", "MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(
        ["rcmf2", "rcmf2"]
    )


def test_get_order_item_list_dict_error():
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
        get_order_item_list(fields)
    assert str(e.value) == "Expected 1 order location, got 2"


def test_validate_fields(stub_record):
    with does_not_raise():
        validate_fields(stub_record.as_dict()["fields"])


def test_validate_fields_invalid_field(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "foo")
    with pytest.raises(ValidationError) as e:
        validate_fields(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "literal_error"


def test_validate_fields_missing_field(stub_record):
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        validate_fields(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_fields_missing_entire_field(stub_record):
    stub_record.remove_fields("960")
    with pytest.raises(ValidationError) as e:
        validate_fields(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_fields_multiple_errors_order_item_mismatch(stub_record):
    stub_record.remove_fields("852")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "PAD")
    with pytest.raises(ValidationError) as e:
        validate_fields(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 2
    assert e.value.errors()[0]["type"] == "missing"
    assert e.value.errors()[1]["type"] == "order_item_mismatch"


def test_validate_fields_order_item_not_checked(stub_record):
    stub_record["949"].delete_subfield("t")
    stub_record["949"].add_subfield("t", "2")
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        validate_fields(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_field_values_missing_field(stub_record):
    stub_record["960"].delete_subfield("t")
    errors = []
    with does_not_raise():
        errors.extend(validate_field_values(stub_record.as_dict()["fields"]))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert str(errors[0]["type"]) == "missing"


def test_validate_field_values_multiple_errors(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["949"].delete_subfield("l")
    stub_record["949"].add_subfield("l", "foo")
    errors = []
    with does_not_raise():
        errors.extend(validate_field_values(stub_record.as_dict()["fields"]))
    error_types = [i["type"] for i in errors]
    assert len(errors) == 2
    assert sorted(error_types) == sorted(["missing", "literal_error"])


def test_validate_leader(stub_record):
    leader_str = "00454cam a22001575i 4500"
    stub_record_leader = stub_record.leader
    valid_leader_str = validate_leader(leader_str)
    valid_leader_marc = validate_leader(stub_record_leader)
    assert valid_leader_str == leader_str
    assert isinstance(valid_leader_str, str)
    assert valid_leader_marc == "00454cam a22001575i 4500"
    assert isinstance(valid_leader_marc, str)


def test_validate_order_item_mismatches(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "MAL")
    errors = []
    with does_not_raise():
        errors.extend(validate_order_item_mismatches(stub_record.as_dict()["fields"]))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert "Invalid combination of item_type, order_location and item_location" in str(
        errors[0]["type"]
    )
    assert errors[0]["input"] == {
        "order_location": "MAL",
        "item_location": "rcmf2",
        "item_type": "55",
    }
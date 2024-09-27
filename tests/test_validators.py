from contextlib import nullcontext as does_not_raise
from pydantic import ValidationError
import pytest
from pymarc import Field as MarcField
from pymarc import Subfield
from record_validator.validators import (
    get_extra_fields,
    get_missing_fields,
    get_order_item_list,
    get_order_item_mismatches,
    get_subfield_from_code,
    get_tag_list,
    validate_field_list,
    validate_leader,
    validate_monograph,
    validate_other,
)


@pytest.mark.parametrize(
    "type, expected", [("monograph", []), ("other", ["852", "949"])]
)
def test_get_extra_fields(type, expected):
    extra_fields = get_extra_fields(
        tag_list=[
            "001",
            "008",
            "050",
            "910",
            "852",
            "980",
            "960",
            "949",
            "901",
            "245",
            "300",
        ],
        material_type=type,
    )
    assert extra_fields == expected


@pytest.mark.parametrize("type, expected", [("monograph", ["901"]), ("other", ["901"])])
def test_get_missing_fields(type, expected):
    missing_fields = get_missing_fields(
        tag_list=["001", "008", "050", "910", "852", "980", "960", "949"],
        material_type=type,
    )
    assert len(missing_fields) == 1
    assert missing_fields == expected


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


def test_get_order_item_mismatches(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "MAL")
    errors = []
    with does_not_raise():
        errors.extend(get_order_item_mismatches(stub_record.as_dict()["fields"]))
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


def test_get_order_item_mismatches_no_errors(stub_record):
    errors = []
    with does_not_raise():
        errors.extend(get_order_item_mismatches(stub_record.as_dict()["fields"]))
    assert len(errors) == 0


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


def test_get_subfield_from_code_None():
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


def test_get_tag_list(stub_record):
    assert sorted(get_tag_list(stub_record)) == sorted(
        ["008", "001", "245", "050", "852", "960", "949", "300", "901", "910", "980"]
    )


def test_get_tag_list_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    assert sorted(get_tag_list(stub_record_dict["fields"])) == sorted(
        ["008", "001", "245", "050", "852", "960", "949", "300", "901", "910", "980"]
    )


@pytest.mark.parametrize(
    "type, field, error",
    [("monograph", "852", "Field required"), ("other", "949", "Extra field")],
)
def test_validate_field_list(type, field, error):
    tags = ["001", "008", "050", "910", "980", "901", "960", "949", "245", "300"]
    errors = []
    with does_not_raise():
        errors.extend(validate_field_list(tag_list=tags, material_type=type))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert str(errors[0]["type"]) == f"{error}: {field}"
    assert errors[0]["input"] == field


def test_validate_leader(stub_record):
    leader_str = "00454cam a22001575i 4500"
    stub_record_leader = stub_record.leader
    valid_leader_str = validate_leader(leader_str)
    valid_leader_marc = validate_leader(stub_record_leader)
    assert valid_leader_str == leader_str
    assert isinstance(valid_leader_str, str)
    assert valid_leader_marc == "00454cam a22001575i 4500"
    assert isinstance(valid_leader_marc, str)


def test_validate_monograph(stub_record):
    with does_not_raise():
        validate_monograph(stub_record.as_dict()["fields"])


def test_validate_monograph_invalid_field(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "foo")
    with pytest.raises(ValidationError) as e:
        validate_monograph(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "literal_error"


def test_validate_monograph_missing_field(stub_record):
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        validate_monograph(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_monograph_missing_entire_field(stub_record):
    stub_record.remove_fields("960")
    with pytest.raises(ValidationError) as e:
        validate_monograph(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_monograph_multiple_errors_order_item_mismatch(stub_record):
    stub_record.remove_fields("852")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "PAM")
    with pytest.raises(ValidationError) as e:
        validate_monograph(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 2
    assert sorted(i["type"] for i in e.value.errors()) == sorted(
        ["missing", "order_item_mismatch"]
    )


def test_validate_monograph_order_item_not_checked(stub_record):
    stub_record["949"].delete_subfield("t")
    stub_record["949"].add_subfield("t", "2")
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        validate_monograph(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_other(stub_record):
    stub_record.remove_fields("949", "852")
    with does_not_raise():
        validate_other(stub_record.as_dict()["fields"])


def test_validate_other_invalid_field(stub_record):
    stub_record.remove_fields("949", "852")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "foo")
    with pytest.raises(ValidationError) as e:
        validate_other(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "literal_error"


def test_validate_other_missing_field(stub_record):
    stub_record.remove_fields("949", "852")
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        validate_other(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_other_missing_entire_field(stub_record):
    stub_record.remove_fields("960", "949", "852")
    with pytest.raises(ValidationError) as e:
        validate_other(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "missing"


def test_validate_other_extra_field(stub_record):
    with pytest.raises(ValidationError) as e:
        validate_other(stub_record.as_dict()["fields"])
    assert len(e.value.errors()) == 2
    assert e.value.errors()[0]["type"] == "extra_forbidden"
    assert e.value.errors()[1]["type"] == "extra_forbidden"

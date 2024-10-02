from contextlib import nullcontext as does_not_raise
from pydantic import ValidationError
import pytest
from pymarc import Field as MarcField
from pymarc import Subfield
from record_validator.validators import (
    get_extra_fields,
    get_missing_fields,
    get_order_item_list,
    validate_order_items,
    get_tag_list,
    validate_field_list,
    validate_leader,
    validate_monograph,
    validate_other,
    validate_fields,
    validate_all,
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


def test_get_order_item_list_multiple(stub_record_multiple_items):
    fields = stub_record_multiple_items.fields
    parsed_data = get_order_item_list(fields)
    assert len(parsed_data) == 2
    assert [i["item_type"] for i in parsed_data] == ["55", "55"]
    assert [i["order_location"] for i in parsed_data] == ["MAF", "MAF"]
    assert sorted([i["item_location"] for i in parsed_data]) == sorted(
        ["rcmf2", "rcmf2"]
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


def test_get_order_item_list_dict_multiple(stub_record_multiple_items):
    stub_record_dict = stub_record_multiple_items.as_dict()
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


def test_validate_order_items(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "MAL")
    errors = []
    with does_not_raise():
        errors.extend(validate_order_items(stub_record.as_dict()["fields"]))
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


def test_validate_order_items_no_errors(stub_record):
    errors = []
    with does_not_raise():
        errors.extend(validate_order_items(stub_record.as_dict()["fields"]))
    assert len(errors) == 0


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


@pytest.mark.parametrize(
    "type",
    ["monograph", "evp_monograph", "auxam_monograph"],
)
def test_validate_fields_monograph(type):
    tags = ["001", "008", "050", "910", "980", "901", "949", "960", "245", "300"]
    errors = []
    with does_not_raise():
        errors.extend(validate_fields(tag_list=tags, record_type=type))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert str(errors[0]["type"]) == "Field required: 852"
    assert errors[0]["input"] == "852"


@pytest.mark.parametrize(
    "type",
    ["evp_other", "other", "leila_other"],
)
def test_validate_fields_other(type):
    tags = ["001", "008", "050", "910", "980", "901", "960", "852", "949", "245", "300"]
    errors = []
    with does_not_raise():
        errors.extend(validate_fields(tag_list=tags, record_type=type))
    assert len(errors) == 2
    assert isinstance(errors, list)
    assert sorted([str(i["type"]) for i in errors]) == sorted(
        [
            "Extra field: 852",
            "Extra field: 949",
        ]
    )
    assert [i["input"] for i in errors] == ["852", "949"]


def test_validate_fields_auxam_other():
    tags = ["001", "008", "050", "910", "980", "901", "960", "852", "949", "245", "300"]
    errors = []
    with does_not_raise():
        errors.extend(validate_fields(tag_list=tags, record_type="auxam_other"))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert str(errors[0]["type"]) == "Extra field: 949"
    assert errors[0]["input"] == "949"


@pytest.mark.parametrize(
    "type",
    ["foo", "bar", "leila"],
)
def test_validate_fields_other_record_type(type):
    tags = ["001", "008", "050", "910", "980", "901", "245", "300"]
    errors = []
    with does_not_raise():
        errors.extend(validate_fields(tag_list=tags, record_type=type))
    assert len(errors) == 1
    assert isinstance(errors, list)
    assert str(errors[0]["type"]) == "Field required: 960"
    assert errors[0]["input"] == "960"


class TestValidateAllMonograph:
    def test_validate_all(self, stub_record):
        with does_not_raise():
            validate_all(stub_record.as_dict()["fields"])

    def test_validate_all_invalid_field(self, stub_record):
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "literal_error"

    def test_validate_all_missing_field(self, stub_record):
        stub_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_missing_entire_field(self, stub_record):
        stub_record.remove_fields("960")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_multiple_errors_order_item_mismatch(self, stub_record):
        stub_record.remove_fields("852")
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "PAM")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 2
        assert sorted(i["type"] for i in e.value.errors()) == sorted(
            ["missing", "order_item_mismatch"]
        )

    def test_validate_all_order_item_not_checked(self, stub_record):
        stub_record["949"].delete_subfield("t")
        stub_record["949"].add_subfield("t", "2")
        stub_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"


class TestValidateAllPamphlet:
    def test_validate_all(self, stub_pamphlet_record):
        with does_not_raise():
            validate_all(stub_pamphlet_record.as_dict()["fields"])

    def test_validate_all_invalid_field(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("t")
        stub_pamphlet_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_pamphlet_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "literal_error"

    def test_validate_all_missing_field(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_pamphlet_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_missing_entire_field(self, stub_pamphlet_record):
        stub_pamphlet_record.remove_fields("960")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_pamphlet_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_extra_field(self, stub_record):
        stub_record["300"].delete_subfield("a")
        stub_record["300"].add_subfield("a", "5 pages")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 2
        assert e.value.errors()[0]["type"] == "extra_forbidden"
        assert e.value.errors()[1]["type"] == "extra_forbidden"


class TestValidateAllAuxamOther:
    def test_validate_all(self, stub_aux_other_record):
        with does_not_raise():
            validate_all(stub_aux_other_record.as_dict()["fields"])

    def test_validate_all_invalid_field(self, stub_aux_other_record):
        stub_aux_other_record["960"].delete_subfield("t")
        stub_aux_other_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_aux_other_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "literal_error"

    def test_validate_all_missing_field(self, stub_aux_other_record):
        stub_aux_other_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_aux_other_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_missing_entire_field(self, stub_aux_other_record):
        stub_aux_other_record.remove_fields("960")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_aux_other_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_extra_field(self, stub_auxam_monograph):
        stub_auxam_monograph["852"].delete_subfield("h")
        stub_auxam_monograph["852"].add_subfield("h", "ReCAP 24-")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_auxam_monograph.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "extra_forbidden"

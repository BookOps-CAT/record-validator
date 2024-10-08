import pytest
from pydantic import ValidationError
from pymarc import Field as MarcField
from record_validator.base_fields import (
    BaseControlField,
    BaseDataField,
    get_control_field_input,
    get_data_field_input,
)
from record_validator.field_models import BibCallNo


def test_get_control_field_input_marc(stub_record):
    field = stub_record.get("001")
    parsed_field = get_control_field_input(field)
    assert parsed_field["tag"] == "001"
    assert parsed_field["value"] == "on1381158740"


def test_get_control_field_input_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    field = stub_record_dict["fields"][0]
    parsed_field = get_control_field_input(field)
    assert parsed_field["tag"] == "001"
    assert parsed_field["value"] == "on1381158740"


@pytest.mark.parametrize(
    "data",
    [[], (960, "", ""), "960", {"960": "foo"}],
)
def test_get_control_field_input_errors(data):
    parsed_data = get_control_field_input(data)
    assert parsed_data == data


def test_get_control_field_input_extra_fields():
    field = {"001": {"value": "on1234567890", "ind1": "1", "ind2": "2"}}
    parsed_data = get_control_field_input(field)
    assert parsed_data == {
        "tag": "001",
        "value": "on1234567890",
        "ind1": "1",
        "ind2": "2",
    }


def test_get_data_field_input_marc(stub_record):
    field = stub_record.get("852")
    parsed_field = get_data_field_input(field, BaseDataField)
    parsed_bib_call_no = get_data_field_input(field, BibCallNo)
    assert parsed_field["tag"] == "852"
    assert parsed_field["ind1"] == "8"
    assert parsed_field["ind2"] == " "
    assert parsed_field["subfields"] == [{"h": "ReCAP 23-100000"}]
    assert parsed_bib_call_no["call_no"] == "ReCAP 23-100000"
    assert parsed_field["tag"] == parsed_bib_call_no["tag"]
    assert parsed_field["ind1"] == parsed_bib_call_no["ind1"]
    assert parsed_field["ind2"] == parsed_bib_call_no["ind2"]
    assert parsed_field["subfields"] == parsed_bib_call_no["subfields"]


def test_get_data_field_input_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    field = stub_record_dict["fields"][-1]
    parsed_field = get_data_field_input(field, BaseDataField)
    assert parsed_field["tag"] == "980"
    assert parsed_field["ind1"] == " "
    assert parsed_field["ind2"] == " "
    assert parsed_field["subfields"] == [
        {"a": "240101"},
        {"b": "100"},
        {"c": "100"},
        {"d": "000"},
        {"e": "200"},
        {"f": "123456"},
        {"g": "1"},
    ]


@pytest.mark.parametrize(
    "data",
    [[], (960, "", ""), "960", {"960": "foo"}],
)
def test_get_data_field_input_errors(data):
    parsed_data = get_data_field_input(data, BaseDataField)
    assert parsed_data == data


def test_BaseControlField_valid():
    model = BaseControlField(tag="001", value="on1234567890")
    assert model.model_dump(by_alias=True) == {"001": "on1234567890"}


def test_BaseControlField_valid_from_field(stub_record):
    field = stub_record.get_fields("008")[0]
    assert isinstance(field, MarcField)
    model = BaseControlField.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "008": "190306s2017    ht a   j      000 1 hat d"
    }


def test_BaseControlField_valid_from_dict():
    input = {"008": "190306s2017    ht a   j      000 1 hat d"}
    model = BaseControlField.model_validate(input, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "008": "190306s2017    ht a   j      000 1 hat d"
    }


def test_BaseControlField_extra_fields():
    with pytest.raises(ValidationError) as e:
        BaseControlField(tag="001", value="on1234567890", ind1="1", ind2="2")
    assert len(e.value.errors()) == 2
    assert e.value.errors()[0]["loc"] == ("ind1",)
    assert e.value.errors()[1]["loc"] == ("ind2",)
    assert e.value.errors()[0]["msg"] == "Extra inputs are not permitted"
    assert e.value.errors()[1]["msg"] == "Extra inputs are not permitted"


def test_BaseControlField_invalid_tag():
    with pytest.raises(ValidationError) as e:
        BaseControlField(tag="0000", value="ReCAP 23-100000")
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ("tag",)
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"


def test_BaseControlField_invalid_value():
    with pytest.raises(ValidationError) as e:
        BaseControlField(tag="005", value=20240413112604.0)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ("value",)
    assert e.value.errors()[0]["type"] == "string_type"


def test_BaseControlField_invalid_tag_literal():
    with pytest.raises(ValidationError) as e:
        BaseControlField(tag="010", ind1=" ", ind2=" ", subfields=[{"a": "foo"}])
    error_types = [error["type"] for error in e.value.errors()]
    assert len(e.value.errors()) == 5
    assert sorted(error_types) == sorted(
        [
            "string_pattern_mismatch",
            "extra_forbidden",
            "extra_forbidden",
            "extra_forbidden",
            "missing",
        ]
    )


@pytest.mark.parametrize(
    "input",
    [
        [],
        "4",
        (
            "005",
            20240413112604.0,
        ),
    ],
)
def test_BaseControlField_invalid_input(input):
    with pytest.raises(ValidationError) as e:
        BaseControlField.model_validate(input, from_attributes=True)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ()
    assert e.value.errors()[0]["type"] == "model_attributes_type"


@pytest.mark.parametrize(
    "tag, ind1_value, ind2_value, field_value", [("020", " ", "4", "9781234567890")]
)
def test_BaseDataField_valid(tag, ind1_value, ind2_value, field_value):
    model = BaseDataField(
        tag=tag, ind1=ind1_value, ind2=ind2_value, subfields=[{"a": field_value}]
    )
    assert model.model_dump(by_alias=True) == {
        "020": {
            "ind1": ind1_value,
            "ind2": ind2_value,
            "subfields": [{"a": field_value}],
        }
    }


def test_BaseDataField_valid_from_field(stub_record):
    field = stub_record.get_fields("050")[0]
    assert isinstance(field, MarcField)
    model = BaseDataField.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "050": {
            "ind1": " ",
            "ind2": "4",
            "subfields": [{"a": "F00"}],
        }
    }


def test_BaseDataField_valid_from_pymarc_dict(stub_record):
    field = stub_record.get_fields("050")[0]
    assert isinstance(field, MarcField)
    model = BaseDataField.model_validate(field, from_attributes=True)
    assert model.model_dump(by_alias=True) == {
        "050": {
            "ind1": " ",
            "ind2": "4",
            "subfields": [{"a": "F00"}],
        }
    }


def test_BaseDataField_invalid_tag():
    with pytest.raises(ValidationError) as e:
        BaseDataField(tag="0000", ind1=" ", ind2=" ", subfields=[{"a": "F00"}])
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ("tag",)
    assert e.value.errors()[0]["type"] == "string_pattern_mismatch"


@pytest.mark.parametrize(
    "ind1, ind2, error_type",
    [
        ("  ", "11", "string_pattern_mismatch"),
        ("A", "B", "string_pattern_mismatch"),
        ("foo", "bar", "string_pattern_mismatch"),
        (1, 2, "string_type"),
    ],
)
def test_BaseDataField_invalid_indicators(ind1, ind2, error_type):
    with pytest.raises(ValidationError) as e:
        BaseDataField(
            tag="020", ind1=ind1, ind2=ind2, subfields=[{"a": "9781234567890"}]
        )
    error_locs = [error["loc"] for error in e.value.errors()]
    error_types = [error["type"] for error in e.value.errors()]
    assert len(e.value.errors()) == 4
    assert sorted(error_locs) == sorted(
        [
            ("ind1", "constrained-str"),
            ("ind1", "literal['',' ']"),
            ("ind2", "constrained-str"),
            ("ind2", "literal['',' ']"),
        ]
    )
    assert sorted(error_types) == sorted(
        [error_type, error_type, "literal_error", "literal_error"]
    )


@pytest.mark.parametrize(
    "subfields",
    ["foo", 1, 2.0],
)
def test_BaseDataField_invalid_subfields(subfields):
    with pytest.raises(ValidationError) as e:
        BaseDataField(tag="020", ind1=" ", ind2=" ", subfields=subfields)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ("subfields",)
    assert e.value.errors()[0]["type"] == "list_type"


@pytest.mark.parametrize(
    "input",
    [
        [],
        "4",
        (
            "005",
            20240413112604.0,
        ),
    ],
)
def test_BaseDataField_invalid_input(input):
    with pytest.raises(ValidationError) as e:
        BaseDataField.model_validate(input, from_attributes=True)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["loc"] == ()
    assert e.value.errors()[0]["type"] == "model_attributes_type"

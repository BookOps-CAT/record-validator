import pytest
from pymarc import Subfield
from pymarc import Field as MarcField
from pydantic import ValidationError
from record_validator.marc_errors import MarcError, MarcValidationError
from record_validator.marc_models import MonographRecord


def test_MarcError_string_pattern(stub_record):
    stub_record.remove_fields("852")
    stub_record.add_field(
        MarcField(
            tag="852",
            indicators=["8", " "],
            subfields=[Subfield(code="h", value="ReCAP-24-119100")],
        )
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields", "852", "call_no")
    assert error.input == "ReCAP-24-119100"
    assert isinstance(error.ctx, dict)
    assert error.type == "string_pattern_mismatch"
    assert "String should match pattern" in error.msg
    assert error.loc_marc == "852$h"


def test_MarcError_missing_field(stub_record):
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == (
        "fields",
        "960",
        "order_location",
    )
    assert error.type == "missing"
    assert error.input == {
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"s": "100"}, {"u": "123456apprv"}],
        "tag": "960",
        "order_fund": "123456apprv",
        "order_price": "100",
    }
    assert error.ctx is None
    assert error.msg == "Field required"
    assert error.loc_marc == "960$t"


def test_MarcError_missing_entire_field(stub_record):
    stub_record.remove_fields("980")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == (
        "fields",
        "980",
    )
    assert error.ctx is None
    assert error.type == "missing"
    assert error.msg == "Field required: 980"
    assert error.loc_marc == "980"


def test_MarcError_missing_subfield(stub_record):
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields", "960", "order_location")
    assert error.type == "missing"
    assert error.input == {
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"s": "100"}, {"u": "123456apprv"}],
        "order_fund": "123456apprv",
        "order_price": "100",
        "tag": "960",
    }
    assert error.ctx is None
    assert error.msg == "Field required"
    assert error.loc_marc == "960$t"


def test_MarcError_literal(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "foo")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields", "960", "order_location")
    assert error.input == "foo"
    assert isinstance(error.ctx, dict)
    assert error.type == "literal_error"
    assert "Input should be" in error.msg
    assert error.loc_marc == "960$t"


def test_MarcError_literal_indicator_error(stub_record):
    stub_record.remove_fields("960")
    stub_record.add_field(
        MarcField(
            tag="960",
            indicators=["7", " "],
            subfields=[
                Subfield(code="s", value="100"),
                Subfield(code="t", value="MAF"),
                Subfield(code="u", value="123456apprv"),
            ],
        )
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields", "960", "ind1")
    assert error.input == "7"
    assert isinstance(error.ctx, dict)
    assert error.type == "literal_error"
    assert "Input should be" in error.msg
    assert error.loc_marc == "960ind1"


def test_MarcError_extra_fields(stub_record):
    record_dict = stub_record.as_dict()
    record_dict["fields"].append(
        {"003": {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(**record_dict)
    extra_field_errors = [i for i in e.value.errors() if i["type"] == "extra_forbidden"]
    string_type_error = [i for i in e.value.errors() if i["type"] == "string_type"]
    error = MarcError(extra_field_errors[0])
    assert len(e.value.errors()) == 4
    assert len(extra_field_errors) == 3
    assert len(string_type_error) == 1
    assert error.loc == (
        "fields",
        "003",
        "ind1",
    )
    assert error.input == " "
    assert error.ctx is None
    assert error.type == "extra_forbidden"
    assert error.msg == "Extra inputs are not permitted"
    assert error.loc_marc == "003ind1"


def test_MarcError_order_item_mismatch(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "MAB")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == (
        "order_field",
        "item_location",
        "item_type",
    )
    assert sorted(error.input) == sorted(("MAB", "rcmf2", "55"))
    assert error.ctx is None
    assert error.type == "order_item_mismatch"
    assert (
        "Invalid combination of item_type, order_location and item_location:"
        in error.msg
    )
    assert error.loc_marc == ("960$t", "949_$l", "949_$t")


def test_MarcError_string_type(stub_record):
    stub_record["960"].delete_subfield("s")
    stub_record["960"].add_subfield("s", 1.00)
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = [MarcError(i) for i in e.value.errors()]
    error_locs = [i.loc for i in errors]
    error_types = [i.type for i in errors]
    errors_loc_marc = [i.loc_marc for i in errors]
    assert len(errors) == 2
    assert sorted(error_locs) == sorted(
        [("fields", "960", "subfields", 0, "s"), ("fields", "960", "order_price")]
    )
    assert all(isinstance(i.input, float) for i in errors)
    assert error_types == ["string_type", "string_type"]
    assert errors_loc_marc == ["960$s", "960$s"]


def test_MarcValidationError_literal_error(stub_record):
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "foo")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert errors["invalid_fields"] == [
        {
            "error_type": "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'",
            "field": "960$t",
        },
    ]
    assert len(errors["invalid_fields"]) == 1
    assert len(errors["missing_fields"]) == 0
    assert len(errors["extra_fields"]) == 0
    assert len(errors["order_item_mismatches"]) == 0


def test_MarcValidationError_string_type(stub_record):
    stub_record["960"].delete_subfield("s")
    stub_record["960"].add_subfield("s", 1.00)
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert errors["invalid_fields"][0] == {
        "error_type": "Input should be a valid string. Examples: ['100', '200']",
        "field": "960$s",
    }
    assert errors["invalid_fields"][1] == {
        "error_type": "Input should be a valid string. Examples: ['100', '200']",
        "field": "960$s",
    }
    assert len(errors["invalid_fields"]) == 2
    assert len(errors["missing_fields"]) == 0
    assert len(errors["extra_fields"]) == 0
    assert len(errors["order_item_mismatches"]) == 0


def test_MarcValidationError_string_pattern(stub_record):
    stub_record["960"].delete_subfield("s")
    stub_record["960"].add_subfield("s", "1.00")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert errors["invalid_fields"] == [
        {
            "error_type": "String should match pattern. Examples: ['100', '200']",
            "field": "960$s",
        }
    ]
    assert len(errors["invalid_fields"]) == 1
    assert len(errors["missing_fields"]) == 0
    assert len(errors["extra_fields"]) == 0
    assert len(errors["order_item_mismatches"]) == 0


def test_MarcValidationError_extra_fields(stub_record):
    record_dict = stub_record.as_dict()
    record_dict["fields"].append(
        {"003": {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(**record_dict)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert len(errors["missing_fields"]) == 0
    assert len(errors["invalid_fields"]) == 1
    assert len(errors["extra_fields"]) == 3
    assert len(errors["order_item_mismatches"]) == 0
    assert errors["missing_fields"] == []
    assert errors["invalid_fields"] == [
        {
            "field": "003",
            "error_type": "Input should be a valid string. Examples: ['OCoLC', 'DLC']",
        }
    ]
    assert errors["extra_fields"] == ["003ind1", "003ind2", "003subfields"]
    assert errors["order_item_mismatches"] == []


def test_MarcValidationError_multiple_errors_order_item(stub_record):
    stub_record.remove_fields("980")
    stub_record["852"].delete_subfield("h")
    stub_record["852"].add_subfield("h", "ReCAP-24-119100")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "PAH")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert len(errors["missing_fields"]) == 1
    assert len(errors["invalid_fields"]) == 1
    assert len(errors["extra_fields"]) == 0
    assert len(errors["order_item_mismatches"]) == 1
    assert errors["missing_fields"] == ["980"]
    assert errors["invalid_fields"][0]["field"] == "852$h"
    assert errors["extra_fields"] == []
    assert errors["order_item_mismatches"] == [("55", "rcmf2", "PAH")]

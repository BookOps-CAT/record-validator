import pytest
from pymarc import Subfield
from pymarc import Field as MarcField
from pydantic import ValidationError
from record_validator.translate import MarcError, MarcValidationError
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
    assert "String should match pattern " in error.msg
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


def test_MarcError_missing_required_field(stub_record):
    stub_record.remove_fields("980")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields",)
    assert error.ctx is None
    assert error.type == "missing_required_field"
    assert error.msg == "Field required: 980"
    # assert error.loc_marc == "980"


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
    assert "Input should be " in error.msg
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
    assert "Input should be " in error.msg
    assert error.loc_marc == "960ind1"


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
    assert error.url is None
    assert error.type == "order_item_mismatch"
    assert (
        "Invalid combination of item_type, order_location and item_location:"
        in error.msg
    )
    assert error.loc_marc == ("960$t", "949_$l", "949_$t")


def test_MarcError_string_type(stub_record):
    stub_record["960"].delete_subfield("b")
    stub_record["960"].add_subfield("b", 1.00)
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    error = MarcError(e.value.errors()[0])
    assert len(e.value.errors()) == 1
    assert error.loc == ("fields", "960", "subfields", 0, "b")
    assert isinstance(error.input, float)
    assert error.ctx is None
    assert error.type == "string_type"
    assert error.msg == "Input should be a valid string"
    assert error.loc_marc == "960$b"


# def test_MarcValidationError_multiple_errors(stub_record):
#     stub_record["949"].delete_subfield("h")
#     stub_record["852"].delete_subfield("h")
#     stub_record["852"].add_subfield("h", "ReCAP-24-119100")
#     stub_record["960"].delete_subfield("t")
#     stub_record["960"].add_subfield("t", "foo")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     errors = MarcValidationError(e.value.errors())
#     error_output = errors.to_dict()
#     error_locs = [error.loc for error in errors.errors]
#     assert error_locs == []
#     assert error_output["missing_field_count"] == 1
#     assert error_output["invalid_field_count"] == 2
#     assert error_output["extra_field_count"] == 0
#     assert error_output["error_count"] == 3
#     assert error_output["missing_fields"] == ["949_1_$h"]
#     assert error_output["invalid_fields"][0]["invalid_field"] == "852$h"
#     assert error_output["extra_fields"] == []
#     assert error_output["order_item_mismatches"] == []


def test_MarcValidationError_multiple_errors_order_item(stub_record):
    stub_record["852"].delete_subfield("h")
    stub_record["852"].add_subfield("h", "ReCAP-24-119100")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "PAH")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    errors = MarcValidationError(e.value.errors()).to_dict()
    assert errors["missing_field_count"] == 0
    assert errors["invalid_field_count"] == 1
    assert errors["extra_field_count"] == 0
    assert errors["error_count"] == 2
    assert len(errors["order_item_mismatches"]) == 1
    assert errors["missing_fields"] == []
    assert errors["invalid_fields"][0]["invalid_field"] == "852$h"
    assert errors["extra_fields"] == []
    assert errors["order_item_mismatches"] == [("55", "rcmf2", "PAH")]

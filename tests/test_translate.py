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


# def test_MarcError_missing_field(stub_record):
#     stub_record.remove_fields("960")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields",)
#     assert error.type == "missing_required_field"
#     assert error.input == "960"
#     assert error.ctx is None
#     assert error.msg == "Field required: 960"
#     assert error.loc_marc == "960"


# def test_MarcError_missing_required_field(stub_record):
#     stub_record.remove_fields("980")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields",)
#     assert error.ctx is None
#     assert error.type == "missing_required_field"
#     assert error.msg == "Field required: 980"
#     assert error.loc_marc == "980"


# def test_MarcError_missing_subfield(stub_record):
#     stub_record["960"].delete_subfield("t")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields", "960", "order_location")
#     assert error.type == "missing"
#     assert error.input == {
#         "ind1": " ",
#         "ind2": " ",
#         "subfields": [{"s": "100"}, {"u": "123456apprv"}],
#         "order_fund": "123456apprv",
#         "order_price": "100",
#         "tag": "960",
#     }
#     assert error.ctx is None
#     assert error.msg == "Field required"
#     assert error.loc_marc == "960$t"


# def test_MarcError_literal(stub_record):
#     stub_record["960"].delete_subfield("t")
#     stub_record["960"].add_subfield("t", "foo")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields", "960", "order_location")
#     assert error.input == "foo"
#     assert isinstance(error.ctx, dict)
#     assert error.type == "literal_error"
#     assert "Input should be " in error.msg
#     assert error.loc_marc == "960$t"


# def test_MarcError_literal_indicator_error(stub_record):
#     stub_record.remove_fields("960")
#     stub_record.add_field(
#         MarcField(
#             tag="960",
#             indicators=["7", " "],
#             subfields=[
#                 Subfield(code="s", value="100"),
#                 Subfield(code="t", value="MAF"),
#                 Subfield(code="u", value="123456apprv"),
#             ],
#         )
#     )
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields", "960", "ind1")
#     assert error.input == "7"
#     assert isinstance(error.ctx, dict)
#     assert error.type == "literal_error"
#     assert "Input should be " in error.msg
#     assert error.loc_marc == "960ind1"


# def test_MarcError_order_item_mismatch(stub_record):
#     stub_record["960"].delete_subfield("t")
#     stub_record["960"].add_subfield("t", "MAB")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == (
#         "fields",
#         "order_field",
#         "item_location",
#         "item_type",
#     )
#     assert error.input == ("MAB", "rcmf2", "55")
#     assert error.ctx is None
#     assert error.url is None
#     assert error.type == "order_item_mismatch"
#     assert (
#         "Invalid combination of item type, order location and item location:"
#         in error.msg
#     )
#     assert error.loc_marc == ("960$t", "949_$l", "949_$t")


# def test_MarcError_string_type(stub_record):
#     stub_record["960"].delete_subfield("b")
#     stub_record["960"].add_subfield("b", 100)
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == ("fields", "invoice_field", "invoice_price")
#     assert isinstance(error.input, float)
#     assert error.ctx is None
#     assert error.type == "string_type"
#     assert error.msg == "Input should be a valid string"
#     assert error.loc_marc == "980$b"


# def test_MarcError_model_type(stub_record):
#     stub_record.remove_fields("980")
#     stub_record_dict = stub_record.as_dict()
#     stub_record_dict["fields"].append({"980": "invoice_field"})
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(**stub_record_dict)
#     error = MarcError(e.value.errors()[0])
#     assert len(e.value.errors()) == 1
#     assert error.loc == (
#         "fields",
#         "invoice_field",
#     )
#     assert isinstance(error.input, set)
#     assert error.ctx == {"class_name": "InvoiceFieldModel"}
#     assert error.type == "model_type"
#     assert "Input should be a valid dictionary or instance of " in error.msg
#     assert error.loc_marc == "980"


# def test_MarcValidationError_monograph_multiple_errors(stub_record):
#     stub_record["949"].delete_subfield("h")
#     stub_record["852"].delete_subfield("h")
#     stub_record["960"].delete_subfield("t")
#     stub_record["852"].add_subfield("h", "ReCAP-24-119100")
#     stub_record["960"].add_subfield("t", "foo")
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
#     errors = MarcValidationError(e.value.errors()).to_dict()
#     assert errors["missing_field_count"] == 1
#     assert errors["invalid_field_count"] == 1
#     assert errors["extra_field_count"] == 0
#     assert errors["error_count"] == 2
#     assert errors["missing_fields"] == ["949_1_$h"]
#     assert errors["invalid_fields"][0]["invalid_field"] == "852$h"
#     assert errors["extra_fields"] == []
#     assert errors["order_item_mismatches"] == []

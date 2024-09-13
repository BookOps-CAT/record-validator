from contextlib import nullcontext as does_not_raise
import pytest
from pydantic import ValidationError
from pymarc import Field as MarcField
from record_validator.validators import validate_order_item_data


# def test_validate_order_item_data(stub_record):
#     stub_record["960"].delete_subfield("t")
#     stub_record["960"].add_subfield("t", "MAL")
#     errors = validate_order_item_data(stub_record.fields)
#     assert len(errors) == 1
#     assert isinstance(errors, list)
#     assert errors[0]["loc"] == ("order_location",)

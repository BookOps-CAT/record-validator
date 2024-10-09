import pytest
from pydantic import ValidationError
from record_validator.marc_errors import (
    get_examples_from_schema,
    MarcError,
    MarcValidationError,
)
from record_validator.marc_models import RecordModel


@pytest.mark.parametrize(
    "field, examples",
    [
        (
            (
                "960",
                "order_price",
            ),
            ["100", "200"],
        ),
        (
            (
                "fields",
                "001",
                "value",
            ),
            ["ocn123456789", "ocm123456789"],
        ),
        (
            (
                "fields",
                "003",
                "value",
            ),
            ["OCoLC", "DLC"],
        ),
        (
            (
                "fields",
                "005",
                "value",
            ),
            ["20240101125000.0"],
        ),
        (
            (
                "fields",
                "006",
                "value",
            ),
            ["b|||||||||||||||||"],
        ),
        (
            (
                "fields",
                "007",
                "value",
            ),
            ["cr |||||||||||"],
        ),
        (
            (
                "fields",
                "008",
                "value",
            ),
            ["210505s2021    nyu           000 0 eng d"],
        ),
        (
            (
                "fields",
                "245",
            ),
            None,
        ),
        (
            (
                "fields",
                "901",
                "vendor_code",
            ),
            ["EVP", "AUXAM", "LEILA"],
        ),
        (
            (
                "fields",
                "910",
                "library",
            ),
            ["RL", "BL", "BPL"],
        ),
        (
            (
                "fields",
                "852",
                "call_no",
            ),
            ["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
        ),
        (
            (
                "fields",
                "050",
                "lcc",
            ),
            ["PJ7962.H565", "DK504.932.R87"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_date",
            ),
            ["240101", "230202"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_price",
            ),
            ["100", "200"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_shipping",
            ),
            ["1", "20"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_tax",
            ),
            ["1", "20"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_net_price",
            ),
            ["100", "200"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_number",
            ),
            ["20051330", "20051331"],
        ),
        (
            (
                "fields",
                "980",
                "invoice_copies",
            ),
            ["1", "20", "4"],
        ),
        (
            (
                "fields",
                "949",
                "item_call_no",
            ),
            ["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
        ),
        (
            (
                "fields",
                "949",
                "item_barcode",
            ),
            ["33433123456789", "33433111111111"],
        ),
        (
            (
                "fields",
                "949",
                "item_price",
            ),
            ["1.00", "0.00"],
        ),
        (
            (
                "fields",
                "960",
                "order_price",
            ),
            ["100", "200"],
        ),
        (
            (
                "fields",
                "960",
                "subfields",
                0,
                "s",
            ),
            ["100", "200"],
        ),
        (
            (
                "fields",
                "960",
                "subfields",
                "order_price",
            ),
            ["100", "200"],
        ),
    ],
)
def test_get_examples_from_schema(field, examples):
    assert get_examples_from_schema(field) == examples


class TestMarcErrorMonograph:
    def test_MarcError_string_pattern(self, stub_record):
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "ReCAP-24-119100")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "852", "call_no")
        assert error.input == "ReCAP-24-119100"
        assert isinstance(error.ctx, dict)
        assert error.type == "string_pattern_mismatch"
        assert (
            error.msg
            == "String should match pattern. Examples: ['ReCAP 23-000001', 'ReCAP 24-100001', 'ReCAP 25-222000']"
        )
        assert error.loc_marc == "852$h"

    def test_MarcError_missing_entire_field(self, stub_record):
        stub_record.remove_fields("980")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
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

    def test_MarcError_missing_subfield(self, stub_record):
        stub_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
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

    def test_MarcError_item_agency(self, stub_record):
        stub_record["949"].delete_subfield("h")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "949", "item_agency")
        assert error.input is None
        assert isinstance(error.ctx, dict)
        assert error.type == "value_error"
        assert error.msg == "Invalid Item Agency. Item Agency is required for rcmf2"
        assert error.loc_marc == "949$h"

    def test_MarcError_literal(self, stub_record):
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "960", "order_location")
        assert error.input == "foo"
        assert isinstance(error.ctx, dict)
        assert error.type == "literal_error"
        assert (
            error.msg
            == "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'"
        )
        assert error.loc_marc == "960$t"

    def test_MarcError_literal_indicator_error(self, stub_record):
        stub_record["960"].indicator1 = "7"
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "960", "ind1")
        assert error.input == "7"
        assert isinstance(error.ctx, dict)
        assert error.type == "literal_error"
        assert error.msg == "Input should be: ' ' or ''"
        assert error.loc_marc == "960ind1"

    def test_MarcError_lcc_indicator_error(self, stub_record):
        stub_record["050"].indicator2 = "0"
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == (
            "fields",
            "050",
        )
        assert error.input == [" ", "0"]
        assert isinstance(error.ctx, dict)
        assert error.type == "value_error"
        assert (
            error.msg
            == "Invalid indicators. Valid combinations are: [(' ', '4'), ('', '4'), ('0', '0'), ('1', '0')]"
        )
        assert error.loc_marc == "050"

    def test_MarcError_extra_fields(self, stub_record):
        record_dict = stub_record.as_dict()
        record_dict["fields"].append(
            {"003": {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
        )
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        extra_field_errors = [
            i for i in e.value.errors() if i["type"] == "extra_forbidden"
        ]
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

    def test_MarcError_order_item_mismatch(self, stub_record):
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "MAB")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == (
            "order_field",
            "item_location",
            "item_type",
        )
        assert sorted(error.input) == sorted(
            {"order_location": "MAB", "item_location": "rcmf2", "item_type": "55"}
        )
        assert error.ctx is None
        assert error.type == "order_item_mismatch"
        assert (
            error.msg
            == "Invalid combination of item_type, order_location and item_location: {'order_location': 'MAB', 'item_location': 'rcmf2', 'item_type': '55'}"
        )
        assert error.loc_marc == ("960$t", "949_$l", "949_$t")

    def test_MarcError_string_type(self, stub_record):
        stub_record["960"].delete_subfield("s")
        stub_record["960"].add_subfield("s", 1.00)
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = [MarcError(i) for i in e.value.errors()]
        error_locs = [i.loc for i in errors]
        error_types = [i.type for i in errors]
        errors_loc_marc = [i.loc_marc for i in errors]
        assert len(errors) == 2
        assert sorted(error_locs) == sorted(
            [
                ("fields", "960", "subfields", 0, "s"),
                ("fields", "960", "order_price"),
            ]
        )
        assert all(isinstance(i.input, float) for i in errors)
        assert error_types == ["string_type", "string_type"]
        assert errors_loc_marc == ["960$s", "960$s"]


class TestMarcErrorOther:
    def test_MarcError_string_pattern(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("s")
        stub_pamphlet_record["960"].add_subfield("s", "1.00")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "960", "order_price")
        assert error.input == "1.00"
        assert isinstance(error.ctx, dict)
        assert error.type == "string_pattern_mismatch"
        assert error.msg == "String should match pattern. Examples: ['100', '200']"
        assert error.loc_marc == "960$s"

    def test_MarcError_missing_entire_field(self, stub_pamphlet_record):
        stub_pamphlet_record.remove_fields("980")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
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

    def test_MarcError_missing_subfield(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
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

    def test_MarcError_literal(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("t")
        stub_pamphlet_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "960", "order_location")
        assert error.input == "foo"
        assert isinstance(error.ctx, dict)
        assert error.type == "literal_error"
        assert (
            error.msg
            == "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'"
        )
        assert error.loc_marc == "960$t"

    def test_MarcError_literal_indicator_error(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].indicator1 = "7"
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == ("fields", "960", "ind1")
        assert error.input == "7"
        assert isinstance(error.ctx, dict)
        assert error.type == "literal_error"
        assert error.msg == "Input should be: ' ' or ''"
        assert error.loc_marc == "960ind1"

    def test_MarcError_lcc_indicator_error(self, stub_pamphlet_record):
        stub_pamphlet_record["050"].indicator2 = "0"
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        error = MarcError(e.value.errors()[0])
        assert len(e.value.errors()) == 1
        assert error.loc == (
            "fields",
            "050",
        )
        assert error.input == [" ", "0"]
        assert isinstance(error.ctx, dict)
        assert error.type == "value_error"
        assert (
            error.msg
            == "Invalid indicators. Valid combinations are: [(' ', '4'), ('', '4'), ('0', '0'), ('1', '0')]"
        )
        assert error.loc_marc == "050"

    def test_MarcError_extra_fields(self, stub_record):
        stub_record["300"].delete_subfield("a")
        stub_record["300"].add_subfield("a", "5 pages")
        record_dict = stub_record.as_dict()
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        error_1 = MarcError(e.value.errors()[0])
        error_2 = MarcError(e.value.errors()[1])
        assert len(e.value.errors()) == 2
        assert error_1.type == "extra_forbidden"
        assert error_1.loc == ("fields", "852")
        assert error_1.input == "852"
        assert error_1.ctx is None
        assert error_1.msg == "Extra field: 852"
        assert error_1.loc_marc == "852"
        assert error_2.type == "extra_forbidden"
        assert error_2.loc == ("fields", "949")
        assert error_2.input == "949"
        assert error_2.ctx is None
        assert error_2.msg == "Extra field: 949"
        assert error_2.loc_marc == "949"

    def test_MarcError_string_type(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("s")
        stub_pamphlet_record["960"].add_subfield("s", 1.00)
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        errors = [MarcError(i) for i in e.value.errors()]
        error_locs = [i.loc for i in errors]
        error_types = [i.type for i in errors]
        errors_loc_marc = [i.loc_marc for i in errors]
        assert len(errors) == 2
        assert sorted(error_locs) == sorted(
            [
                ("fields", "960", "subfields", 0, "s"),
                ("fields", "960", "order_price"),
            ]
        )
        assert all(isinstance(i.input, float) for i in errors)
        assert error_types == ["string_type", "string_type"]
        assert errors_loc_marc == ["960$s", "960$s"]


class TestMarcValidationErrorMonograph:
    def test_MarcValidationError_literal_error(self, stub_record):
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 1
        assert errors["invalid_fields"] == [
            {
                "error_type": "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'",
                "field": "960$t",
                "input": "foo",
            },
        ]
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_string_type(self, stub_record):
        stub_record["960"].delete_subfield("s")
        stub_record["960"].add_subfield("s", 1.00)
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 2
        assert errors["invalid_fields"][0] == {
            "error_type": "Input should be a valid string. Examples: ['100', '200']",
            "field": "960$s",
            "input": 1.0,
        }
        assert errors["invalid_fields"][1] == {
            "error_type": "Input should be a valid string. Examples: ['100', '200']",
            "field": "960$s",
            "input": 1.0,
        }
        assert len(errors["invalid_fields"]) == 2
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_string_pattern(self, stub_record):
        stub_record["960"].delete_subfield("s")
        stub_record["960"].add_subfield("s", "1.00")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 1
        assert errors["invalid_fields"] == [
            {
                "error_type": "String should match pattern. Examples: ['100', '200']",
                "field": "960$s",
                "input": "1.00",
            }
        ]
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_extra_fields(self, stub_record):
        record_dict = stub_record.as_dict()
        record_dict["fields"].append(
            {"003": {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]}}
        )
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 4
        assert len(errors["missing_fields"]) == 0
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["extra_fields"]) == 3
        assert len(errors["order_item_mismatches"]) == 0
        assert errors["missing_fields"] == []
        assert errors["invalid_fields"] == [
            {
                "field": "003",
                "error_type": "Input should be a valid string. Examples: ['OCoLC', 'DLC']",
                "input": {"ind1": " ", "ind2": " ", "subfields": [{"a": "foo"}]},
            }
        ]
        assert errors["extra_fields"] == ["003ind1", "003ind2", "003subfields"]
        assert errors["order_item_mismatches"] == []

    def test_MarcValidationError_multiple_errors_order_item(self, stub_record):
        stub_record.remove_fields("980")
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "ReCAP-24-119100")
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "PAH")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 3
        assert len(errors["missing_fields"]) == 1
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 1
        assert errors["missing_fields"] == ["980"]
        assert errors["invalid_fields"] == [
            {
                "field": "852$h",
                "input": "ReCAP-24-119100",
                "error_type": "String should match pattern. Examples: ['ReCAP 23-000001', 'ReCAP 24-100001', 'ReCAP 25-222000']",
            }
        ]
        assert errors["extra_fields"] == []
        assert errors["order_item_mismatches"] == [
            {"order_location": "PAH", "item_location": "rcmf2", "item_type": "55"}
        ]


class TestMarcValidationErrorOther:
    def test_MarcValidationError_literal_error(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("t")
        stub_pamphlet_record["960"].add_subfield("t", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 1
        assert errors["invalid_fields"] == [
            {
                "error_type": "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'",
                "field": "960$t",
                "input": "foo",
            },
        ]
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_string_type(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("s")
        stub_pamphlet_record["960"].add_subfield("s", 1.00)
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 2
        assert errors["invalid_fields"][0] == {
            "error_type": "Input should be a valid string. Examples: ['100', '200']",
            "field": "960$s",
            "input": 1.0,
        }
        assert errors["invalid_fields"][1] == {
            "error_type": "Input should be a valid string. Examples: ['100', '200']",
            "field": "960$s",
            "input": 1.0,
        }
        assert len(errors["invalid_fields"]) == 2
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_string_pattern(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("s")
        stub_pamphlet_record["960"].add_subfield("s", "1.00")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 1
        assert errors["invalid_fields"] == [
            {
                "error_type": "String should match pattern. Examples: ['100', '200']",
                "field": "960$s",
                "input": "1.00",
            }
        ]
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["missing_fields"]) == 0
        assert len(errors["extra_fields"]) == 0
        assert len(errors["order_item_mismatches"]) == 0

    def test_MarcValidationError_extra_fields(self, stub_record):
        stub_record["300"].delete_subfield("a")
        stub_record["300"].add_subfield("a", "5 pages :")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 2
        assert len(errors["missing_fields"]) == 0
        assert len(errors["invalid_fields"]) == 0
        assert len(errors["extra_fields"]) == 2
        assert len(errors["order_item_mismatches"]) == 0
        assert errors["missing_fields"] == []
        assert errors["invalid_fields"] == []
        assert errors["extra_fields"] == ["852", "949"]
        assert errors["order_item_mismatches"] == []

    def test_MarcValidationError_multiple_errors(
        self, stub_pamphlet_record, stub_call_no
    ):
        stub_pamphlet_record.remove_fields("980")
        stub_pamphlet_record["960"].delete_subfield("t")
        stub_pamphlet_record["960"].add_subfield("t", "FOO")
        stub_pamphlet_record.add_field(stub_call_no)
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        errors = MarcValidationError(e.value.errors()).to_dict()
        assert errors["error_count"] == 3
        assert len(errors["missing_fields"]) == 1
        assert len(errors["invalid_fields"]) == 1
        assert len(errors["extra_fields"]) == 1
        assert len(errors["order_item_mismatches"]) == 0
        assert errors["missing_fields"] == ["980"]
        assert errors["invalid_fields"] == [
            {
                "error_type": "Input should be: 'MAB', 'MAF', 'MAG', 'MAL', 'MAP', 'MAS', 'PAD', 'PAH', 'PAM', 'PAT' or 'SC'",
                "field": "960$t",
                "input": "FOO",
            }
        ]
        assert errors["extra_fields"] == ["852"]
        assert errors["order_item_mismatches"] == []

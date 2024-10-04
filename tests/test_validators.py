from contextlib import nullcontext as does_not_raise
from pydantic import ValidationError
import pytest
from record_validator.validators import (
    validate_leader,
    validate_all,
    validate_fields,
    validate_order_items,
)


def test_validate_leader(stub_record):
    leader_str = "00454cam a22001575i 4500"
    stub_record_leader = stub_record.leader
    valid_leader_str = validate_leader(leader_str)
    valid_leader_marc = validate_leader(stub_record_leader)
    assert valid_leader_str == leader_str
    assert isinstance(valid_leader_str, str)
    assert valid_leader_marc == "00454cam a22001575i 4500"
    assert isinstance(valid_leader_marc, str)


class TestValidateMonograph:
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

    def test_validate_all_order_item_not_checked_missing(self, stub_record):
        stub_record["949"].delete_subfield("t")
        stub_record["949"].add_subfield("t", "2")
        stub_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "missing"

    def test_validate_all_order_item_not_checked_extra(self, stub_record, stub_order):
        stub_record["949"].delete_subfield("t")
        stub_record["949"].add_subfield("t", "2")
        stub_record.add_field(stub_order)
        with pytest.raises(ValidationError) as e:
            validate_all(stub_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "extra_forbidden"

    def test_validate_order_items(self, stub_record):
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", "MAL")
        errors = []
        with does_not_raise():
            errors.extend(validate_order_items(stub_record.as_dict()["fields"]))
        assert len(errors) == 1
        assert isinstance(errors, list)
        assert (
            "Invalid combination of item_type, order_location and item_location"
            in str(errors[0]["type"])
        )
        assert errors[0]["input"] == {
            "order_location": "MAL",
            "item_location": "rcmf2",
            "item_type": "55",
        }

    def test_validate_order_items_no_errors(self, stub_record):
        errors = []
        with does_not_raise():
            errors.extend(validate_order_items(stub_record.as_dict()["fields"]))
        assert len(errors) == 0

    def test_validate_fields_extra(self, stub_record, stub_order):
        errors = []
        stub_record.add_field(stub_order)
        with does_not_raise():
            errors.extend(
                validate_fields(fields=stub_record.fields, record_type="evp_monograph")
            )
        field_tags = [str(i.tag) for i in stub_record.fields]
        assert len(errors) == 1
        assert isinstance(errors, list)
        assert str(errors[0]["type"]) == "Extra field: 960"
        assert errors[0]["input"] == "960"
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "852",
                "901",
                "910",
                "949",
                "960",
                "960",
                "980",
            ]
        )

    def test_validate_fields_missing(self, stub_record):
        errors = []
        stub_record.remove_fields("960", "949", "852")
        with does_not_raise():
            errors.extend(
                validate_fields(fields=stub_record.fields, record_type="evp_monograph")
            )
        field_tags = [str(i.tag) for i in stub_record.fields]
        assert len(errors) == 3
        assert isinstance(errors, list)
        assert sorted([str(i["type"]) for i in errors]) == sorted(
            ["Field required: 852", "Field required: 949", "Field required: 960"]
        )
        assert sorted([str(i["input"]) for i in errors]) == sorted(
            ["852", "949", "960"]
        )
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "901",
                "910",
                "980",
            ]
        )


class TestValidatePamphlet:
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

    def test_validate_fields_extra(self, stub_record, stub_order):
        errors = []
        stub_record.add_field(stub_order)
        stub_record["300"].delete_subfield("a")
        stub_record["300"].add_subfield("a", "5 pages")
        with does_not_raise():
            errors.extend(
                validate_fields(fields=stub_record.fields, record_type="evp_other")
            )
        field_tags = [str(i.tag) for i in stub_record.fields]
        assert len(errors) == 3
        assert isinstance(errors, list)
        assert sorted([str(i["type"]) for i in errors]) == sorted(
            ["Extra field: 960", "Extra field: 949", "Extra field: 852"]
        )
        assert sorted([str(i["input"]) for i in errors]) == sorted(
            ["960", "949", "852"]
        )
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "852",
                "901",
                "910",
                "949",
                "960",
                "960",
                "980",
            ]
        )

    def test_validate_fields_missing(self, stub_pamphlet_record):
        errors = []
        stub_pamphlet_record.remove_fields("960", "980")
        with does_not_raise():
            errors.extend(
                validate_fields(
                    fields=stub_pamphlet_record.fields, record_type="evp_other"
                )
            )
        field_tags = [str(i.tag) for i in stub_pamphlet_record.fields]
        assert len(errors) == 2
        assert isinstance(errors, list)
        assert sorted([str(i["type"]) for i in errors]) == sorted(
            ["Field required: 960", "Field required: 980"]
        )
        assert sorted([str(i["input"]) for i in errors]) == sorted(["980", "960"])
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "901",
                "910",
            ]
        )


class TestValidateAuxamOther:
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

    def test_validate_all_extra_field(self, stub_aux_other_record, stub_auxam_item):
        stub_aux_other_record.add_field(stub_auxam_item)
        with pytest.raises(ValidationError) as e:
            validate_all(stub_aux_other_record.as_dict()["fields"])
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "extra_forbidden"

    def test_validate_fields_extra(self, stub_aux_other_record, stub_auxam_item):
        errors = []
        stub_aux_other_record.add_field(stub_auxam_item)
        with does_not_raise():
            errors.extend(
                validate_fields(
                    fields=stub_aux_other_record.fields, record_type="auxam_other"
                )
            )
        field_tags = [str(i.tag) for i in stub_aux_other_record.fields]
        assert len(errors) == 1
        assert isinstance(errors, list)
        assert str(errors[0]["type"]) == "Extra field: 949"
        assert errors[0]["input"] == "949"
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "852",
                "901",
                "910",
                "949",
                "960",
                "980",
            ]
        )

    def test_validate_fields_missing(self, stub_aux_other_record):
        errors = []
        stub_aux_other_record.remove_fields("960", "980")
        with does_not_raise():
            errors.extend(
                validate_fields(
                    fields=stub_aux_other_record.fields, record_type="auxam_other"
                )
            )
        field_tags = [str(i.tag) for i in stub_aux_other_record.fields]
        assert len(errors) == 2
        assert isinstance(errors, list)
        assert sorted([str(i["type"]) for i in errors]) == sorted(
            ["Field required: 960", "Field required: 980"]
        )
        assert sorted([str(i["input"]) for i in errors]) == sorted(["960", "980"])
        assert sorted(field_tags) == sorted(
            [
                "001",
                "008",
                "050",
                "245",
                "300",
                "852",
                "901",
                "910",
            ]
        )

import pytest
from pydantic import ValidationError
from contextlib import nullcontext as does_not_raise
from pymarc import Leader, MARCReader
from record_validator.marc_models import RecordModel


class TestRecordModelMonograph:
    def test_RecordModel_valid(self):
        model = RecordModel(
            leader="00000cam a2200000 a 4500",
            fields=[
                {"008": "200101s2001    xx      b    000 0 eng  d"},
                {
                    "050": {
                        "ind1": " ",
                        "ind2": "4",
                        "subfields": [{"a": "F00"}, {"b": ".F00"}],
                    }
                },
                {"245": {"ind1": "0", "ind2": "0", "subfields": [{"a": "The Title"}]}},
                {"300": {"ind1": " ", "ind2": " ", "subfields": [{"a": "100 pages"}]}},
                {
                    "852": {
                        "ind1": "8",
                        "ind2": " ",
                        "subfields": [{"h": "ReCAP 24-111111"}],
                    }
                },
                {"901": {"ind1": " ", "ind2": " ", "subfields": [{"a": "EVP"}]}},
                {"910": {"ind1": " ", "ind2": " ", "subfields": [{"a": "RL"}]}},
                {
                    "960": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [{"s": "100"}, {"t": "MAL"}, {"u": "123456apprv"}],
                    }
                },
                {
                    "980": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [
                            {"a": "240101"},
                            {"b": "100"},
                            {"c": "0"},
                            {"d": "0"},
                            {"f": "1"},
                            {"e": "100"},
                            {"g": "1"},
                        ],
                    }
                },
                {
                    "949": {
                        "ind1": " ",
                        "ind2": "1",
                        "subfields": [
                            {"z": "8528"},
                            {"a": "ReCAP 24-111111"},
                            {"i": "33433123456789"},
                            {"p": "1.00"},
                            {"v": "EVP"},
                            {"h": "43"},
                            {"l": "rc2ma"},
                            {"t": "55"},
                            {"c": "1"},
                            {"u": "foo"},
                            {"m": "bar"},
                        ],
                    }
                },
            ],
        )
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_str_leader(self, stub_record):
        assert isinstance(stub_record.leader, str)
        model = RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_leader(self, stub_record):
        record = stub_record.as_marc21()
        reader = MARCReader(record)
        record = next(reader)
        assert isinstance(record.leader, Leader)
        model = RecordModel(leader=record.leader, fields=record.fields)
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_dict_valid(self, stub_record):
        record_dict = stub_record.as_dict()
        with does_not_raise():
            RecordModel(**record_dict)

    def test_RecordModel_from_marc_multiple_items(self, stub_record, stub_evp_item):
        stub_record.add_field(stub_evp_item)
        with does_not_raise():
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)

    def test_RecordModel_from_marc_dict_multiple_items(
        self, stub_record, stub_evp_item
    ):
        stub_record.add_field(stub_evp_item)
        record_dict = stub_record.as_dict()
        with does_not_raise():
            RecordModel(**record_dict)

    def test_RecordModel_from_marc_invalid(self, stub_record):
        stub_record.remove_fields("901")
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 2
        assert sorted([i["type"] for i in e.value.errors()]) == sorted(
            ["missing", "string_too_short"]
        )

    def test_RecordModel_invalid(self):
        record_dict = {
            "leader": "00000cam a2200000 a 4500",
            "fields": [
                {"245": {"ind1": "0", "ind2": "0", "subfields": [{"a": "The Title"}]}},
                {
                    "852": {
                        "ind1": "8",
                        "ind2": " ",
                        "subfields": [{"h": "foo"}],
                    }
                },
                {"901": {"ind1": " ", "ind2": " ", "subfields": [{"a": "EVP"}]}},
                {"910": {"ind1": " ", "ind2": " ", "subfields": [{"a": "RL"}]}},
                {
                    "960": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [{"s": "100"}, {"t": "bar"}, {"u": "123456apprv"}],
                    }
                },
                {
                    "980": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [
                            {"a": "240101"},
                            {"b": "100"},
                            {"c": "0"},
                            {"d": "0"},
                            {"f": "1"},
                            {"e": "100"},
                            {"g": "1"},
                        ],
                    }
                },
                {
                    "949": {
                        "ind1": " ",
                        "ind2": "1",
                        "subfields": [
                            {"z": "8528"},
                            {"a": "ReCAP 24-111111"},
                            {"i": "33433123456789"},
                            {"p": "1.00"},
                            {"v": "EVP"},
                            {"h": "43"},
                            {"l": "rc2ma"},
                            {"t": "55"},
                            {"c": "1"},
                            {"u": "foo"},
                            {"m": "bar"},
                        ],
                    }
                },
            ],
        }
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 3
        assert sorted([i["type"] for i in e.value.errors()]) == sorted(
            ["literal_error", "string_too_short", "missing"]
        )

    def test_RecordModel_missing_field(self, stub_record):
        stub_record.remove_fields("852")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["missing"]

    def test_RecordModel_string_too_short(self, stub_record):
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["string_too_short"]

    def test_RecordModel_string_too_long(self, stub_record):
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "ReCAP 11-1111111111")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["string_too_long"]

    def test_RecordModel_string_pattern_mismatch(self, stub_record):
        stub_record["852"].delete_subfield("h")
        stub_record["852"].add_subfield("h", "ReCAP 11-111111")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["string_pattern_mismatch"]

    def test_RecordModel_literal_error(self, stub_record):
        stub_record["901"].delete_subfield("a")
        stub_record["901"].add_subfield("a", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["literal_error"]

    @pytest.mark.parametrize(
        "leader_value, leader_error",
        [
            ("foo", "string_too_short"),
            ("bar", "string_too_short"),
            ("foobarfoobarfoobarfoobar", "string_pattern_mismatch"),
        ],
    )
    def test_RecordModel_invalid_leader(
        self,
        stub_record,
        leader_value,
        leader_error,
    ):
        record_dict = stub_record.as_dict()
        record_dict["leader"] = leader_value
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == leader_error

    @pytest.mark.parametrize(
        "fields_value",
        [{}, None],
    )
    def test_RecordModel_invalid_fields(
        self,
        stub_record,
        fields_value,
    ):
        record_dict = stub_record.as_dict()
        record_dict["fields"] = fields_value
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 2
        assert e.value.errors()[0]["type"] == "list_type"

    @pytest.mark.parametrize(
        "order_location_value,item_location_value,item_type_value,",
        [
            ("MAL", "rc2ma", "55"),
            ("MAL", None, None),
            ("MAL", None, "55"),
            ("MAL", "rc2ma", None),
            ("MAB", "rcmb2", "2"),
            ("MAS", "rcmb2", "2"),
            ("MAF", "rcmf2", "55"),
            ("MAF", "rcmf2", None),
            ("MAG", "rcmg2", "55"),
            ("MAG", "rcmg2", None),
        ],
    )
    def test_RecordModel_valid_location_combos(
        self, stub_record, order_location_value, item_location_value, item_type_value
    ):
        stub_record["949"].delete_subfield("l")
        stub_record["949"].delete_subfield("t")
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", order_location_value)
        if item_location_value is not None:
            stub_record["949"].add_subfield("l", item_location_value)
        if item_type_value is not None:
            stub_record["949"].add_subfield("t", item_type_value)
        with does_not_raise():
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)

    def test_RecordModel_order_item_data_not_checked(self, stub_record):
        stub_record["949"].delete_subfield("t")
        stub_record["949"].add_subfield("t", "2")
        stub_record["960"].delete_subfield("t")
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        error_types = [error["type"] for error in e.value.errors()]
        assert len(e.value.errors()) == 1
        assert "order_item_mismatch" not in error_types
        assert error_types == ["missing"]

    @pytest.mark.parametrize(
        "order_location_value,item_location_value,item_type_value,",
        [
            ("MAB", "rc2ma", "55"),
            ("MAS", None, None),
            ("MAG", "rcmf2", "55"),
            ("MAF", "rc2ma", None),
            ("MAL", "rcmg2", "55"),
        ],
    )
    def test_RecordModel_invalid_order_item_data(
        self, stub_record, order_location_value, item_location_value, item_type_value
    ):
        stub_record["949"].delete_subfield("l")
        stub_record["949"].delete_subfield("t")
        stub_record["960"].delete_subfield("t")
        stub_record["960"].add_subfield("t", order_location_value)
        if item_location_value is not None:
            stub_record["949"].add_subfield("l", item_location_value)
        if item_type_value is not None:
            stub_record["949"].add_subfield("t", item_type_value)
        with pytest.raises(ValidationError) as e:
            RecordModel(leader=stub_record.leader, fields=stub_record.fields)
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == "order_item_mismatch"

    def test_RecordModel_invalid_order_item_data_multiple(
        self,
        stub_record_multiple_items,
    ):
        stub_record_multiple_items["949"].delete_subfield("l")
        stub_record_multiple_items["949"].add_subfield("l", "rcmg2")
        stub_record_multiple_items["960"].delete_subfield("t")
        stub_record_multiple_items["960"].add_subfield("t", "MAP")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_record_multiple_items.leader,
                fields=stub_record_multiple_items.fields,
            )
        assert len(e.value.errors()) == 2
        assert e.value.errors()[0]["type"] == "order_item_mismatch"


class TestRecordModelPamphlet:
    def test_RecordModel_valid(self):
        model = RecordModel(
            leader="00000cam a2200000 a 4500",
            fields=[
                {"008": "200101s2001    xx      b    000 0 eng  d"},
                {
                    "050": {
                        "ind1": " ",
                        "ind2": "4",
                        "subfields": [{"a": "F00"}, {"b": ".F00"}],
                    }
                },
                {"245": {"ind1": "0", "ind2": "0", "subfields": [{"a": "The Title"}]}},
                {"300": {"ind1": " ", "ind2": " ", "subfields": [{"a": "5 pages"}]}},
                {"901": {"ind1": " ", "ind2": " ", "subfields": [{"a": "EVP"}]}},
                {"910": {"ind1": " ", "ind2": " ", "subfields": [{"a": "RL"}]}},
                {
                    "960": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [{"s": "100"}, {"t": "MAL"}, {"u": "123456apprv"}],
                    }
                },
                {
                    "980": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [
                            {"a": "240101"},
                            {"b": "100"},
                            {"c": "0"},
                            {"d": "0"},
                            {"f": "1"},
                            {"e": "100"},
                            {"g": "1"},
                        ],
                    }
                },
            ],
        )
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_str_leader(self, stub_pamphlet_record):
        assert isinstance(stub_pamphlet_record.leader, str)
        model = RecordModel(
            leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
        )
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_leader(self, stub_pamphlet_record):
        record = stub_pamphlet_record.as_marc21()
        reader = MARCReader(record)
        record = next(reader)
        assert isinstance(record.leader, Leader)
        model = RecordModel(leader=record.leader, fields=record.fields)
        assert list(model.model_dump().keys()) == ["leader", "fields"]

    def test_RecordModel_from_marc_dict_valid(self, stub_pamphlet_record):
        record_dict = stub_pamphlet_record.as_dict()
        with does_not_raise():
            RecordModel(**record_dict)

    def test_RecordModel_invalid(self):
        record_dict = {
            "leader": "00000cam a2200000 a 4500",
            "fields": [
                {"008": "200101s2001    xx      b    000 0 eng  d"},
                {
                    "050": {
                        "ind1": " ",
                        "ind2": "4",
                        "subfields": [{"a": "F00"}, {"b": ".F00"}],
                    }
                },
                {"245": {"ind1": "0", "ind2": "0", "subfields": [{"a": "The Title"}]}},
                {"300": {"ind1": " ", "ind2": " ", "subfields": [{"a": "5 pages"}]}},
                {"901": {"ind1": " ", "ind2": " ", "subfields": [{"a": "FOO"}]}},
                {"910": {"ind1": " ", "ind2": " ", "subfields": [{"a": "RL"}]}},
                {
                    "960": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [{"s": "100"}, {"t": "MAL"}, {"u": "123456apprv"}],
                    }
                },
                {
                    "980": {
                        "ind1": " ",
                        "ind2": " ",
                        "subfields": [
                            {"a": "240101"},
                            {"b": "1.00"},
                            {"c": "0"},
                            {"d": "0"},
                            {"f": "1"},
                            {"e": "100"},
                        ],
                    }
                },
            ],
        }
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 3
        assert sorted([i["type"] for i in e.value.errors()]) == sorted(
            ["literal_error", "string_pattern_mismatch", "missing"]
        )

    def test_RecordModel_missing_field(self, stub_pamphlet_record):
        stub_pamphlet_record.remove_fields("901")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["missing"]

    def test_RecordModel_string_pattern_mismatch(self, stub_pamphlet_record):
        stub_pamphlet_record["960"].delete_subfield("s")
        stub_pamphlet_record["960"].add_subfield("s", "1.00")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["string_pattern_mismatch"]

    def test_RecordModel_literal_error(self, stub_pamphlet_record):
        stub_pamphlet_record["901"].delete_subfield("a")
        stub_pamphlet_record["901"].add_subfield("a", "foo")
        with pytest.raises(ValidationError) as e:
            RecordModel(
                leader=stub_pamphlet_record.leader, fields=stub_pamphlet_record.fields
            )
        assert len(e.value.errors()) == 1
        assert [i["type"] for i in e.value.errors()] == ["literal_error"]

    @pytest.mark.parametrize(
        "leader_value, leader_error",
        [
            ("foo", "string_too_short"),
            ("bar", "string_too_short"),
            ("foobarfoobarfoobarfoobar", "string_pattern_mismatch"),
        ],
    )
    def test_RecordModel_invalid_leader(
        self,
        stub_pamphlet_record,
        leader_value,
        leader_error,
    ):
        record_dict = stub_pamphlet_record.as_dict()
        record_dict["leader"] = leader_value
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 1
        assert e.value.errors()[0]["type"] == leader_error

    @pytest.mark.parametrize(
        "fields_value",
        [{}, None],
    )
    def test_RecordModel_invalid_fields(
        self,
        stub_pamphlet_record,
        fields_value,
    ):
        record_dict = stub_pamphlet_record.as_dict()
        record_dict["fields"] = fields_value
        with pytest.raises(ValidationError) as e:
            RecordModel(**record_dict)
        assert len(e.value.errors()) == 2
        assert e.value.errors()[0]["type"] == "list_type"

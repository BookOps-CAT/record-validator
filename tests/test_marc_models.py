import pytest
from pydantic import ValidationError
from contextlib import nullcontext as does_not_raise
from pymarc import Field as MarcField
from pymarc import Subfield
from record_validator.marc_models import MonographRecord


def test_MonographRecord_valid():
    model = MonographRecord(
        leader="00000cam a2200000 a 4500",
        fields=[
            {"008": "200101s2001    xx      b    000 0 eng  "},
            {
                "050": {
                    "ind1": " ",
                    "ind2": "4",
                    "subfields": [{"a": "F00"}, {"b": ".F00"}],
                }
            },
            {"245": {"ind1": "0", "ind2": "0", "subfields": [{"a": "The Title"}]}},
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


def test_MonographRecord_from_marc_valid(stub_record):
    with does_not_raise():
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)


def test_MonographRecord_from_marc_dict_valid(stub_record):
    record_dict = stub_record.as_dict()
    with does_not_raise():
        MonographRecord(**record_dict)


def test_MonographRecord_from_marc_multiple_items(stub_record):
    stub_record.add_field(
        MarcField(
            tag="949",
            indicators=[" ", "1"],
            subfields=[
                Subfield(code="z", value="8528"),
                Subfield(code="a", value="ReCAP 24-000000"),
                Subfield(code="i", value="33433123456789"),
                Subfield(code="p", value="1.00"),
                Subfield(code="v", value="EVP"),
                Subfield(code="h", value="43"),
                Subfield(code="l", value="rcmf2"),
                Subfield(code="t", value="55"),
            ],
        )
    )
    with does_not_raise():
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)


def test_MonographRecord_from_marc_dict_multiple_items(stub_record):
    stub_record.add_field(
        MarcField(
            tag="949",
            indicators=[" ", "1"],
            subfields=[
                Subfield(code="z", value="8528"),
                Subfield(code="a", value="ReCAP 24-000000"),
                Subfield(code="i", value="33433123456789"),
                Subfield(code="p", value="1.00"),
                Subfield(code="v", value="EVP"),
                Subfield(code="h", value="43"),
                Subfield(code="l", value="rcmf2"),
                Subfield(code="t", value="55"),
            ],
        )
    )
    record_dict = stub_record.as_dict()
    with does_not_raise():
        MonographRecord(**record_dict)


def test_MonographRecord_from_marc_invalid(stub_record):
    stub_record.remove_fields("901", "852")
    stub_record.add_field(
        MarcField(
            tag="852",
            indicators=["8", " "],
            subfields=[Subfield(code="h", value="foo")],
        )
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 2
    assert sorted([i["type"] for i in e.value.errors()]) == sorted(
        ["missing_required_field", "string_pattern_mismatch"]
    )


def test_MonographRecord_invalid():
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
        MonographRecord(**record_dict)
    assert len(e.value.errors()) == 3
    assert sorted([i["type"] for i in e.value.errors()]) == sorted(
        ["literal_error", "string_pattern_mismatch", "missing_required_field"]
    )


def test_MonographRecord_missing_field(stub_record):
    stub_record.remove_fields("852")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 1
    assert sorted([i["type"] for i in e.value.errors()]) == sorted(
        ["missing_required_field"]
    )


def test_MonographRecord_string_pattern_mismatch(stub_record):
    stub_record.remove_fields("852")
    stub_record.add_field(
        MarcField(
            tag="852",
            indicators=["8", " "],
            subfields=[Subfield(code="h", value="foo")],
        )
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 1
    assert sorted([i["type"] for i in e.value.errors()]) == sorted(
        ["string_pattern_mismatch"]
    )


def test_MonographRecord_literal_error(stub_record):
    stub_record.remove_fields("901")
    stub_record.add_field(
        MarcField(
            tag="901",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="foo")],
        )
    )
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 1
    assert sorted([i["type"] for i in e.value.errors()]) == sorted(["literal_error"])


@pytest.mark.parametrize(
    "leader_value, leader_error",
    [
        ("foo", "string_too_short"),
        ("bar", "string_too_short"),
        ("foobarfoobarfoobarfoobar", "string_pattern_mismatch"),
    ],
)
def test_MonographRecord_invalid_leader(
    stub_record,
    leader_value,
    leader_error,
):
    record_dict = stub_record.as_dict()
    record_dict["leader"] = leader_value
    with pytest.raises(ValidationError) as e:
        MonographRecord(**record_dict)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == leader_error


@pytest.mark.parametrize(
    "fields_value",
    [{}, None],
)
def test_MonographRecord_invalid_fields(
    stub_record,
    fields_value,
):
    record_dict = stub_record.as_dict()
    record_dict["fields"] = fields_value
    with pytest.raises(ValidationError) as e:
        MonographRecord(**record_dict)
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
def test_MonographRecord_valid_location_combos(
    stub_record, order_location_value, item_location_value, item_type_value
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
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)


def test_MonographRecord_order_item_data_not_checked(stub_record):
    stub_record["949"].delete_subfield("t")
    stub_record["949"].add_subfield("t", "2")
    stub_record["960"].delete_subfield("t")
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
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
def test_MonographRecord_invalid_order_item_data(
    stub_record, order_location_value, item_location_value, item_type_value
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
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 1
    assert e.value.errors()[0]["type"] == "order_item_mismatch"


def test_MonographRecord_invalid_order_item_data_multiple(stub_record, stub_item):
    stub_record["949"].delete_subfield("l")
    stub_record["949"].add_subfield("l", "rcmg2")
    stub_record["960"].delete_subfield("t")
    stub_record["960"].add_subfield("t", "MAP")
    stub_record.add_field(stub_item)
    with pytest.raises(ValidationError) as e:
        MonographRecord(leader=stub_record.leader, fields=stub_record.fields)
    assert len(e.value.errors()) == 2
    assert e.value.errors()[0]["type"] == "order_item_mismatch"


# def test_MonographRecord_invalid_material_type(
#     mock_bib_call_no,
#     mock_bib_vendor_code,
#     mock_lc_class,
#     mock_library,
#     mock_order_field,
#     mock_invoice_field,
#     mock_item_fields,
# ):
#     with pytest.raises(ValidationError) as e:
#         MonographRecord(
#             leader="00000cam a2200000 a 4500",
#             fields=[{"245": {"a": "The Title"}}],
#             bib_call_no=mock_bib_call_no,
#             bib_vendor_code=mock_bib_vendor_code,
#             lc_class=mock_lc_class,
#             library_field=mock_library,
#             material_type=None,
#             order_field=mock_order_field,
#             invoice_field=mock_invoice_field,
#             item_fields=mock_item_fields,
#         )
#     assert len(e.value.errors()) == 1
#     assert e.value.errors()[0]["type"] == "literal_error"

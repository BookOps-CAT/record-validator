import pytest
from record_validator.utils import (
    dict2subfield,
    field2dict,
    get_record_type,
)


@pytest.mark.parametrize(
    "tag, code, expected",
    [
        ("050", "a", "F00"),
        ("245", "a", "Title :"),
        ("300", "a", "100 pages :"),
        ("901", "a", "EVP"),
        ("949", "v", "EVP"),
    ],
)
def test_dict2subfield(stub_record, tag, code, expected):
    record_dict = stub_record.as_dict()
    field = [i for i in record_dict["fields"] if tag in i.keys()][0]
    assert dict2subfield(field, code) == [expected]


def test_dict2subfield_test():
    field = {"852": {"ind1": "8", "ind2": " ", "subfields": [{"h": "ReCAP 24-100000"}]}}
    assert dict2subfield(field, "h") == ["ReCAP 24-100000"]


def test_field2dict_marc(stub_record):
    fields = stub_record.fields
    assert len([field2dict(i) for i in fields]) == len(fields)
    assert field2dict(fields[0]) == {"001": "on1381158740"}


def test_field2dict_pymarc_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    fields = stub_record_dict["fields"]
    assert len([field2dict(i) for i in fields]) == len(fields)
    assert field2dict(fields[0]) == {"001": "on1381158740"}


def test_field2dict_dict():
    fields = [
        {"tag": "001", "value": "on1381158740"},
        {"tag": "300", "ind1": " ", "ind2": " ", "subfields": [{"a": "100 pages :"}]},
    ]
    assert len([field2dict(i) for i in fields]) == len(fields)
    assert field2dict(fields[0]) == {"001": "on1381158740"}
    assert field2dict(fields[1]) == {
        "300": {"ind1": " ", "ind2": " ", "subfields": [{"a": "100 pages :"}]}
    }


def test_get_record_type_monograph(stub_leila_monograph):
    assert get_record_type(fields=stub_leila_monograph.fields) == "leila_monograph"


def test_get_record_type_dance(stub_dance_record):
    assert get_record_type(fields=stub_dance_record.fields) == "evp_other"


def test_get_record_type_pamphlet(stub_pamphlet_record):
    assert get_record_type(fields=stub_pamphlet_record.fields) == "evp_other"


def test_get_record_type_catalogue(stub_catalogue_record):
    assert get_record_type(fields=stub_catalogue_record.fields) == "evp_other"


def test_get_record_type_multivol(stub_multivol_record):
    assert get_record_type(fields=stub_multivol_record.fields) == "evp_other"


def test_get_record_type_auxam_other(stub_aux_other_record):
    assert get_record_type(fields=stub_aux_other_record.fields) == "auxam_other"


def test_get_record_type_bad_input():
    assert get_record_type(fields=["foo"]) == "other"


def test_get_record_type_dict(stub_record):
    record_dict = stub_record.as_dict()
    assert get_record_type(fields=record_dict["fields"]) == "evp_monograph"

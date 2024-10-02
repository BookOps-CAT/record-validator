import pytest
from record_validator.validators import get_subfield_from_code


@pytest.mark.parametrize(
    "tag, code, expected",
    [("960", "t", ["MAF"]), ("050", "a", ["F00"])],
)
def test_get_subfield_from_code_marc(stub_record, tag, code, expected):
    field = stub_record.get(tag)
    assert get_subfield_from_code(field=field, tag=tag, code=code) == expected


def test_get_subfield_from_code_dict():
    field = {
        "tag": "980",
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"a": "foo"}, {"b": "bar"}, {"c": "baz"}],
    }
    assert get_subfield_from_code(field=field, tag="980", code="a") == ["foo"]
    assert get_subfield_from_code(field=field, tag="980", code="b") == ["bar"]
    assert get_subfield_from_code(field=field, tag="980", code="c") == ["baz"]


def test_get_subfield_from_code_pymarc_dict(stub_record):
    stub_record_dict = stub_record.as_dict()
    field = stub_record_dict["fields"][-1]
    assert get_subfield_from_code(field=field, tag="980", code="a") == ["240101"]


def test_get_subfield_from_code_None():
    field = {
        "tag": "980",
        "ind1": " ",
        "ind2": " ",
        "subfields": [{"a": "foo"}, {"b": "bar"}, {"c": "baz"}],
    }
    assert get_subfield_from_code(field=field, tag="980", code="z") == [None]


def test_get_subfield_from_code_other():
    field = ("980", " ", " ", [("a", "foo"), ("b", "bar"), ("c", "baz")])
    assert get_subfield_from_code(field=field, tag="980", code="a") is None

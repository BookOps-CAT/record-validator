import pytest
from record_validator.constants import AllFields, AllSubfields, ValidOrderItems


@pytest.mark.parametrize(
    "tag, model",
    [
        ("001", "ControlField001"),
        ("003", "ControlField003"),
        ("005", "ControlField005"),
        ("006", "ControlField006"),
        ("007", "ControlField007"),
        ("008", "ControlField008"),
        ("050", "LCClass"),
        ("901", "BibVendorCode"),
        ("910", "LibraryField"),
        ("960", "OrderField"),
        ("980", "InvoiceField"),
        ("949", "ItemField"),
        ("852", "BibCallNo"),
    ],
)
def test_AllFields_all_fields(tag, model):
    assert AllFields(tag).name == model


def test_AllFields_monograph_fields():
    assert sorted(AllFields.monograph_fields()) == sorted(["949", "852"])


def test_AllFields_required_fields():
    assert sorted(AllFields.required_fields()) == sorted(
        ["050", "901", "910", "960", "980"]
    )


def test_AllFields_control_fields():
    assert sorted(AllFields.control_fields()) == sorted(
        ["001", "003", "005", "006", "007", "008"]
    )


@pytest.mark.parametrize(
    "field_name, code",
    [
        ("call_no", "h"),
        ("vendor_code", "a"),
        ("lcc", "a"),
        ("order_price", "s"),
        ("invoice_price", "b"),
        ("item_barcode", "i"),
        ("item_vendor_code", "v"),
    ],
)
def test_AllSubfields(field_name, code):
    assert AllSubfields[field_name].value == code


@pytest.mark.parametrize(
    "field_name, mapping",
    [
        (
            "call_no",
            "subfields.h",
        ),
        (
            "invoice_net_price",
            "subfields.e",
        ),
        (
            "item_type",
            "subfields.t",
        ),
        (
            "lcc",
            "subfields.a",
        ),
        (
            "ind1",
            "ind1",
        ),
        (
            "ind2",
            "ind2",
        ),
        (
            "tag",
            "tag",
        ),
    ],
)
def test_AllSubfields_get_alias(field_name, mapping):
    alias = AllSubfields.get_alias(field_name)
    assert alias == mapping


def test_ValidOrderItems_to_list():
    assert ValidOrderItems.to_list() == [
        {"order_location": "MAB", "item_location": "rcmb2", "item_type": "2"},
        {"order_location": "MAS", "item_location": "rcmb2", "item_type": "2"},
        {"order_location": "MAF", "item_location": "rcmf2", "item_type": "55"},
        {"order_location": "MAF", "item_location": "rcmf2", "item_type": None},
        {"order_location": "MAG", "item_location": "rcmg2", "item_type": "55"},
        {"order_location": "MAG", "item_location": "rcmg2", "item_type": None},
        {"order_location": "MAL", "item_location": "rc2ma", "item_type": "55"},
        {"order_location": "MAL", "item_location": None, "item_type": "55"},
        {"order_location": "MAL", "item_location": "rc2ma", "item_type": None},
        {"order_location": "MAL", "item_location": None, "item_type": None},
        {"order_location": "MAP", "item_location": "rcmp2", "item_type": "2"},
        {"order_location": "PAH", "item_location": "rcph2", "item_type": "55"},
        {"order_location": "PAH", "item_location": "rcph2", "item_type": None},
        {"order_location": "PAM", "item_location": "rcpm2", "item_type": "55"},
        {"order_location": "PAM", "item_location": "rcpm2", "item_type": None},
        {"order_location": "PAT", "item_location": "rcpt2", "item_type": "55"},
        {"order_location": "PAT", "item_location": "rcpt2", "item_type": None},
        {"order_location": "SC", "item_location": "rc2cf", "item_type": "55"},
        {"order_location": "SC", "item_location": "rc2cf", "item_type": None},
    ]

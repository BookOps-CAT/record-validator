import pytest
from pymarc import Record, Subfield
from pymarc import Field as MarcField


@pytest.fixture
def stub_item():
    item_field = MarcField(
        tag="949",
        indicators=[" ", "1"],
        subfields=[
            Subfield(code="z", value="8528"),
            Subfield(code="a", value="ReCAP 23-100000"),
            Subfield(code="c", value="1"),
            Subfield(code="h", value="43"),
            Subfield(code="i", value="33433123456789"),
            Subfield(code="l", value="rcmf2"),
            Subfield(code="m", value="bar"),
            Subfield(code="p", value="1.00"),
            Subfield(code="t", value="55"),
            Subfield(code="u", value="foo"),
            Subfield(code="v", value="AUXAM"),
        ],
    )
    return item_field


@pytest.fixture
def stub_item_dict():
    return {
        "949": [
            {"z": "8528"},
            {"a": "ReCAP 23-100000"},
            {"c": "1"},
            {"h": "43"},
            {"i": "33433123456789"},
            {"l": "rcmf2"},
            {"m": "bar"},
            {"p": "1.00"},
            {"t": "55"},
            {"u": "foo"},
            {"v": "AUXAM"},
        ]
    }


@pytest.fixture
def stub_order():
    order_field = MarcField(
        tag="960",
        indicators=[" ", " "],
        subfields=[
            Subfield(code="s", value="100"),
            Subfield(code="t", value="MAF"),
            Subfield(code="u", value="123456apprv"),
        ],
    )
    return order_field


@pytest.fixture
def stub_invoice():
    invoice_field = MarcField(
        tag="980",
        indicators=[" ", " "],
        subfields=[
            Subfield(code="a", value="240101"),
            Subfield(code="b", value="100"),
            Subfield(code="c", value="100"),
            Subfield(code="d", value="000"),
            Subfield(code="e", value="200"),
            Subfield(code="f", value="123456"),
            Subfield(code="g", value="1"),
        ],
    )

    return invoice_field


@pytest.fixture
def stub_record(stub_item, stub_order, stub_invoice):
    bib = Record()
    bib.leader = "00454cam a22001575i 4500"
    bib.add_field(MarcField(tag="008", data="190306s2017    ht a   j      000 1 hat d"))
    bib.add_field(MarcField(tag="001", data="on1381158740"))
    bib.add_field(
        MarcField(
            tag="050",
            indicators=[" ", "4"],
            subfields=[
                Subfield(code="a", value="F00"),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="245",
            indicators=["0", "0"],
            subfields=[
                Subfield(code="a", value="Title :"),
                Subfield(
                    code="b",
                    value="subtitle /",
                ),
                Subfield(
                    code="c",
                    value="Author",
                ),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="300",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value="100 pages :"),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="852",
            indicators=["8", " "],
            subfields=[
                Subfield(code="h", value="ReCAP 23-100000"),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="901",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value="EVP"),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="910",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="a", value="RL"),
            ],
        )
    )
    bib.add_field(stub_item)
    bib.add_field(stub_order)
    bib.add_field(stub_invoice)
    return bib


@pytest.fixture
def stub_record_with_dupes(stub_record):
    dupe_record = stub_record
    dupe_record.add_field(
        MarcField(tag="050", indicators=[" ", "4"], subfields=[Subfield("h", "foo")])
    )
    dupe_record.add_field(
        MarcField(
            tag="852",
            indicators=["8", " "],
            subfields=[Subfield("h", "ReCAP 25-000000")],
        )
    )
    dupe_record.add_field(
        MarcField(tag="901", indicators=[" ", " "], subfields=[Subfield("a", "foo")])
    )
    dupe_record.add_field(
        MarcField(tag="910", indicators=[" ", " "], subfields=[Subfield("a", "foo")])
    )
    dupe_record.add_field(
        MarcField(
            tag="949",
            indicators=[" ", "1"],
            subfields=[
                Subfield(code="z", value="8528"),
                Subfield(code="a", value="ReCAP 24-100000"),
                Subfield(code="c", value="1"),
                Subfield(code="h", value="43"),
                Subfield(code="i", value="33433123456789"),
                Subfield(code="l", value="rc2ma"),
                Subfield(code="m", value="bar"),
                Subfield(code="p", value="1.00"),
                Subfield(code="t", value="55"),
                Subfield(code="u", value="foo"),
                Subfield(code="v", value="AUXAM"),
            ],
        )
    )
    dupe_record.add_field(
        MarcField(tag="980", indicators=[" ", " "], subfields=[Subfield("a", "foo")])
    )
    return dupe_record

import pytest
from pymarc import Field as MarcField
from pymarc import Record, Subfield


@pytest.fixture
def stub_call_no():
    return MarcField(
        tag="852",
        indicators=["8", " "],
        subfields=[Subfield(code="h", value="ReCAP 24-119100")],
    )


@pytest.fixture
def stub_order():
    return MarcField(
        tag="960",
        indicators=[" ", " "],
        subfields=[
            Subfield(code="s", value="200"),
            Subfield(code="t", value="MAF"),
            Subfield(code="u", value="123456apprv"),
        ],
    )


@pytest.fixture
def stub_auxam_item():
    return MarcField(
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


@pytest.fixture
def stub_evp_item():
    return MarcField(
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
            Subfield(code="v", value="EVP"),
        ],
    )


@pytest.fixture
def stub_record():
    bib = Record()
    bib.leader = "00454cam a22001575i 4500"
    bib.add_field(MarcField(tag="001", data="on1381158740"))
    bib.add_field(MarcField(tag="008", data="190306s2017    ht a   j      000 1 hat d"))
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
    bib.add_field(
        MarcField(
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
                Subfield(code="v", value="EVP"),
            ],
        )
    )
    bib.add_field(
        MarcField(
            tag="960",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="s", value="100"),
                Subfield(code="t", value="MAF"),
                Subfield(code="u", value="123456apprv"),
            ],
        )
    )
    bib.add_field(
        MarcField(
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
    )
    return bib


@pytest.fixture
def stub_record_multiple_items(stub_record):
    dupe_record = stub_record
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
                Subfield(code="l", value="rcmf2"),
                Subfield(code="m", value="bar"),
                Subfield(code="p", value="1.00"),
                Subfield(code="t", value="55"),
                Subfield(code="u", value="foo"),
                Subfield(code="v", value="EVP"),
            ],
        )
    )
    return dupe_record


@pytest.fixture
def stub_dance_record(stub_record):
    stub_record.remove_fields("949", "960")
    stub_record.add_field(
        MarcField(
            tag="949",
            indicators=[" ", "1"],
            subfields=[
                Subfield(code="z", value="8528"),
                Subfield(code="a", value="ReCAP 24-100000"),
                Subfield(code="c", value="1"),
                Subfield(code="h", value="43"),
                Subfield(code="i", value="33433123456789"),
                Subfield(code="l", value="rcpd2"),
                Subfield(code="m", value="bar"),
                Subfield(code="p", value="1.00"),
                Subfield(code="t", value="55"),
                Subfield(code="u", value="foo"),
                Subfield(code="v", value="EVP"),
            ],
        )
    )
    stub_record.add_field(
        MarcField(
            tag="960",
            indicators=[" ", " "],
            subfields=[
                Subfield(code="s", value="100"),
                Subfield(code="t", value="PAD"),
                Subfield(code="u", value="123456apprv"),
            ],
        )
    )
    return stub_record


@pytest.fixture
def stub_pamphlet_record(stub_record):
    stub_record.remove_fields("949", "852")
    stub_record["300"].delete_subfield("a")
    stub_record["300"].add_subfield("a", "5 pages")
    return stub_record


@pytest.fixture
def stub_catalogue_record(stub_record):
    stub_record.remove_fields("949", "852")
    stub_record.add_field(
        MarcField(
            tag="650",
            indicators=[" ", " "],
            subfields=[Subfield(code="v", value="Catalogues raisonnés")],
        )
    )
    return stub_record


@pytest.fixture
def stub_multivol_record(stub_record):
    stub_record.remove_fields("949", "852")
    stub_record["300"].delete_subfield("a")
    stub_record["300"].add_subfield("a", "5 volumes")
    return stub_record


@pytest.fixture
def stub_auxam_monograph(stub_record):
    stub_record.remove_fields("901")
    stub_record.add_field(
        MarcField(
            tag="901",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="AUXAM")],
        )
    )
    stub_record["949"].delete_subfield("v")
    stub_record["949"].add_subfield("v", "AUXAM")
    return stub_record


@pytest.fixture
def stub_aux_other_record(stub_record):
    stub_record.remove_fields("901", "949")
    stub_record.add_field(
        MarcField(
            tag="901",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="AUXAM")],
        )
    )
    stub_record["852"].delete_subfield("h")
    stub_record["852"].add_subfield("h", "ReCAP 24-")
    return stub_record


@pytest.fixture
def stub_leila_monograph(stub_record):
    stub_record.remove_fields("901")
    stub_record.add_field(
        MarcField(
            tag="901",
            indicators=[" ", " "],
            subfields=[Subfield(code="a", value="LEILA")],
        )
    )
    stub_record["949"].delete_subfield("v")
    stub_record["949"].add_subfield("v", "LEILA")
    return stub_record

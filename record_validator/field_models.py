from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import Field, model_validator
from record_validator.base_fields import BaseDataField, BaseControlField


class BibCallNo(BaseDataField):
    tag: Annotated[Literal["852"], Field(alias="852")]
    ind1: Literal["8"]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    call_no: Annotated[
        str,
        Field(
            pattern=r"^ReCAP 23-\d{6}$|^ReCAP 24-\d{6}$|^ReCAP 25-\d{6}$",
            exclude=True,
            examples=["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
        ),
    ]


class BibVendorCode(BaseDataField):
    tag: Annotated[Literal["901"], Field(alias="901")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    vendor_code: Annotated[
        Literal["EVP", "AUXAM", "LEILA"],
        Field(exclude=True, examples=["EVP", "AUXAM", "LEILA"]),
    ]


class ControlField001(BaseControlField):
    tag: Annotated[Literal["001"], Field(alias="001")]
    value: Annotated[
        str,
        Field(examples=["ocn123456789", "ocm123456789"]),
    ]


class ControlField003(BaseControlField):
    tag: Annotated[Literal["003"], Field(alias="003")]
    value: Annotated[
        str,
        Field(examples=["OCoLC", "DLC"]),
    ]


class ControlField005(BaseControlField):
    tag: Annotated[Literal["005"], Field(alias="005")]
    value: Annotated[
        str,
        Field(pattern=r"^\d{14}\.\d$", examples=["20240101125000.0"]),
    ]


class ControlField006(BaseControlField):
    tag: Annotated[Literal["006"], Field(alias="006")]
    value: Annotated[
        str,
        Field(pattern=r"^[A-z0-9|\\ ]{1,18}$", examples=["b|||||||||||||||||"]),
    ]


class ControlField007(BaseControlField):
    tag: Annotated[Literal["007"], Field(alias="007")]
    value: Annotated[
        str,
        Field(pattern=r"^[A-z0-9|\\ ]{2,23}$", examples=["cr |||||||||||"]),
    ]


class ControlField008(BaseControlField):
    tag: Annotated[Literal["008"], Field(alias="008")]
    value: Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9|\\ ]{40}$",
            examples=["210505s2021    nyu           000 0 eng d"],
        ),
    ]


class InvoiceField(BaseDataField):
    tag: Annotated[Literal["980"], Field(alias="980")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    invoice_date: Annotated[
        str,
        Field(
            pattern=r"^\d{6}$",
            examples=["240101", "230202"],
            exclude=True,
        ),
    ]
    invoice_price: Annotated[
        str,
        Field(
            pattern=r"^\d{3,}$",
            exclude=True,
            examples=["100", "200"],
        ),
    ]
    invoice_shipping: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
            examples=["1", "20"],
        ),
    ]
    invoice_tax: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
            examples=["1", "20"],
        ),
    ]
    invoice_net_price: Annotated[
        str,
        Field(
            pattern=r"^\d{3,}$",
            exclude=True,
            examples=["100", "200"],
        ),
    ]
    invoice_number: Annotated[
        str, Field(exclude=True, examples=["20051330", "20051331"])
    ]
    invoice_copies: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
            examples=["1", "20", "4"],
        ),
    ]


class ItemField(BaseDataField):
    tag: Annotated[Literal["949"], Field(alias="949")]
    ind1: Literal[" ", ""]
    ind2: Literal["1"]
    subfields: List[Dict[str, str]]
    item_call_no: Annotated[
        str,
        Field(
            pattern=r"^ReCAP 23-\d{6}$|^ReCAP 24-\d{6}$|^ReCAP 25-\d{6}$",
            examples=["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
            exclude=True,
        ),
    ]
    item_volume: Optional[
        Annotated[str, Field(exclude=True, examples=["v. 1", "v. 10"])]
    ] = None
    item_agency: Annotated[
        Literal["43"],
        Field(exclude=True, examples=["43"]),
    ]
    item_barcode: Annotated[
        str,
        Field(
            pattern=r"^33433[0-9]{9}$",
            examples=["33433123456789", "33433111111111"],
            exclude=True,
        ),
    ]
    item_location: Annotated[
        Optional[
            Literal[
                "rcmb2",
                "rcmf2",
                "rcmg2",
                "rc2ma",
                "rcmp2",
                "rcmb2",
                "rcph2",
                "rcpm2",
                "rcpt2",
                "rc2cf",
            ]
        ],
        Field(exclude=True, default=None, examples=["rcmb2", "rcmf2"]),
    ]
    message: Optional[Annotated[str, Field(exclude=True)]] = None
    item_price: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}\.\d{2}$",
            exclude=True,
            examples=["1.00", "0.00"],
        ),
    ]
    item_type: Annotated[
        Optional[Literal["2", "55"]], Field(exclude=True, default=None)
    ]
    item_message: Optional[Annotated[str, Field(exclude=True)]] = None
    item_vendor_code: Annotated[
        Literal["EVP", "AUXAM", "LEILA"],
        Field(exclude=True, examples=["EVP", "AUXAM", "LEILA"]),
    ]
    item_call_tag: Annotated[
        Literal["8528"],
        Field(exclude=True, examples=["8528"]),
    ]


class LCClass(BaseDataField):
    tag: Annotated[Literal["050"], Field(alias="050")]
    ind1: Literal[" ", "", "0", "1"]
    ind2: Literal["0", "4"]
    subfields: List[Dict[str, str]]
    lcc: Annotated[str, Field(exclude=True, examples=["PJ7962.H565", "DK504.932.R87"])]

    @model_validator(mode="after")
    def validate_indicator_pair(self) -> "LCClass":
        valid_combos = [(" ", "4"), ("", "4"), ("0", "0"), ("1", "0")]
        if (self.ind1, self.ind2) not in valid_combos:
            raise ValueError(
                f"Invalid indicators. Valid combinations are: {valid_combos}"
            )
        else:
            return self


class LibraryField(BaseDataField):
    tag: Annotated[Literal["910"], Field(alias="910")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    library: Annotated[
        Literal["RL", "BL", "BPL"],
        Field(exclude=True, examples=["RL", "BL", "BPL"]),
    ]


class MonographOtherField(BaseDataField):
    tag: Annotated[
        str,
        Field(
            pattern=r"0[1-9]{2}|0[1-46-9]0|^[1-7]\d\d|8[0-46-9]\d|85[013-9]|90[02-9]|9[168][1-9]|94[0-8]|9[23579]\d",  # noqa: E501
            examples=["100", "710", "650", "245"],
        ),
    ]
    ind1: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    ind2: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    subfields: List[Any]


class OrderField(BaseDataField):
    tag: Annotated[Literal["960"], Field(alias="960")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    order_price: Annotated[
        str,
        Field(
            pattern=r"^\d{3,}$",
            exclude=True,
            examples=["100", "200"],
        ),
    ]
    order_location: Annotated[
        Literal[
            "MAB", "MAF", "MAG", "MAL", "MAP", "MAS", "PAD", "PAH", "PAM", "PAT", "SC"
        ],
        Field(exclude=True),
    ]
    order_fund: Annotated[
        str,
        Field(exclude=True, examples=["41901apprv"]),
    ]


class OtherDataField(BaseDataField):
    tag: Annotated[
        str,
        Field(
            pattern=r"0[1-9]{2}|0[1-46-9]0|^[1-8]\d\d|90[02-9]|9[168][1-9]|9[2-579]\d",  # noqa: E501
            examples=["100", "710", "650", "245"],
        ),
    ]
    ind1: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    ind2: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    subfields: List[Any]

from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from pydantic import Field, model_validator
from pydantic_core import PydanticCustomError
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
        ),
    ]


class BibVendorCode(BaseDataField):
    tag: Annotated[Literal["901"], Field(alias="901")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    vendor_code: Annotated[
        Literal["EVP", "AUXAM", "LEILA"],
        Field(exclude=True),
    ]


class ControlField(BaseControlField):
    tag: Literal["001", "003", "005", "006", "007", "008"]
    value: str


class InvoiceField(BaseDataField):
    tag: Annotated[Literal["980"], Field(alias="980")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    invoice_date: Annotated[
        str,
        Field(
            pattern=r"^\d{6}$",
            exclude=True,
        ),
    ]
    invoice_price: Annotated[
        str,
        Field(
            pattern=r"^\d{3,}$",
            exclude=True,
        ),
    ]
    invoice_shipping: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
        ),
    ]
    invoice_tax: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
        ),
    ]
    invoice_net_price: Annotated[
        str,
        Field(
            pattern=r"^\d{3,}$",
            exclude=True,
        ),
    ]
    invoice_number: Annotated[str, Field(exclude=True)]
    invoice_copies: Annotated[
        str,
        Field(
            pattern=r"^\d{1,}$",
            exclude=True,
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
            exclude=True,
        ),
    ]
    item_volume: Optional[Annotated[str, Field(exclude=True)]] = None
    item_agency: Annotated[
        Literal["43"],
        Field(exclude=True),
    ]
    item_barcode: Annotated[
        str,
        Field(
            pattern=r"^33433[0-9]{9}$",
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
        Field(exclude=True, default=None),
    ]
    message: Optional[Annotated[str, Field(exclude=True)]] = None
    item_price: Annotated[
        str,
        Field(pattern=r"^\d{1,}\.\d{2}$", exclude=True),
    ]
    item_type: Annotated[
        Optional[Literal["2", "55"]], Field(exclude=True, default=None)
    ]
    item_message: Optional[Annotated[str, Field(exclude=True)]] = None
    item_vendor_code: Annotated[
        Literal["EVP", "AUXAM", "LEILA"],
        Field(exclude=True),
    ]
    item_call_tag: Annotated[
        Literal["8528"],
        Field(exclude=True),
    ]


class LCClass(BaseDataField):
    tag: Annotated[Literal["050"], Field(alias="050")]
    ind1: Literal[" ", "", "0", "1"]
    ind2: Literal["0", "4"]
    subfields: List[Dict[str, str]]
    lcc: Annotated[str, Field(exclude=True)]

    @model_validator(mode="after")
    def validate_indicator_pair(self) -> "LCClass":
        valid_combos = [(" ", "4"), ("", "4"), ("0", "0"), ("1", "0")]
        if (self.ind1, self.ind2) not in valid_combos:
            raise PydanticCustomError(
                "literal_error", f"Invalid indicators: [{self.ind1}, {self.ind2}]"
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
        Field(exclude=True),
    ]


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
        Field(exclude=True),
    ]


class OtherDataField(BaseDataField):
    tag: Annotated[
        str,
        Field(
            pattern=r"0[1-9]{2}|0[1-46-9]0|^[1-7]\d\d|8[0-46-9]\d|85[013-9]|90[02-9]|9[168][1-9]|94[0-8]|9[23579]\d",  # noqa: E501
        ),
    ]
    ind1: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    ind2: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    subfields: List[Any]

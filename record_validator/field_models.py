"""This module contains classes that define MARC fields provided in vendor records"""

from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import Field, model_validator

from record_validator.base_fields import BaseControlField, BaseDataField


class AuxBibCallNo(BaseDataField):
    """
    A 852 field in a MARC record for an Amalivre non-monograph record.

    Args:
        tag: The MARC tag for the field. Must be "852".
        ind1: The first indicator for the field. Must be "8".
        ind2: The second indicator for the field. Must be " " or "".
        subfields: A list of dictionaries containing subfield tags and values.
        call_no: The call number for the item from subfield h.
    """

    tag: Annotated[Literal["852"], Field(alias="852")]
    ind1: Literal["8"]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    call_no: Annotated[
        str,
        Field(
            pattern=r"^ReCAP 23-$|^ReCAP 24-$|^ReCAP 25-$",
            min_length=9,
            max_length=9,
            exclude=True,
            examples=["ReCAP 23-", "ReCAP 24-", "ReCAP 25-"],
        ),
    ]


class BibCallNo(BaseDataField):
    """
    A 852 field in a MARC record for a monograph record.

    Args:
        tag: The MARC tag for the field. Must be "852".
        ind1: The first indicator for the field. Must be "8".
        ind2: The second indicator for the field. Must be " " or "".
        subfields: A list of dictionaries containing subfield tags and values.
        call_no: The call number for the item from subfield h.
    """

    tag: Annotated[Literal["852"], Field(alias="852")]
    ind1: Literal["8"]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    call_no: Annotated[
        str,
        Field(
            pattern=r"^ReCAP 23-\d{6}$|^ReCAP 24-\d{6}$|^ReCAP 25-\d{6}$",
            min_length=15,
            max_length=15,
            exclude=True,
            examples=["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
        ),
    ]


class BibVendorCode(BaseDataField):
    """
    A 901 field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "852".
        ind1: The first indicator for the field. Must be "8".
        ind2: The second indicator for the field. Must be " " or "".
        subfields: A list of dictionaries containing subfield tags and values.
        vendor_code: The 3-5 digit code corresponding to the vendor.
    """

    tag: Annotated[Literal["901"], Field(alias="901")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    vendor_code: Annotated[
        Literal["EVP", "AUXAM", "LEILA"],
        Field(exclude=True, examples=["EVP", "AUXAM", "LEILA"]),
    ]


class ControlField001(BaseControlField):
    """
    A 001 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "001".
        value: The value of the field. Must be a string.

    """

    tag: Annotated[Literal["001"], Field(alias="001")]
    value: Annotated[
        str,
        Field(examples=["ocn123456789", "ocm123456789"]),
    ]


class ControlField003(BaseControlField):
    """
    A 003 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "003".
        value: The value of the field. Must be a string.
    """

    tag: Annotated[Literal["003"], Field(alias="003")]
    value: Annotated[
        str,
        Field(examples=["OCoLC", "DLC"]),
    ]


class ControlField005(BaseControlField):
    """
    A 005 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "005".
        value: The value of the field. Must be a string.
    """

    tag: Annotated[Literal["005"], Field(alias="005")]
    value: Annotated[
        str,
        Field(
            pattern=r"^\d{14}\.\d$",
            min_length=16,
            max_length=16,
            examples=["20240101125000.0"],
        ),
    ]


class ControlField006(BaseControlField):
    """
    A 006 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "006".
        value: The value of the field. Must be a string.
    """

    tag: Annotated[Literal["006"], Field(alias="006")]
    value: Annotated[
        str,
        Field(
            pattern=r"^[A-z0-9|\\ ]{1,18}$",
            min_length=7,
            max_length=18,
            examples=["b|||||||||||||||||"],
        ),
    ]


class ControlField007(BaseControlField):
    """
    A 007 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "007".
        value: The value of the field. Must be a string.
    """

    tag: Annotated[Literal["007"], Field(alias="007")]
    value: Annotated[
        str,
        Field(
            pattern=r"^[A-z0-9|\\ ]{2,23}$",
            min_length=2,
            max_length=23,
            examples=["cr |||||||||||"],
        ),
    ]


class ControlField008(BaseControlField):
    """
    An 008 control field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "008".
        value: The value of the field. Must be a string.
    """

    tag: Annotated[Literal["008"], Field(alias="008")]
    value: Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9|\\ ]{40}$",
            min_length=40,
            max_length=40,
            examples=["210505s2021    nyu           000 0 eng d"],
        ),
    ]


class InvoiceField(BaseDataField):
    """
    A 980 field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "980".
        ind1: The first indicator for the field. Must be " ".
        ind2: The second indicator for the field. Must be " ".
        subfields: A list of dictionaries containing subfield tags and values.
        invoice_date: The date of the invoice in the format "YYMMDD" from subfield a.
        invoice_price: The total price of the invoice from subfield b.
        invoice_shipping: The shipping cost of the invoice from subfield c.
        invoice_tax: The tax cost of the invoice from subfield d.
        invoice_net_price: The net price of the invoice from subfield e.
        invoice_number: The invoice number from subfield f.
        invoice_copies: The number of copies from subfield g.
    """

    tag: Annotated[Literal["980"], Field(alias="980")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    invoice_date: Annotated[
        str,
        Field(
            pattern=r"^\d{6}$",
            min_length=6,
            max_length=6,
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
    """
    A 949 field in a monograph record

    Args:
        tag: The MARC tag for the field. Must be "949".
        ind1: The first indicator for the field. Must be " ".
        ind2: The second indicator for the field. Must be "1".
        subfields: A list of dictionaries containing subfield tags and values.
        item_call_no: The call number for the item from subfield a.
        item_volume: The volume number for the item from subfield c.
        item_agency: The agency code for the item from subfield h.
        item_barcode: The barcode for the item from subfield i.
        item_location: The location for the item from subfield l.
        message: A message from the vendor from subfield m.
        item_price: The price for the item from subfield p.
        item_type: The type of item from subfield t.
        item_message: A message from the vendor from subfield u.
        item_vendor_code: The vendor code for the item from subfield v.
        item_call_tag: The call number tag for the item from subfield z.
    """

    tag: Annotated[Literal["949"], Field(alias="949")]
    ind1: Literal[" ", ""]
    ind2: Literal["1"]
    subfields: List[Dict[str, str]]
    item_call_no: Annotated[
        str,
        Field(
            pattern=r"^ReCAP 23-\d{6}$|^ReCAP 24-\d{6}$|^ReCAP 25-\d{6}$",
            min_length=15,
            max_length=15,
            examples=["ReCAP 23-000001", "ReCAP 24-100001", "ReCAP 25-222000"],
            exclude=True,
        ),
    ]
    item_volume: Optional[
        Annotated[str, Field(exclude=True, examples=["v. 1", "v. 10"])]
    ] = None
    item_agency: Optional[
        Annotated[
            Literal["43"],
            Field(exclude=True, examples=["43"]),
        ]
    ] = None
    item_barcode: Annotated[
        str,
        Field(
            pattern=r"^33433[0-9]{9}$",
            min_length=14,
            max_length=14,
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
                "rcpd2",
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

    @model_validator(mode="after")
    def validate_item_agency(self) -> "ItemField":
        error_msg = "Invalid Item Agency for item location:"
        if self.item_agency is None and self.item_location not in ["rc2ma", None]:
            raise ValueError(f"{error_msg} {self.item_location}")
        else:
            return self


class LCClass(BaseDataField):
    """
    A 050 field in a MARC record. After validating the field the combination of
    indicators is checked.

    Args:
        tag: The MARC tag for the field. Must be "050".
        ind1: The first indicator for the field. Must be " ", "", "0", or "1".
        ind2: The second indicator for the field. Must be "0" or "4".
        subfields: A list of dictionaries containing subfield tags and values.
        lcc: The Library of Congress Classification number from subfield a.


    """

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
    """
    A 910 field in a MARC record

    Args:
        tags: The MARC tag for the field. Must be "910".
        ind1: The first indicator for the field. Must be " ".
        ind2: The second indicator for the field. Must be " ".
        subfields: A list of dictionaries containing subfield tags and values.
        library: The library code from subfield a.
    """

    tag: Annotated[Literal["910"], Field(alias="910")]
    ind1: Literal[" ", ""]
    ind2: Literal[" ", ""]
    subfields: List[Dict[str, str]]
    library: Annotated[
        Literal["RL", "BL", "BPL"],
        Field(exclude=True, examples=["RL", "BL", "BPL"]),
    ]


class MonographDataField(BaseDataField):
    """
    A generic data field for monograph records. This model is used to validate
    any fields that are not specific to a particular vendor or to shelf-ready
    materials.

    Args:
        tag: The MARC tag for the field. Must be a three digit string.
        ind1: The first indicator for the field. Must be " ", "" or a string.
        ind2: The second indicator for the field. Must be " ", "" or a string.
        subfields: A list of dictionaries containing subfield tags and values.
    """

    tag: Annotated[
        str,
        Field(
            pattern=r"0[1-9]{2}|0[1-46-9]0|^[1-7]\d\d|8[0-46-9]\d|85[013-9]|90[02-9]|9[168][1-9]|94[0-8]|9[23579]\d",  # noqa: E501
            min_length=3,
            max_length=3,
            examples=["100", "710", "650", "245"],
        ),
    ]
    ind1: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    ind2: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    subfields: List[Any]


class OrderField(BaseDataField):
    """
    A 960 field in a MARC record

    Args:
        tag: The MARC tag for the field. Must be "960".
        ind1: The first indicator for the field. Must be " " or "".
        ind2: The second indicator for the field. Must be " " or "".
        subfields: A list of dictionaries containing subfield tags and values.
        order_price: The price of the order from subfield a.
        order_location: The location of the order from subfield t.
        order_fund: The fund for the order from subfield u.
    """

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
    """
    A generic data field for non-monograph records. This model is used to validate
    any fields that are not specific to a particular vendor or to shelf-ready
    materials.

    Args:
        tag: The MARC tag for the field. Must be a three digit string.
        ind1: The first indicator for the field. Must be " ", "" or a string.
        ind2: The second indicator for the field. Must be " ", "" or a string.
        subfields: A list of dictionaries containing subfield tags and values.
    """

    tag: Annotated[
        str,
        Field(
            pattern=r"0[1-9]{2}|0[1-46-9]0|^[1-8]\d\d|90[02-9]|9[168][1-9]|9[2-579]\d",  # noqa: E501
            min_length=3,
            max_length=3,
            examples=["100", "710", "650", "245"],
        ),
    ]
    ind1: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    ind2: Union[Literal["", " "], Annotated[str, Field(max_length=1, min_length=1)]]
    subfields: List[Any]

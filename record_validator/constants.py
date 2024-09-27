from enum import Enum


class AllFields(Enum):
    """
    A class to translate fields used in the validator to MARC fields/subfields
    """

    ControlField001 = "001"
    ControlField003 = "003"
    ControlField005 = "005"
    ControlField006 = "006"
    ControlField007 = "007"
    ControlField008 = "008"
    LCClass = "050"
    BibVendorCode = "901"
    LibraryField = "910"
    OrderField = "960"
    InvoiceField = "980"
    BibCallNo = "852"
    ItemField = "949"

    @classmethod
    def required_fields(cls):
        return [
            cls.LCClass.value,
            cls.BibVendorCode.value,
            cls.LibraryField.value,
            cls.OrderField.value,
            cls.InvoiceField.value,
        ]

    @classmethod
    def control_fields(cls):
        return [
            cls.ControlField001.value,
            cls.ControlField003.value,
            cls.ControlField005.value,
            cls.ControlField006.value,
            cls.ControlField007.value,
            cls.ControlField008.value,
        ]

    @classmethod
    def monograph_fields(cls):
        return [cls.BibCallNo.value, cls.ItemField.value]


class AllSubfields(Enum):
    call_no = "h"
    vendor_code = "a"
    lcc = "a"
    order_price = "s"
    order_location = "t"
    order_fund = "u"
    invoice_date = "a"
    invoice_price = "b"
    invoice_shipping = "c"
    invoice_tax = "d"
    invoice_net_price = "e"
    invoice_number = "f"
    invoice_copies = "g"
    item_call_no = "a"
    item_volume = "c"
    item_agency = "h"
    item_barcode = "i"
    item_location = "l"
    message = "m"
    item_price = "p"
    item_message = "u"
    item_vendor_code = "v"
    item_type = "t"
    item_call_tag = "z"
    library = "a"

    @staticmethod
    def get_alias(field_name: str) -> str:
        if field_name not in AllSubfields.__members__:
            return field_name
        else:
            subfield_mapping = AllSubfields[field_name].value
            return f"subfields.{subfield_mapping}"


class ValidOrderItems(Enum):
    MAB = {"order_location": "MAB", "item_location": "rcmb2", "item_type": "2"}
    MAS = {"order_location": "MAS", "item_location": "rcmb2", "item_type": "2"}
    MAF = {"order_location": "MAF", "item_location": "rcmf2", "item_type": "55"}
    MAF_NO_ITEM_TYPE = {
        "order_location": "MAF",
        "item_location": "rcmf2",
        "item_type": None,
    }
    MAG = {"order_location": "MAG", "item_location": "rcmg2", "item_type": "55"}
    MAG_NO_ITEM_TYPE = {
        "order_location": "MAG",
        "item_location": "rcmg2",
        "item_type": None,
    }
    MAL = {"order_location": "MAL", "item_location": "rc2ma", "item_type": "55"}
    MAL_NO_ITEM_LOCATION = {
        "order_location": "MAL",
        "item_location": None,
        "item_type": "55",
    }
    MAL_NO_ITEM_TYPE = {
        "order_location": "MAL",
        "item_location": "rc2ma",
        "item_type": None,
    }
    MAL_NO_ITEM_LOCATION_OR_TYPE = {
        "order_location": "MAL",
        "item_location": None,
        "item_type": None,
    }
    MAP = {"order_location": "MAP", "item_location": "rcmp2", "item_type": "2"}
    PAH = {"order_location": "PAH", "item_location": "rcph2", "item_type": "55"}
    PAH_NO_ITEM_TYPE = {
        "order_location": "PAH",
        "item_location": "rcph2",
        "item_type": None,
    }
    PAM = {"order_location": "PAM", "item_location": "rcpm2", "item_type": "55"}
    PAM_NO_ITEM_TYPE = {
        "order_location": "PAM",
        "item_location": "rcpm2",
        "item_type": None,
    }
    PAT = {"order_location": "PAT", "item_location": "rcpt2", "item_type": "55"}
    PAT_NO_ITEM_TYPE = {
        "order_location": "PAT",
        "item_location": "rcpt2",
        "item_type": None,
    }
    SC = {"order_location": "SC", "item_location": "rc2cf", "item_type": "55"}
    SC_NO_ITEM_TYPE = {
        "order_location": "SC",
        "item_location": "rc2cf",
        "item_type": None,
    }

    @classmethod
    def to_list(cls):
        return [item.value for item in cls]

from enum import Enum
from typing import Optional, Tuple, Union
from pydantic_core import ErrorDetails


class MarcEncoding(Enum):
    """
    A class to translate fields used in the validator to MARC fields/subfields
    """

    ind1 = "ind1"
    ind2 = "ind2"
    bib_call_no = "852"
    call_no = "$h"
    bib_vendor_code = "901"
    vendor_code = "$a"
    lc_class = "050"
    lcc = "$a"
    order_field = "960"
    order_price = "$s"
    order_location = "$t"
    order_fund = "$u"
    invoice_field = "980"
    invoice_date = "$a"
    invoice_price = "$b"
    invoice_shipping = "$c"
    invoice_tax = "$d"
    invoice_net_price = "$e"
    invoice_number = "$f"
    invoice_copies = "$g"
    item_fields = "949"
    item_call_tag = "$z"
    item_call_no = "$a"
    item_barcode = "$i"
    item_price = "$p"
    item_message = "$u"
    message = "$m"
    item_vendor_code = "$v"
    item_agency = "$h"
    item_location = "$l"
    item_type = "$t"
    library_field = "910"
    library = "$a"


class MarcError:
    """A class to translate an error from the validator to a more readable format"""

    def __init__(self, error: ErrorDetails):
        self.original_error = error
        self.input = self._get_input()
        self.msg = self._get_msg()
        self.loc = self._get_loc()
        self.type = error.get("type", None)
        self.ctx = error.get("ctx", None)
        self.url = error.get("url", None)
        self.loc_marc = self._loc2marc()

    def _get_msg(self) -> Optional[str]:
        msg = self.original_error.get("msg")
        return msg

    def _get_input(self):
        input = self.original_error.get("input")
        if self.original_error["type"] == "order_item_mismatch":
            return (
                input["item_type"],
                input["item_location"],
                input["order_location"],
            )
        else:
            return input

    def _get_loc(self):
        loc = self.original_error.get("loc")
        if self.original_error["type"] == "order_item_mismatch":
            return (
                "order_field",
                "item_location",
                "item_type",
            )
        else:
            return loc

    def _loc2marc(self) -> Union[str, Tuple[str, str, str]]:
        out_loc = []
        if self.type == "order_item_mismatch":
            return ("960$t", "949_$l", "949_$t")
        if "949" in self.loc:
            locs = [i for i in self.loc if i != "fields" and i != "subfields"]
        else:
            locs = [
                i
                for i in self.loc
                if i != "fields" and i != "subfields" and isinstance(i, str)
            ]
        for i in locs:
            if isinstance(i, int):
                out_loc.append(f"_{i + 1}_")
            elif "subfields." in i:
                out_loc.append(f"${i.split("subfields.")[1]}")
            elif i in MarcEncoding.__members__:
                out_loc.append(MarcEncoding[str(i)].value)
            elif len(i) == 1 and not i.isdigit():
                out_loc.append(f"${i}")
            else:
                out_loc.append(i)
        return "".join(out_loc)


class MarcValidationError:
    """A class to translate a list of errors from the `errors()` method of a
    `ValidationError` object to a more readable format"""

    def __init__(self, errors: list):
        self.errors = [MarcError(i) for i in errors]
        self.missing_fields = self._get_missing_fields()
        self.extra_fields = self._get_extra_fields()
        self.invalid_fields = self._get_invalid_fields()
        self.order_item_mismatches = self._get_order_item_mismatch_errors()

    def _get_missing_fields(self) -> list:
        return [
            i for i in self.errors if i.type in ["missing", "missing_before_validation"]
        ]

    def _get_extra_fields(self) -> list:
        return [i for i in self.errors if i.type == "extra_forbidden"]

    def _get_invalid_fields(self) -> list:
        invalid_fields = [
            i
            for i in self.errors
            if i.type in ["string_pattern_mismatch", "literal_error"]
        ]

        invalid_field_list = []
        for error in invalid_fields:
            invalid_field_list.append(
                {
                    "invalid_field": error.loc_marc,
                    "input": error.input,
                    "expectation": error.ctx,
                }
            )
        return invalid_field_list

    def _get_order_item_mismatch_errors(self) -> list:
        return [i.input for i in self.errors if i.type == "order_item_mismatch"]

    def to_dict(self):
        out_dict = {
            "valid": False,
            "error_count": 0,
            "missing_field_count": len(self.missing_fields),
            "missing_fields": [i.loc_marc for i in self.missing_fields],
            "extra_field_count": len(self.extra_fields),
            "extra_fields": [i.loc_marc for i in self.extra_fields],
            "invalid_field_count": len(self.invalid_fields),
            "invalid_fields": self.invalid_fields,
            "order_item_mismatches": self.order_item_mismatches,
        }
        out_dict["error_count"] = (
            out_dict["missing_field_count"]
            + out_dict["extra_field_count"]
            + out_dict["invalid_field_count"]
        )
        out_dict["error_count"] += len(self.order_item_mismatches)
        return out_dict

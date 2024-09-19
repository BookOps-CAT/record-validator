from enum import Enum
from typing import Any, Tuple, Union
from pydantic_core import ErrorDetails
from record_validator.parsers import get_examples_from_schema


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
    subfields = "subfields"


class MarcError:
    """A class to translate an error from the validator to a more readable format"""

    def __init__(self, error: ErrorDetails):
        self.original_error = error
        self.type: str = error["type"]
        self.ctx: Union[dict[str, Any], None] = error.get("ctx", None)
        self.input: Union[str, tuple] = self._get_input()
        self.loc: Union[str, tuple] = self._get_loc()
        self.loc_marc: Union[str, tuple] = self._loc2marc()
        self.msg: Union[str, None] = self._get_msg()

    def _get_input(self):
        if self.type == "order_item_mismatch":
            return (
                self.original_error["input"]["item_type"],
                self.original_error["input"]["item_location"],
                self.original_error["input"]["order_location"],
            )
        else:
            return self.original_error.get("input")

    def _get_loc(self):
        if self.type == "order_item_mismatch":
            return (
                "order_field",
                "item_location",
                "item_type",
            )
        elif self.type == "missing_required_field":
            return (
                "fields",
                self.input,
            )
        else:
            return self.original_error.get("loc")

    def _get_msg(self):
        if self.ctx is not None and "pattern" in self.ctx:
            examples = get_examples_from_schema(self.loc)
            out_msg = self.original_error.get("msg").split(" '")[0].strip()
            return f"{out_msg}. Examples: {examples}"
        elif self.ctx is not None and "expected" in self.ctx:
            examples = self.ctx["expected"]
            out_msg = self.original_error.get("msg").split(" '")[0].strip()
            return f"{out_msg}: {examples}"
        elif self.ctx is None and self.type == "string_type":
            examples = get_examples_from_schema(self.loc)
            out_msg = self.original_error.get("msg").split(" '")[0].strip()
            return f"{out_msg}. Examples: {examples}"
        else:
            return self.original_error.get("msg", None)

    def _loc2marc(self) -> Union[str, Tuple[str, str, str]]:
        out_loc = []
        if self.type == "order_item_mismatch":
            return ("960$t", "949_$l", "949_$t")
        if self.type == "extra_forbidden":
            locs = [i for i in self.loc if isinstance(i, str)]
        else:
            locs = [i for i in self.loc if i != "subfields" and isinstance(i, str)]
        for i in locs:
            if i in MarcEncoding.__members__:
                out_loc.append(MarcEncoding[str(i)].value)
            elif len(i) == 1 and not i.isdigit():
                out_loc.append(f"${i}")
            elif i == "fields" or i == "value":
                pass
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
            i
            for i in self.errors
            if i.type == "missing" or i.type == "missing_required_field"
        ]

    def _get_extra_fields(self) -> list:
        return [i for i in self.errors if i.type == "extra_forbidden"]

    def _get_invalid_fields(self) -> list:
        invalid_fields = [
            i
            for i in self.errors
            if i.type
            not in [
                "missing",
                "missing_before_validation",
                "extra_forbidden",
                "order_item_mismatch",
            ]
        ]

        invalid_field_list = []
        for error in invalid_fields:
            out = {"field": error.loc_marc, "error_type": error.msg}
            invalid_field_list.append(out)
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

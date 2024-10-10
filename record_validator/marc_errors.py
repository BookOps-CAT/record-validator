"""A module to translate errors from the validator to a more readable format"""

from typing import Any, Dict, List, Tuple, Union
from pydantic_core import ErrorDetails
from record_validator.adapters import get_adapter
from record_validator.constants import AllFields, AllSubfields


def get_field_examples(loc: tuple) -> Union[List[str], None]:
    """
    Get the examples provided in a model's schema for a given error location

    Args:
        loc:
            a tuple containing the location of an error
            eg. ("fields", "960", "subfields", "t",)

    Returns:
        a list of examples for the field or None if no examples are provided
    """
    field = [i for i in loc if isinstance(i, str) and i != "fields"]
    model = field[0]
    if model not in [i.value for i in AllFields]:
        return None
    else:
        model_name = AllFields(model).name
    if len(field) == 3 and field[1] == "subfields" and len(field[2]) == 1:
        model_field = f"subfields.{field[2]}"
        by_alias = True
    elif len(field) == 2:
        model_field = field[1]
        by_alias = False
    else:
        model_field = field[2]
        by_alias = False
    adapter = get_adapter(record_type=None)
    adapter_schema = adapter.json_schema(by_alias=by_alias)
    return adapter_schema["$defs"][model_name]["properties"][model_field]["examples"]


class MarcError:
    """A class to define an error identified while validating a MARC record"""

    def __init__(self, error: ErrorDetails):
        """
        This class adds attributes that enable the error data to be written to
        a more readable format.

        Args:
            error:
                an `ErrorDetails` object from the `errors()` method of a
                `ValidationError` object

        Attributes:
            original_error: the original error object
            type: the type of error (eg. missing, extra_forbidden, value_error)
            ctx: the context of the error (eg. pattern, expected)
            input: the input that caused the error (eg. a typo in a field)
            loc: the location of the error in the model schema
            loc_marc: the location of the error translated to MARC tags (eg. "960$t")
            msg: the error message (eg. "Field required: 'item_location'")"""

        self.original_error = error
        self.type: str = error["type"]
        self.ctx: Union[dict[str, Any], None] = error.get("ctx", None)
        self.input: Any = self._get_input()
        self.loc: tuple = self._get_loc()
        self.loc_marc: Union[str, tuple] = self._loc2marc()
        self.msg: Union[str, None] = self._get_msg()

    def _get_input(self) -> Union[str, tuple, List[str], None]:
        """Get the input that caused the error. Adds an input for ValueErrors."""
        input = self.original_error.get("input")
        if input is not None and "Invalid indicators" in self.original_error["msg"]:
            ind1 = input.indicator1 if hasattr(input, "indicator1") else input["ind1"]
            ind2 = input.indicator2 if hasattr(input, "indicator2") else input["ind2"]
            return [ind1, ind2]
        elif "Invalid Item Agency" in self.original_error["msg"]:
            return None
        else:
            return input

    def _get_loc(self) -> tuple:
        """Get the location of the error. Adds a location for custom errors."""
        if self.type == "order_item_mismatch":
            return (
                "order_field",
                "item_location",
                "item_type",
            )
        elif (
            self.type == "missing" and "Field required:" in self.original_error["msg"]
        ) or (
            self.type == "extra_forbidden"
            and "Extra field:" in self.original_error["msg"]
        ):
            return tuple([i for i in self.original_error["loc"]] + [self.input])
        elif (
            self.type == "value_error"
            and "Invalid Item Agency" in self.original_error["msg"]
        ):
            return tuple([i for i in self.original_error["loc"]] + ["item_agency"])
        else:
            return tuple(self.original_error["loc"])

    def _get_msg(self) -> Union[str, None]:
        """Get the error message. Adds examples to the message for certain errors."""
        msg = self.original_error.get("msg")
        if msg is not None and self.ctx is not None and "pattern" in self.ctx:
            examples = get_field_examples(self.loc)
            out_msg = msg.split(" '")[0].strip()
            return f"{out_msg}. Examples: {examples}"
        elif msg is not None and self.ctx is not None and "expected" in self.ctx:
            examples = self.ctx["expected"]
            out_msg = msg.split(" '")[0].strip()
            return f"{out_msg}: {examples}"
        elif msg is not None and self.ctx is None and self.type == "string_type":
            examples = get_field_examples(self.loc)
            out_msg = msg.split(" '")[0].strip()
            return f"{out_msg}. Examples: {examples}"
        elif msg is not None and self.type == "value_error":
            return msg.strip("Value error, ")
        else:
            return self.original_error.get("msg", None)

    def _loc2marc(self) -> Union[str, Tuple[str, str, str]]:
        """Translate the error location to MARC tags"""
        out_loc = []
        if self.type == "order_item_mismatch":
            return ("960$t", "949_$l", "949_$t")
        if self.type == "extra_forbidden":
            locs = [str(i) for i in self.loc]
        else:
            locs = [i for i in self.loc if i != "subfields" and isinstance(i, str)]
        for i in locs:
            if i in AllSubfields.__members__:
                out_loc.append(f"${AllSubfields[str(i)].value}")
            elif len(i) == 1 and not i.isdigit():
                out_loc.append(f"${i}")
            elif i == "fields" or i == "value":
                pass
            else:
                out_loc.append(i)
        return "".join(out_loc)


class MarcValidationError:
    """A class to model a list of `MarcError` objects as a single error object"""

    def __init__(self, errors: List[ErrorDetails]):
        """
        Args:
            errors:
                a list of `ErrorDetails` objects from the `errors()` method of
                a `ValidationError` object

        Attributes:
            errors:
                a list of `MarcError` objects
            error_count:
                the number of errors in the list
            missing_fields:
                a list MARC tags for fields missing from the record
            extra_fields:
                a list MARC tags for extra fields in the record
            invalid_fields:
                a list of dictionaries with the field, input and error type
            order_item_mismatches:
                a list of dictionaries with the order location, item location,
                and item type that do not match valid combinations
        """
        self.errors = [MarcError(i) for i in errors]
        self.error_count = len(errors)
        self.missing_fields = self._get_missing_fields()
        self.extra_fields = self._get_extra_fields()
        self.invalid_fields = self._get_invalid_fields()
        self.order_item_mismatches = self._get_order_item_mismatch_errors()

    def _get_missing_fields(self) -> List[Union[str, Tuple[str, str]]]:
        """Get MARC tags for missing fields from the list of errors"""
        return [
            i.loc_marc
            for i in self.errors
            if i.type == "missing" or i.type == "missing_required_field"
        ]

    def _get_extra_fields(self) -> List[Union[str, Tuple[str, str]]]:
        """Get MARC tags for extra fields from the list of errors"""
        return [i.loc_marc for i in self.errors if i.type == "extra_forbidden"]

    def _get_invalid_fields(self) -> List[Dict[str, Any]]:
        """
        Get a list of dictionaries with the field, input and error type for fields
        with other errors (eg. string_pattern_error, literal_error).
        """
        invalid_fields = [
            i
            for i in self.errors
            if i.type
            not in [
                "missing",
                "missing_required_field",
                "extra_forbidden",
                "order_item_mismatch",
            ]
        ]

        invalid_field_list = []
        for error in invalid_fields:
            out = {
                "field": error.loc_marc,
                "input": error.input,
                "error_type": error.msg,
            }
            invalid_field_list.append(out)
        return invalid_field_list

    def _get_order_item_mismatch_errors(self) -> List[Dict[str, str]]:
        """
        Get a list of dictionaries with the order location, item location, and
        item type that do not match valid combinations.
        """
        return [i.input for i in self.errors if i.type == "order_item_mismatch"]

    def to_dict(self) -> Dict[str, Any]:
        """Return the error data as a dictionary"""
        return {
            "error_count": self.error_count,
            "missing_fields": self.missing_fields,
            "extra_fields": self.extra_fields,
            "invalid_fields": self.invalid_fields,
            "order_item_mismatches": self.order_item_mismatches,
        }

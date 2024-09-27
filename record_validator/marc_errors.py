from typing import Any, List, Tuple, Union
from pydantic_core import ErrorDetails
from record_validator.adapters import FieldAdapter
from record_validator.constants import AllFields, AllSubfields


def get_examples_from_schema(loc: tuple) -> Union[List[str], None]:
    field = [
        i
        for i in loc
        if isinstance(i, str) and i not in ["fields", "monograph", "other"]
    ]
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
    adapter_schema = FieldAdapter.json_schema(by_alias=by_alias)
    return adapter_schema["$defs"][model_name]["properties"][model_field]["examples"]


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
        input = self.original_error.get("input")
        if self.type == "order_item_mismatch":
            return (
                input["item_type"],
                input["item_location"],
                input["order_location"],
            )
        elif self.type == "value_error":
            ind1 = input.indicator1 if hasattr(input, "indicator1") else input["ind1"]
            ind2 = input.indicator2 if hasattr(input, "indicator2") else input["ind2"]
            return [ind1, ind2]
        else:
            return input

    def _get_loc(self):
        if self.type == "order_item_mismatch":
            return (
                "order_field",
                "item_location",
                "item_type",
            )
        if (
            self.type == "missing" and "Field required:" in self.original_error["msg"]
        ) or (
            self.type == "extra_forbidden"
            and "Extra field:" in self.original_error["msg"]
        ):
            return tuple([i for i in self.original_error["loc"]] + [self.input])
        else:
            return self.original_error["loc"]

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
        elif self.type == "value_error":
            return self.original_error.get("msg").strip("Value error, ")
        else:
            return self.original_error.get("msg", None)

    def _loc2marc(self) -> Union[str, Tuple[str, str, str]]:
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
            elif i == "fields" or i == "value" or i == "other" or i == "monograph":
                pass
            else:
                out_loc.append(i)
        return "".join(out_loc)


class MarcValidationError:
    """A class to translate a list of errors from the `errors()` method of a
    `ValidationError` object to a more readable format"""

    def __init__(self, errors: list):
        self.errors = [MarcError(i) for i in errors]
        self.error_count = len(errors)
        self.missing_fields = self._get_missing_fields()
        self.extra_fields = self._get_extra_fields()
        self.invalid_fields = self._get_invalid_fields()
        self.order_item_mismatches = self._get_order_item_mismatch_errors()

    def _get_missing_fields(self) -> list:
        return [
            i.loc_marc
            for i in self.errors
            if i.type == "missing" or i.type == "missing_required_field"
        ]

    def _get_extra_fields(self) -> list:
        return [i.loc_marc for i in self.errors if i.type == "extra_forbidden"]

    def _get_invalid_fields(self) -> list:
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

    def _get_order_item_mismatch_errors(self) -> list:
        return [i.input for i in self.errors if i.type == "order_item_mismatch"]

    def to_dict(self):
        return {
            "error_count": self.error_count,
            "missing_fields": self.missing_fields,
            "extra_fields": self.extra_fields,
            "invalid_fields": self.invalid_fields,
            "order_item_mismatches": self.order_item_mismatches,
        }

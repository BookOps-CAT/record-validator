from itertools import product
from typing import Any, Dict, List, Union
from pymarc import Field as MarcField

CONTROL_FIELDS = ["001", "003", "005", "006", "007", "008"]
REQUIRED_FIELDS = ["852", "901", "050", "910", "960", "980", "949"]


def get_field_tag(field: Union[MarcField, dict]) -> str:
    tag = field.tag if isinstance(field, MarcField) else list(field.keys())[0]
    if tag in CONTROL_FIELDS:
        return "control_field"
    elif tag in REQUIRED_FIELDS:
        return tag
    else:
        return "data_field"


def get_missing_field_list(fields: list) -> list:
    if all(isinstance(i, dict) for i in fields):
        all_fields = [key for i in fields for key in i.keys()]
    elif all(isinstance(i, MarcField) for i in fields):
        all_fields = [i.tag for i in fields]
    else:
        all_fields = []
    return [tag for tag in REQUIRED_FIELDS if tag not in all_fields]


def order_item_from_field(
    input: List[Union[MarcField, Dict[str, Any]]]
) -> List[Dict[str, Union[str, None]]]:
    order_locations = []
    item_locations = []
    item_types = []
    for field in input:
        if (isinstance(field, MarcField) and field.tag == "960") or (
            isinstance(field, dict)
            and ("960" in field or ("tag" in field and field["tag"] == "960"))
        ):
            order_locations.append(subfield_from_code(field=field, code="t", tag="960"))
        elif (isinstance(field, MarcField) and field.tag == "949") or (
            isinstance(field, dict)
            and ("949" in field or ("tag" in field and field["tag"] == "949"))
        ):
            item_locations.append(subfield_from_code(field=field, code="l", tag="949"))
            item_types.append(subfield_from_code(field=field, code="t", tag="949"))
        else:
            continue
    order_count = len(order_locations)
    assert order_count == 1, f"Expected 1 order location, got {order_count}"
    combos = set(product(order_locations, item_locations, item_types))
    result = [
        {"order_location": ol, "item_location": il, "item_type": it}
        for ol, il, it in combos
    ]
    return result


def parse_input(input: Union[MarcField, Dict[str, Any]], model: Any) -> Dict[str, Any]:
    if not isinstance(input, (MarcField, dict)):
        return input
    elif isinstance(input, dict) and "tag" not in input or isinstance(input, MarcField):
        tag = input.tag if isinstance(input, MarcField) else next(iter(input))
        ind1 = input.indicator1 if isinstance(input, MarcField) else input[tag]["ind1"]
        ind2 = input.indicator2 if isinstance(input, MarcField) else input[tag]["ind2"]
        if isinstance(input, MarcField):
            subfields = [{i[0]: i[1]} for i in input.subfields]
        else:
            subfields = input[tag]["subfields"]
    else:
        tag, ind1, ind2 = input["tag"], input["ind1"], input["ind2"]
        subfields = input["subfields"]
    if not isinstance(subfields, list) or not all(
        isinstance(i, dict) for i in subfields
    ):
        return {"tag": tag, "ind1": ind1, "ind2": ind2, "subfields": subfields}
    sorted_subfields = sorted([i for i in subfields], key=lambda x: list(x.keys())[0])
    out = {"tag": tag, "ind1": ind1, "ind2": ind2, "subfields": sorted_subfields}
    extra_fields = [i for i in model.model_fields if i not in out.keys()]
    for field in extra_fields:
        alias = model.model_config["alias_generator"](field)
        nested_key = alias.split("subfields.")[1]
        for subfield in sorted_subfields:
            if nested_key in subfield:
                out.update({field: subfield[nested_key]})
                continue
    return out


def subfield_from_code(
    field: Union[MarcField, dict],
    tag: str,
    code: str,
) -> Union[str, None]:
    if not isinstance(field, (MarcField, dict)):
        return None
    elif isinstance(field, MarcField):
        subfields = [i[1] for i in field.subfields if code == i[0]]
    else:
        all_subfields = (
            field.get("subfields") if "tag" in field else field[tag].get("subfields")
        )
        subfields = [i[code] for i in all_subfields if code in i.keys()]
    if subfields == []:
        return None
    assert len(subfields) == 1
    return subfields[0]

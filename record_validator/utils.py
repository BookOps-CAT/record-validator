"""This module contains utility functions for working with MARC records."""

import re
from itertools import chain
from typing import Any, Dict, List, Union

from pymarc import Field as MarcField


def dict2subfield(field: Dict[str, Any], code: str) -> List[Union[str, None]]:
    """Extract subfield values from a MARC represented as a dict."""
    subfields = field[next(iter(field))]["subfields"]
    subfield_codes = list(chain(*[i.keys() for i in subfields]))
    out_list = []
    if code in subfield_codes:
        out_list.extend([i[code] for i in subfields if code in i.keys()])
    else:
        out_list.append(None)
    return out_list


def field2dict(field: Union[MarcField, Dict[str, Any]]) -> Dict[str, Any]:
    """Convert a MARC field to a dict."""
    if isinstance(field, MarcField) and field.tag.startswith("00"):
        return {field.tag: field.data}
    elif isinstance(field, dict) and "tag" in field and "subfields" not in field:
        return {field["tag"]: field["value"]}
    elif isinstance(field, dict) and all(isinstance(i, str) for i in field.values()):
        return {tag: value for tag, value in field.items()}
    elif isinstance(field, MarcField):
        tag, ind1, ind2 = field.tag, field.indicator1, field.indicator2
        subfields = [{i[0]: i[1]} for i in field.subfields]
    elif isinstance(field, dict) and "tag" in field and "subfields" in field:
        tag, ind1, ind2 = field["tag"], field["ind1"], field["ind2"]
        subfields = field["subfields"]
    else:
        ((tag, data),) = field.items()
        ind1, ind2, subfields = data["ind1"], data["ind2"], data["subfields"]
    return {tag: {"ind1": ind1, "ind2": ind2, "subfields": subfields}}


def get_record_type(fields: List[Union[MarcField, Dict[str, Any]]]) -> str:
    """Determine the record type based on the fields present in a MARC record."""
    if not isinstance(fields, list) or not all(
        isinstance(i, (MarcField, dict)) for i in fields
    ):
        return "other"
    field_list = [field2dict(i) for i in fields]

    item_vendor = [dict2subfield(i, "v") for i in field_list if "949" in i]
    bib_vendor = [dict2subfield(i, "a") for i in field_list if "901" in i]
    deduped_vendor = list(set(chain(*item_vendor + bib_vendor)))
    if len(deduped_vendor) == 1 and isinstance(deduped_vendor[0], str):
        vendor_code = deduped_vendor[0].lower()
    else:
        vendor_code = None
    aux_call_no_fields = [
        i for i in field_list if "852" in i and vendor_code == "auxam"
    ]
    subject_fields = [i for i in field_list if next(iter(i)).startswith("6")]

    aux_call_nos = list(chain(*[dict2subfield(i, "h") for i in aux_call_no_fields]))
    phys_desc = list(chain(*[dict2subfield(i, "a") for i in field_list if "300" in i]))
    subjects = list(chain(*[dict2subfield(i, "v") for i in subject_fields]))

    aux_pattern = re.compile(r"^ReCAP 2[345]-$")
    catalogue = re.compile(r"^[cC]atalogue(s?) [rR]aisonn[eé](s?)")
    multivol = re.compile(r"^(\d+)( v\.| volumes)( :$| ;$|$| $)")
    pamphlet = re.compile(r"^(\d|[0-4][0-9])( p\.| pages)( :$| ;$|$| $)")
    if any(j is not None for j in [aux_pattern.match(str(i)) for i in aux_call_nos]):
        material_type = "other"
    elif any(j is not None for j in [catalogue.match(str(i)) for i in subjects]):
        material_type = "other"
    elif any(j is not None for j in [multivol.match(str(i)) for i in phys_desc]):
        material_type = "other"
    elif any(j is not None for j in [pamphlet.match(str(i)) for i in phys_desc]):
        material_type = "other"
    else:
        material_type = "monograph"
    if vendor_code is not None:
        return f"{vendor_code}_{material_type}"
    else:
        return material_type

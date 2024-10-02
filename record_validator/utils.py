from typing import Union
from pymarc import Field as MarcField


def get_subfield_from_code(
    field: Union[MarcField, dict],
    tag: str,
    code: str,
) -> Union[list[str], list[None]]:
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
        return [None]
    else:
        return subfields


def get_vendor_code(fields: list) -> Union[str, None]:
    if not all(isinstance(i, (MarcField, dict)) for i in fields):
        return None
    if all(isinstance(i, MarcField) for i in fields):
        fields = [i for i in fields if i.tag == "901" or i.tag == "949"]
    elif all(isinstance(i, dict) for i in fields) and all("tag" in i for i in fields):
        fields = [i for i in fields if i["tag"] == "901" or i["tag"] == "949"]
    else:
        fields = [i for i in fields if "901" in i or "949" in i]
    subfields: list = []
    for field in fields:
        if isinstance(field, MarcField):
            tag = field.tag
        elif isinstance(field, dict) and "tag" in field:
            tag = field["tag"]
        else:
            tag = list(field.keys())[0]
        code = "a" if tag == "901" else "v"
        subfields.extend(get_subfield_from_code(field, tag=tag, code=code))
    deduped_subfields = list(set(subfields))
    if len(deduped_subfields) == 1:
        return deduped_subfields[0]
    else:
        return None

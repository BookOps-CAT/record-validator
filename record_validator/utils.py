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

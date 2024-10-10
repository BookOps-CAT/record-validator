"""This module contains classes that define MARC fields provided in vendor records
and functions to parse MARC data into these classes.

Classes:
    BaseControlField:
        A class that defines a control field in a MARC record. This is the parent
        class for all control field models.
    BaseDataField:
        A class that defines a data field in a MARC record. This is the parent class
        for all data field models.

Functions:
    get_control_field_input:
        A function that is used as a `BeforeValidator` for all control fields to
        parse the data input into the correct format for a control field model.

    get_data_field_input:
        A function that is used as a `BeforeValidator` for all data fields to parse
        the data input into the correct format for a control field model. This
        function also subfields by parsing them into the correct `Field` of the
        `BaseModel`. Any subfields that do not correspond to a specific field as
        defined in the model are left as a dictionary.
"""

from typing import Annotated, Any, Dict, List, Literal, Union
from pymarc import Field as MarcField
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from record_validator.constants import AllFields, AllSubfields


def get_control_field_input(input: Union[MarcField, Dict[str, Any]]) -> Dict[str, Any]:
    if not isinstance(input, (MarcField, dict)):
        return input
    elif isinstance(input, MarcField):
        return {"tag": input.tag, "value": input.value()}
    elif next(iter(input)) not in AllFields.control_fields():
        return input
    else:
        ((tag, value),) = input.items()
        out = {"tag": tag, "value": value}
        if isinstance(value, dict):
            out.update({field: value for field, value in value.items()})
        return out


def get_data_field_input(
    input: Union[MarcField, Dict[str, Any]], model: Any
) -> Dict[str, Any]:
    if not isinstance(input, (MarcField, dict)):
        return input
    elif isinstance(input, dict):
        tag = next(iter(input)) if "tag" not in input else input["tag"]
        data = input[tag] if "tag" not in input else input
        if any(loc not in data for loc in ["subfields", "ind1", "ind2"]):
            return input
        ind1, ind2, subfields = data["ind1"], data["ind2"], data["subfields"]
    else:
        tag, ind1, ind2 = input.tag, input.indicator1, input.indicator2
        subfields = [{i[0]: i[1]} for i in input.subfields]
    if not isinstance(subfields, list) or not all(
        isinstance(i, dict) for i in subfields
    ):
        return {"tag": tag, "ind1": ind1, "ind2": ind2, "subfields": subfields}
    out = {"tag": tag, "ind1": ind1, "ind2": ind2}
    out["subfields"] = sorted([i for i in subfields], key=lambda x: list(x.keys())[0])
    other_fields = [i for i in model.model_fields if i not in out.keys()]
    for field in other_fields:
        alias = model.model_config["alias_generator"](field)
        nested_key = alias.split("subfields.")[1]
        for subfield in out["subfields"]:
            if nested_key in subfield:
                out.update({field: subfield[nested_key]})
                continue
    return out


class BaseControlField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, loc_by_alias=False, extra="forbid")

    tag: Annotated[str, Field(pattern=r"00[1-9]")]
    value: str

    @model_validator(mode="before")
    @classmethod
    def parse_input(cls, input: Any) -> Any:
        return get_control_field_input(input)

    @model_serializer(mode="plain")
    def serialize_control_field(self) -> Dict[str, str]:
        return {self.tag: self.value}


class BaseDataField(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        loc_by_alias=False,
        alias_generator=AllSubfields.get_alias,
    )

    tag: Annotated[str, Field(pattern=r"0[1-9]\d|[1-9]\d\d", exclude=True)]
    ind1: Union[Literal["", " "], Annotated[str, Field(pattern=r"^\d$")]]
    ind2: Union[Literal["", " "], Annotated[str, Field(pattern=r"^\d$")]]
    subfields: List[Dict[str, str]]

    @model_validator(mode="before")
    @classmethod
    def parse_input(cls, input: Any) -> Any:
        return get_data_field_input(input, cls)

    @model_serializer(mode="plain")
    def serialize_data_field(
        self,
    ) -> Dict[str, Dict[str, Union[str, List[Dict[str, str]]]]]:
        return {
            self.tag: {
                "ind1": self.ind1,
                "ind2": self.ind2,
                "subfields": self.subfields,
            }
        }

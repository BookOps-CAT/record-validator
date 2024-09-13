from typing import Annotated, Any, Dict, List, Literal, Union
from pymarc import Field as MarcField
from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator
from record_validator.parsers import parse_input

SUBFIELD_MAPPING = {
    "call_no": "h",
    "vendor_code": "a",
    "invoice_date": "a",
    "invoice_price": "b",
    "invoice_shipping": "c",
    "invoice_tax": "d",
    "invoice_net_price": "e",
    "invoice_number": "f",
    "invoice_copies": "g",
    "item_call_no": "a",
    "item_volume": "c",
    "item_agency": "h",
    "item_barcode": "i",
    "item_location": "l",
    "message": "m",
    "item_price": "p",
    "item_type": "t",
    "item_message": "u",
    "item_vendor_code": "v",
    "item_call_tag": "z",
    "lcc": "a",
    "library": "a",
    "order_price": "s",
    "order_location": "t",
    "order_fund": "u",
}


def get_alias(field_name: str) -> str:
    if field_name not in SUBFIELD_MAPPING.keys():
        return field_name
    else:
        return f"subfields.{SUBFIELD_MAPPING[field_name]}"


class BaseControlField(BaseModel):
    model_config = ConfigDict(populate_by_name=True, loc_by_alias=False, extra="forbid")

    tag: Annotated[str, Field(pattern=r"^00[0-9]$")]
    value: str

    @model_validator(mode="before")
    @classmethod
    def parse_control_field_input(cls, input: Any) -> "BaseControlField":
        if isinstance(input, MarcField):
            return cls(tag=input.tag, value=input.value())
        elif isinstance(input, dict) and next(iter(input)) in [
            "001",
            "003",
            "005",
            "006",
            "007",
            "008",
        ]:
            ((tag, value),) = input.items()
            return cls(tag=tag, value=value)
        else:
            return input

    @model_serializer(mode="plain")
    def serialize_control_field(self) -> Dict[str, str]:
        return {self.tag: self.value}


class BaseDataField(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, loc_by_alias=False, alias_generator=get_alias
    )

    tag: Annotated[str, Field(max_length=3, min_length=3, exclude=True)]
    ind1: Union[Literal["", " "], Annotated[str, Field(pattern=r"^\d$")]]
    ind2: Union[Literal["", " "], Annotated[str, Field(pattern=r"^\d$")]]
    subfields: List[Dict[str, str]]

    @model_validator(mode="before")
    @classmethod
    def parse_input(cls, input: Any) -> Any:
        if isinstance(input, (MarcField, dict)):
            return parse_input(input, cls)
        else:
            return input

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


# class BaseOrderItem(BaseModel):
#     order_item_combination: Dict[str, Union[str, None]]

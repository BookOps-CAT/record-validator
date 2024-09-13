from typing import Annotated, List, Literal, Union
from pydantic import BaseModel, Field


class MABMASOrderItem(BaseModel):
    item_type: Literal["2"]
    item_location: Literal["rcmb2"]
    order_location: Literal["MAB", "MAS"]


class MAFOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rcmf2"]
    order_location: Literal["MAF"]


class MAGOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rcmg2"]
    order_location: Literal["MAG"]


class MALOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Union[Literal["rc2ma"], None]
    order_location: Literal["MAL"]


class MAPOrderItem(BaseModel):
    item_type: Literal["2"]
    item_location: Literal["rcmp2"]
    order_location: Literal["MAP"]


class PAHOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rcph2"]
    order_location: Literal["PAH"]


class PAMOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rcpm2"]
    order_location: Literal["PAM"]


class PATOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rcpt2"]
    order_location: Literal["PAT"]


class SCOrderItem(BaseModel):
    item_type: Union[Literal["55"], None]
    item_location: Literal["rc2cf"]
    order_location: Literal["SC"]


class OrderItem(BaseModel):
    order_item_list: List[
        Annotated[
            Union[
                MABMASOrderItem,
                MAFOrderItem,
                MAGOrderItem,
                MALOrderItem,
                MAPOrderItem,
                PAHOrderItem,
                PAMOrderItem,
                PATOrderItem,
                SCOrderItem,
            ],
            Field(discriminator="order_location"),
        ]
    ]

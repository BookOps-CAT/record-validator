"""This module contains pydantic models for validating vendor-provided MARC records."""

from typing import Annotated, Dict, List, Union
from pydantic import BaseModel, Field, ConfigDict
from pymarc import Field as MarcField
from pydantic.functional_validators import AfterValidator, BeforeValidator
from record_validator.validators import validate_leader, validate_monograph


class RecordModel(BaseModel):
    """
    A class to define a valid, full MARC record for a monograph.

    Fields marked with the annotation `Field(exclude=True)` are not included when
    serializing the model.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    leader: Annotated[
        str,
        Field(
            min_length=24,
            max_length=24,
            pattern=r"^[0-9]{5}[acdnp][acdefgijkmoprt][abcdims][\sa][\sa]22[0-9]{5}[\s12345678uz][\sacinu][\sabc]4500$",  # noqa E501
        ),
        BeforeValidator(validate_leader),
    ]
    fields: Annotated[
        Union[
            List[MarcField],
            List[Dict[str, Union[str, Dict[str, Union[str, List[Dict[str, str]]]]]]],
        ],
        AfterValidator(validate_monograph),
    ]

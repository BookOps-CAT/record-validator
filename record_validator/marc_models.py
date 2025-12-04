"""This module contains pydantic models for validating vendor-provided MARC records."""

from typing import Annotated, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from pymarc import Field as MarcField

from record_validator.validators import validate_all, validate_leader


class RecordModel(BaseModel):
    """
    A class to define a valid, full MARC record. This model is used to validate a
    MARC record and its fields. The `model_config` attribute allows for arbitrary types
    to be used in the model so that the model can be used to validate a PyMARC record
    or MARC data in another format. The `leader` field is a string that must be 24
    characters long. The `fields` field is a list of fields in the MARC record which
    will be validated against the appropriate field models using the `AfterValidator`
    `validate_all` function.

    Args:
        leader: The leader field of the MARC record.
        fields: A list of fields in the MARC record.
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
        AfterValidator(validate_all),
    ]

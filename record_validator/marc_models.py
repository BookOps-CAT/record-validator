"""This module contains pydantic models for validating vendor-provided MARC records."""

from typing import Annotated, Dict, List, Union
from pydantic import BaseModel, Field, ConfigDict
from pymarc import Field as MarcField
from pydantic.functional_validators import AfterValidator
from record_validator.validators import validate_fields


class MonographRecord(BaseModel):
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
    ]
    fields: Annotated[
        Union[
            List[MarcField],
            List[Dict[str, Union[str, Dict[str, Union[str, List[Dict[str, str]]]]]]],
        ],
        AfterValidator(validate_fields),
    ]
    # material_type: Annotated[
    #     Union[
    #         Literal["monograph"],
    #         Literal[
    #             "catalogue_raissonne",
    #             "dance",
    #             "multipart",
    #             "pamphlet",
    #             "non-standard_binding_packaging",
    #         ],
    #     ],
    #     Field(exclude=True),
    #     BeforeValidator(get_material_type),
    # ]

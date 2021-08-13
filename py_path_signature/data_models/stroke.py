import math

from py_path_signature.data_models.basic import BasicModel
from py_path_signature.data_models.error_messages import ERROR_MESSAGES
from pydantic import root_validator, validator
from pydantic.types import conlist


class StrokeFormatError(Exception):
    """Custom error that is raised when an input stroke doesn't have the right format."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class Stroke(BasicModel):

    x: conlist(float, min_items=1)
    y: conlist(float, min_items=1)

    @root_validator(pre=True)
    @classmethod
    def check_same_length_of_attributes(cls, values):
        if len(values.get("x")) != len(values.get("y")):
            raise StrokeFormatError(
                message=ERROR_MESSAGES["ATTRIBUTES_DIFFERENT_LENGTH"],
            )
        return values

    # Check all values of all attributes are not NaN
    @validator("*", pre=True, each_item=True)
    @classmethod
    def check_value_is_nan(cls, value):
        if math.isnan(value):
            raise StrokeFormatError(message=ERROR_MESSAGES["NAN_DETECTED"])
        return value

from abc import abstractmethod
from typing import List, Tuple, Annotated, Iterable
import math

from py_path_signature.data_models.basic import BasicModel
from py_path_signature.data_models.error_messages import ERROR_MESSAGES
from pydantic import root_validator, validator, Field
from pydantic.types import conlist

class Stroke(BasicModel):

    @abstractmethod
    def x_generator(self) -> Iterable[float]:
        pass

    @abstractmethod
    def y_generator(self) -> Iterable[float]:
        pass

class StrokeFormatError(Exception):
    """Custom error that is raised when an input stroke doesn't have the right format."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class StrokeDict(Stroke):

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

    def x_generator(self) -> Iterable[float]:
        for i in self.x:
            yield i

    def y_generator(self) -> Iterable[float]:
        for i in self.y:
            yield i

class StrokeTuple(Stroke):

    coordinates: Annotated[List[Tuple[float, float]], Field(min_length=2)]

    def x_generator(self) -> Iterable[float]:
        for (x,y) in self.coordinates:
            yield x

    def y_generator(self) -> Iterable[float]:
        for (x,y) in self.coordinates:
            yield y

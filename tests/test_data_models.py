import math

import pytest
from py_path_signature.data_models.error_messages import ERROR_MESSAGES
from py_path_signature.data_models.stroke import Stroke, StrokeFormatError


@pytest.mark.parametrize(
    "data",
    [
        {"x": [1, 2, 3], "y": [2, 1, 3, 4]},
        {"x": [1, 3, 2, 4, 5], "y": [2]},
    ],
)
def test_stroke_different_attributes_length(data):

    with pytest.raises(StrokeFormatError) as excinfo:
        Stroke(**data)

    assert excinfo.value.message == ERROR_MESSAGES["ATTRIBUTES_DIFFERENT_LENGTH"]


@pytest.mark.parametrize(
    "data",
    [
        {"x": [1, 2, math.nan], "y": [2, 1, 4]},
        {"x": [1, 3, 2], "y": [2, math.nan, 3]},
    ],
)
def test_stroke_different_nan_values(data):

    with pytest.raises(StrokeFormatError) as excinfo:
        Stroke(**data)

    assert excinfo.value.message == ERROR_MESSAGES["NAN_DETECTED"]

import json
import os

import numpy as np
import pytest
from py_path_signature.data_models.stroke import Stroke
from py_path_signature.path_signature_extractor import PathSignatureExtractor

from .conftest import TEST_DATA_INPUT_DIR, TEST_DATA_REFERENCE_DIR


@pytest.mark.parametrize(
    "input_strokes, expected_bounding_box",
    [
        (
            [{"x": [1, 2, 3], "y": [1, 2, 3]}],
            (1, 1, 2, 2),
        ),
        (
            [{"x": [0, 1, 2, 3], "y": [1, 2, 3, 4]}, {"x": [6, 8, 2, 3], "y": [0, 2, 3, 9]}],
            (0, 0, 9, 8),
        ),
        (
            [
                {"x": [714, 1], "y": [3, 4]},
                {"x": [6, 8], "y": [0, 9]},
                {"x": [100, 8], "y": [10, 9]},
            ],
            (0, 1, 10, 713),
        ),
    ],
)
def test_bounding_box(input_strokes, expected_bounding_box):

    strokes = [Stroke(**stroke) for stroke in input_strokes]
    bounding_box = PathSignatureExtractor.calculate_bounding_box(strokes=strokes)
    assert bounding_box == expected_bounding_box


def list_test_cases():

    return [
        os.path.splitext(case)[0]
        for case in os.listdir(TEST_DATA_INPUT_DIR)
        if os.path.isfile(os.path.join(TEST_DATA_INPUT_DIR, case))
    ]


@pytest.fixture(scope="function", params=list_test_cases())
def strokes_and_reference_signature(request):

    test_case = request.param

    with open(os.path.join(TEST_DATA_INPUT_DIR, f"{test_case}.json")) as f:
        strokes = json.load(f)

    with open(os.path.join(TEST_DATA_REFERENCE_DIR, f"{test_case}.json")) as f:
        path_signature = np.array(json.load(f))

    return (strokes, path_signature)


@pytest.fixture(scope="class")
def path_signature_extractor():
    path_signature_extractor = PathSignatureExtractor(
        order=2, rendering_size=(128, -1), min_rendering_dimension=5, max_aspect_ratio=30, delta=5
    )
    return path_signature_extractor


def test_image_signatures(path_signature_extractor, strokes_and_reference_signature):

    input_strokes, path_signature_groundtruth = strokes_and_reference_signature

    strokes = [Stroke(**stroke) for stroke in input_strokes]
    path_signature = path_signature_extractor.extract_signature(strokes=strokes)

    assert (path_signature == path_signature_groundtruth).all()

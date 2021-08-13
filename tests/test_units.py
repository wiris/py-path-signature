import pytest
from py_path_signature.data_models.stroke import Stroke
from py_path_signature.path_signature_extractor import PathSignatureExtractor


@pytest.fixture(scope="class")
def path_signature_extractor():
    path_signature_extractor = PathSignatureExtractor()
    yield path_signature_extractor


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
def test_bounding_box(path_signature_extractor, input_strokes, expected_bounding_box):

    strokes = [Stroke(**stroke) for stroke in input_strokes]
    bounding_box = path_signature_extractor.calculate_bounding_box(strokes=strokes)

    assert bounding_box == expected_bounding_box

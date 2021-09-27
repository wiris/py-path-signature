# Here we test the main class arguments and see if the corresponding exceptions are raised
import pytest
from py_path_signature.path_signature_extractor import PathSignatureExtractor


@pytest.mark.parametrize(
    "order",
    [-100, -10, -1, 3, 5.6, 10, 100],
)
def test_order(order):

    with pytest.raises(ValueError):
        PathSignatureExtractor(order=order)


@pytest.mark.parametrize(
    "rendering_size",
    [128, (128), (128,), (128, 256, 512), (-10, 10), (-1, 10), (0, 10), (128, -10), (128, 0)],
)
def test_rendering_size(rendering_size):

    with pytest.raises(ValueError):
        PathSignatureExtractor(rendering_size=rendering_size)


@pytest.mark.parametrize(
    "min_rendering_dimension",
    [-4, -3, -2, -1, 0, 1, 2, 3, 4],
)
def test_min_rendering_dimension(min_rendering_dimension):

    with pytest.raises(ValueError):
        PathSignatureExtractor(min_rendering_dimension=min_rendering_dimension)


@pytest.mark.parametrize(
    "max_aspect_ratio",
    [-100.1, -10, -1.0, -0.123, 0],
)
def test_max_aspect_ratio(max_aspect_ratio):

    with pytest.raises(ValueError):
        PathSignatureExtractor(max_aspect_ratio=max_aspect_ratio)


@pytest.mark.parametrize(
    "delta",
    [-100, -10, -1, 0],
)
def test_delta(delta):

    with pytest.raises(ValueError):
        PathSignatureExtractor(delta=delta)

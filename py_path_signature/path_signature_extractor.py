from math import log, sqrt
from typing import List, Tuple

import numpy as np

from py_path_signature.data_models.stroke import Stroke


class PathSignatureExtractor:
    def __init__(
        self,
        order: int = 0,
        rendering_size: Tuple[int, int] = (64, 64),  # (height, width)
        min_rendering_dimension: int = 5,
        max_aspect_ratio: float = 30,
        delta: int = 5,
    ) -> None:

        self.order = order
        self.rendering_size = rendering_size
        self.min_rendering_dimension = min_rendering_dimension
        self.max_aspect_ratio = max_aspect_ratio
        self.delta = delta
        self.bounding_box = None
        self.calculate_num_channels()

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, value):
        if value < 0 or value > 2:
            raise ValueError(f"Path signature order must take values 0, 1 or 2. Got order={value}.")
        self._order = value

    @property
    def rendering_size(self):
        return self._rendering_size

    @rendering_size.setter
    def rendering_size(self, value):
        try:
            height, width = value
        except:
            raise ValueError("Give a tuple with two values for the rendering size.")
        if height <= 0:
            raise ValueError(f"The height value must be greater than 0. Got height={height}.")
        if width < -1 or width == 0:
            raise ValueError(
                f"The width value must be greater than 0 or set to -1 to keep the aspect ratio. Got width={width}."
            )
        self._rendering_size = value

    @property
    def min_rendering_dimension(self):
        return self._min_rendering_dimension

    @min_rendering_dimension.setter
    def min_rendering_dimension(self, value):
        if value < 5:
            raise ValueError(
                f"Minimum render dimension allowed is 5. Got min_rendering_dimension={value}."
            )
        self._min_rendering_dimension = value

    @property
    def max_aspect_ratio(self):
        return self._max_aspect_ratio

    @max_aspect_ratio.setter
    def max_aspect_ratio(self, value):
        if value <= 0:
            raise ValueError(
                f"Max aspect ratio must be greater than 0. Got max_aspect_ratio={value}."
            )
        self._max_aspect_ratio = value

    @property
    def delta(self):
        return self._delta

    @delta.setter
    def delta(self, value):
        if value < 1:
            raise ValueError(f"Delta must be greater or equal than 1. Got delta={value}.")
        self._delta = value

    def calculate_num_channels(self) -> None:
        """
        Calculates the number of channels of the path signature image representation.
        """

        if self.order == 0:
            self.num_channels = 1
        elif self.order == 1:
            self.num_channels = 3
        else:
            self.num_channels = 7

    @staticmethod
    def calculate_bounding_box(strokes: List[Stroke]) -> Tuple[int, int, int, int]:
        """
        Calculates the bounding box enclosing a set of cartesian coordinates in the form of a
        list of strokes. Returns min and max values for the input coordinates and the height and
        width of the enclosing bounding box.
        """

        if len(strokes) == 0:
            raise Exception("Empty list of strokes.")

        x_values = [x for stroke in strokes for x in stroke.x]
        y_values = [y for stroke in strokes for y in stroke.y]

        x_min = min(x_values)
        x_max = max(x_values)
        y_min = min(y_values)
        y_max = max(y_values)

        w = x_max - x_min
        h = y_max - y_min

        # these will be used by from_coordinates_to_pixels: to avoid numerical errors when
        # rasterizing, w and h cannot be zero
        w = max(1, w)
        h = max(1, h)

        return (y_min, x_min, h, w)

    def from_coordinates_to_pixels(self, strokes: List[Stroke]) -> List[List[Tuple[int, int]]]:
        """
        Rasterizes the coordinates of the set of input strokes into image pixel positions.
        """

        if self.bounding_box is None:
            self.bounding_box = self.calculate_bounding_box(strokes)

        (y_min, x_min, h, w) = self.bounding_box

        pixels = []
        for stroke in strokes:
            out_stroke = []
            for (x, y) in zip(stroke.x, stroke.y):
                x = (self.rendering_size[1] - 1) * (x - x_min) / w
                y = (self.rendering_size[0] - 1) * (y - y_min) / h

                out_stroke.append((int(x), int(y)))

            pixels.append(out_stroke)

        return pixels

    def limit_aspect_ratio_by_number_of_strokes(self, number_of_strokes: int) -> float:
        """
        Avoid very wide path signature image representations by limiting the aspect ratio
        """

        return min(int(5 + 6 * log(number_of_strokes)), self.max_aspect_ratio)

    def set_rendering_size_keeping_aspect_ratio(self, strokes: List[Stroke]) -> None:
        """
        Set the rendering size of the path signature image representation by keeping the
        aspect ratio of the input strokes dimensions.
        """

        if self.bounding_box is None:
            self.bounding_box = self.calculate_bounding_box(strokes)

        (_, _, h, w) = self.bounding_box
        aspect_ratio = w / h

        # Set max ratio according to a function of the number of strokes
        aspect_ratio = min(aspect_ratio, self.limit_aspect_ratio_by_number_of_strokes(len(strokes)))

        self.rendering_size = (
            self.rendering_size[0],
            int(self.rendering_size[0] * aspect_ratio),
        )

    def set_rendering_size(self, strokes: List[Stroke]) -> None:
        """
        Set the rendering size of the path signature image representation.
        """

        # The user might have asked to render features keeping the aspect ratio
        if self.rendering_size[1] == -1:
            self.set_rendering_size_keeping_aspect_ratio(strokes)

        # Be sure to have at least some pixels to render features
        self.rendering_size = (
            max(self.min_rendering_dimension, self.rendering_size[0]),
            max(self.min_rendering_dimension, self.rendering_size[1]),
        )

    def calculate_signature(self, pixels: List[List[Tuple[int, int]]]) -> np.ndarray:
        """
        Calculates the path signature of a set of input pixel coordinates.
        """

        # Create image representation for Path Signature. Background is set to 0.0
        img = np.zeros((self.num_channels, self.rendering_size[0], self.rendering_size[1]))

        # Compute Path Signature representation up to order 2
        for pixel_sublist in pixels:
            for i, (tx, ty) in enumerate(pixel_sublist):

                # k=0 (image)
                img[0, ty, tx] = 1.0

                if self.order == 0:
                    continue

                sx, sy = pixel_sublist[max(0, i - self.delta)]
                ux, uy = pixel_sublist[min(len(pixel_sublist) - 1, i + self.delta)]

                # Displacements
                Dst = np.array([tx - sx, ty - sy])
                Dtu = np.array([ux - tx, uy - ty])

                # Speed normalization using the module of the direction vector
                modDst = sqrt(Dst[0] * Dst[0] + Dst[1] * Dst[1])
                modDtu = sqrt(Dtu[0] * Dtu[0] + Dtu[1] * Dtu[1])

                if modDst != 0.0:
                    Dst = Dst / modDst
                if modDtu != 0.0:
                    Dtu = Dtu / modDtu

                # k=1 (direction): Displacement(s, t) + Displacement(t,u)
                img[1, ty, tx] = Dst[0] + Dtu[0]
                img[2, ty, tx] = Dst[1] + Dtu[1]

                if self.order == 1:
                    continue

                # k=2 (kurvature):
                # TensorProduct( Displacement(s,t), Displacement(s,t) ) / 2.0
                # + TensorProduct( Displacement(s,t), Displacement(t,u) )
                # + TensorProduct( Displacement(t,u), Displacement(t,u) ) / 2.0
                img[3, ty, tx] = (
                    (Dst[0] * Dst[0]) / 2.0 + (Dst[0] * Dtu[0]) + (Dtu[0] * Dtu[0]) / 2.0
                )
                img[4, ty, tx] = (
                    (Dst[0] * Dst[1]) / 2.0 + (Dst[0] * Dtu[1]) + (Dtu[0] * Dtu[1]) / 2.0
                )
                img[5, ty, tx] = (
                    (Dst[1] * Dst[0]) / 2.0 + (Dst[1] * Dtu[0]) + (Dtu[1] * Dtu[0]) / 2.0
                )
                img[6, ty, tx] = (
                    (Dst[1] * Dst[1]) / 2.0 + (Dst[1] * Dtu[1]) + (Dtu[1] * Dtu[1]) / 2.0
                )

        return img

    @staticmethod
    def interpolate_points_in_path_signature(
        pixels: List[List[Tuple[int, int]]], path_signature_img: np.ndarray
    ) -> np.ndarray:
        """
        Given a set of strokes in pixel coordinates and their corresponding path signature image
        respresentation, linearly interpolate the channel-wise path signature values.
        """

        for pixel_sublist in pixels:
            for i, (x, y) in enumerate(pixel_sublist[1:], start=1):
                x1, y1 = pixel_sublist[i - 1]

                diff = path_signature_img[:, y, x] - path_signature_img[:, y1, x1]

                if abs(x - x1) > abs(y - y1):
                    if x1 < x:
                        for ix in range(x1 + 1, x):
                            ratio = (ix - x1) / (x - x1)
                            iy = int(y1 + (y - y1) * ratio)
                            path_signature_img[:, iy, ix] = (
                                path_signature_img[:, y1, x1] + ratio * diff
                            )
                    else:
                        for ix in range(x + 1, x1):
                            ratio = (ix - x) / (x1 - x)
                            iy = int(y + (y1 - y) * ratio)
                            path_signature_img[:, iy, ix] = (
                                path_signature_img[:, y1, x1] + ratio * diff
                            )
                else:
                    if y1 < y:
                        for iy in range(y1 + 1, y):
                            ratio = (iy - y1) / (y - y1)
                            ix = int(x1 + (x - x1) * ratio)
                            path_signature_img[:, iy, ix] = (
                                path_signature_img[:, y1, x1] + ratio * diff
                            )
                    else:
                        for iy in range(y + 1, y1):
                            ratio = (iy - y) / (y1 - y)
                            ix = int(x + (x1 - x) * ratio)
                            path_signature_img[:, iy, ix] = (
                                path_signature_img[:, y1, x1] + ratio * diff
                            )

        return path_signature_img

    def normalize_feature_channels(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize feature channels to value range in [-1,1]:
        -   channel #0: [0,1] -> [-1,1]
        -   channels #1-#2: already in the range [-1,1]
        -   channels #3-#6: [-2,2] -> [-1,1]
        """

        features[0] = features[0] * 2 - 1
        if self.order == 2:
            features[3:] = 0.5 * features[3:]

        return features

    def extract_signature(self, strokes: List[Stroke]) -> np.ndarray:
        """
        Main method to extract path signature features of an input set of strokes.
        """

        if len(strokes) == 0:
            raise Exception("Empty list of strokes.")

        self.set_rendering_size(strokes)
        pixels = self.from_coordinates_to_pixels(strokes)
        img = self.calculate_signature(pixels)
        img = self.interpolate_points_in_path_signature(pixels, img)
        img = self.normalize_feature_channels(img)

        return img

from PIL import Image
from py_path_signature.data_models.stroke import Stroke
from py_path_signature.path_signature_extractor import PathSignatureExtractor

from sample_strokes import sample_strokes

strokes = [Stroke(**stroke) for stroke in sample_strokes]

pse = PathSignatureExtractor(
    order=2, rendering_size=(128, -1), min_rendering_dimension=5, max_aspect_ratio=30, delta=5
)
img = pse.extract_signature(strokes=strokes)

# Each channel of the path signature image representation stores path signature features of a given
# order. Value range is [-1, 1] for each channel.
for channel_idx in range(img.shape[0]):
    channel = 255 * (img[channel_idx] + 1) / 2
    channel = Image.fromarray(channel.astype("uint8")).save(f"results/channel_{channel_idx}.png")

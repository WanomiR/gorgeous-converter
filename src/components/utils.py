import rawpy
import re
import numpy as np
from PIL import Image


def read_raw(path: str) -> (np.array, tuple[int]):
    """
    Takes in raw image file and returns numpy array
    :param path:
    :return: (np.array, shape)
    """
    with rawpy.imread(path) as raw:
        img = raw.postprocess(
            output_color=rawpy.ColorSpace(1),
            half_size=True,
            use_camera_wb=True,
            output_bps=16,
            no_auto_bright=True,
            no_auto_scale=False,
            gamma=(1, 1),
            chromatic_aberration=(1, 1),
        )
        img = img.astype(np.float32)

    return img


def get_file_name(input_file) -> str:
    return re.search("[\S]*(?=\.)", input_file.name).group()


def show_img(img: np.array):
    img = (img // 257).astype(np.uint8)
    Image.fromarray(img).show()


def normalize_18pct_grey(img: np.array) -> np.array:
    return img * 50_000 / np.average(img) + 200


def log_convert(img: np.array) -> np.array:
    """
    Convert blurred image into human perception range
    :param img: np.array
    :return: np.array
    """
    img_log = np.log10(img)
    return (
            (img_log - 2.3)
            /
            (np.max(img_log) - 2.3)
    )


def prepare_out(img: np.array, white: int = 254) -> Image:
    img = np.around(img * white).astype(np.uint8)
    return Image.fromarray(img.clip(0, 255))

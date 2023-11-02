import numpy as np
import streamlit as st
from scipy import signal


def gen_blur_matrix(n: int = 10, k: int = 50) -> np.array:
    """
    Create a blur matrix based on the
    hyperbolic decay function: https://habr.com/ru/articles/432622/
    :param n:  blur radius
    :param k: spread coefficient
    :return: 2-dimensional matrix
    """
    x = np.fabs(  # create a linear space from -1 to 1 with 2n+1 steps
        np.linspace(-n, n, n * 2 + 1) / n
    )
    kernel_1d = (  # apply the hyperbolic decay function
            (((x - 1) ** 2) * (x * k + k + 1))
            /
            ((k + 1) * (k * x + 1))
    )
    # create an outer product normalized matrix
    kernel_2d = np.outer(kernel_1d.T, kernel_1d.T)
    kernel_2d /= np.sum(kernel_2d)
    return kernel_2d


def get_blur_constant(img_shape: tuple[int]) -> float:
    """
    2_000 is an arbitrary number chosen relying on perceptual feeling
    normalized with respect to the biggest side
    :param img_shape:
    :return:
    """
    return 2_000. / np.max(img_shape)


def blur_image(img: np.array, params: list[dict]) -> np.array:
    """
    Apply blur matrix convolution to each layer using individual blur parameters.
    :param img: np.array
    :param params: list of dictionaries
    :return: np.array
    """
    return np.dstack([
        signal.convolve2d(
            in1=img[:, :, p["channel_idx"]],
            in2=gen_blur_matrix(p["radius"], p["spread"]),
            mode="same"
        ) for p in params
    ])


@st.cache_data
def apply_blur(img: np.array, blur_radius_coef: float,
               blur_spread_coef: float, halation_coef: float):

    _blur_constant = get_blur_constant(img.shape)

    blur_params = [
        {
            "channel": "red",
            "channel_idx": 0,
            "radius": int(12 * blur_radius_coef * halation_coef * _blur_constant),
            "spread": int(25 * blur_spread_coef),
        },
        {
            "channel": "green",
            "channel_idx": 1,
            "radius": int(5 * blur_radius_coef * _blur_constant),
            "spread": int(25 * blur_spread_coef),
        },
        {
            "channel": "blue",
            "channel_idx": 2,
            "radius": int(3 * blur_radius_coef * _blur_constant),
            "spread": int(25 * blur_spread_coef),
        }
    ]

    blurred = blur_image(img, blur_params)
    return blurred

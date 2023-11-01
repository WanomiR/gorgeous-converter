import numpy as np
from PIL import Image
from colour import (read_LUT,
                    RGB_to_XYZ,
                    XYZ_to_ProLab,
                    ProLab_to_XYZ,
                    XYZ_to_RGB)

# film variables
FILM_CURVE = read_LUT("./film/film_curve_portra_400.spi1d")
FILM_COLOUR = read_LUT("./film/Portra_400.cube")
NOISE_SAMPLE = Image.open("./film/grain_portra400.tif")
GRAIN_CURVE = read_LUT("./film/Grain_curve.spi1d")


def rgb_to_prolab(img: np.array, **kwargs) -> np.array:
    xyz = RGB_to_XYZ(img, "sRgb", chromatic_adaptation_transform=None,
                     illuminant=None, **kwargs)
    prolab = XYZ_to_ProLab(xyz)
    return prolab


def prolab_to_rgb(img: np.array, **kwargs) -> np.array:
    xyz = ProLab_to_XYZ(img)
    rgb = XYZ_to_RGB(xyz, "sRGB", chromatic_adaptation_transform=None,
                     illuminant=None, **kwargs)
    return rgb


def apply_wb_correction(img: np.array, r: float, g: float, b: float) -> np.array:
    img[:, :, 0] += r
    img[:, :, 1] += g
    img[:, :, 2] += b
    # return img


def apply_film_lut(img: np.array, cont_scene: int, exp_shift: float) -> np.array:
    # dynamic range compression, total 9ev
    app_cont_scene = img / 9 * cont_scene
    # normalize after adapting for dynamic range
    auto_grey = app_cont_scene + (0.29 - np.mean(app_cont_scene))
    # over/under exposure emulation, shift exposure before applying LUT
    colored = FILM_COLOUR.apply((auto_grey + exp_shift / 9))
    # normalize again to account for film error, shift exposure again
    normalized = colored + (0.4 - np.mean(colored)) + exp_shift / 9
    # apply contrast curve
    curved = FILM_CURVE.apply(normalized)
    # normalize the result
    result = (curved - np.mean(curved)) / cont_scene * 9 + 0.5

    return result


def apply_cont_curve(img: np.array, print_cont: float, print_exp: float) -> np.array:
    return (1 / (1 + np.power(
        10 ** print_cont,
        2 * (-img - print_exp + 0.5))
                 ))


def apply_saturation(img: np.array, channel: int, end: float, mask_less_zero: bool):
    if mask_less_zero:
        mask = img[:, :, channel] < 0
    else:
        mask = img[:, :, channel] >= 0

    img[:, :, channel][mask] = ((2 / (1 + np.power(
        (16 ** end),
        -img[:, :, channel][mask] / 100)
                                      ) - 1) * 100 / end)


def apply_grain(img: np.array, amplify: float, amplify_mask: float) -> np.array:

    grain_sample = NOISE_SAMPLE
    if img.shape[0] > img.shape[1]:
        grain_sample = grain_sample.transpose(method=Image.Transpose.ROTATE_90)

    grain_crop = grain_sample.crop((0, 0, img.shape[1], img.shape[0]))
    grain = np.asarray(grain_crop, dtype=np.float32) / 255.
    grain -= np.mean(grain)

    grain_mask = GRAIN_CURVE.apply(img)
    grain = (grain * amplify * (grain_mask ** amplify_mask)) + 1
    img *= grain

    return img


def apply_film(img: np.array, wb_r: float, wb_g: float, wb_b: float,
               cont_scene: int, exp_shift: int, print_cont: float,
               print_exp: float, end_a_minus: float, end_a_plus: float,
               end_b_minus: float, end_b_plus: float, saturation: float,
               amplify_grain: float, amplify_grain_mask: float):

    saturation_params = [
        (1, end_a_minus, True),
        (1, end_a_plus, False),
        (2, end_b_minus, True),
        (2, end_b_plus, False)
    ]

    # apply white balance correction
    # TO DO: don't forget to try extreme wb to see if it works
    apply_wb_correction(img, wb_r, wb_g, wb_b)
    # apply film LUT
    img = apply_film_lut(img, cont_scene, exp_shift)
    # apply contrast curve
    img = apply_cont_curve(img, print_cont, print_exp)
    # convert to prolab
    img = rgb_to_prolab(img)

    # make saturation adjustments
    img[:, :, 1] *= saturation
    img[:, :, 2] *= saturation

    for channel, end, less_zero in saturation_params:
        apply_saturation(img, channel, end, less_zero)

    # convert back to sRgb
    img = prolab_to_rgb(img)
    # apply graining
    img = apply_grain(img, amplify_grain, amplify_grain_mask)

    return img

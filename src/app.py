import streamlit as st
from io import BytesIO
from components.blur import apply_blur
from components.film import apply_film
from components.utils import (read_raw,
                              get_file_name,
                              normalize_18pct_grey,
                              log_convert,
                              prepare_out)

st.title("Gorgeous Converter")

uploaded_file = st.file_uploader("Upload a raw image file")

# variables
BR_COEF: float = 1.2  # blur radius coefficient
BS_COEF: float = 1.  # blur spread coefficient
HALATION: float = 1.

# lab channels balance
END_A_PLUS: float = 3.
END_A_MINUS: float = 1.5
END_B_PLUS: float = 2.
END_B_MINUS: float = 4.

# white balance correction coefficients
WB_RED: float = 0.
WB_GREEN: float = 0.
WB_BLUE: float = 0.

# saturation adjustment
SATURATION: float = .5

# film adjustments
SCENE_CONTRAST: int = 6
EXPOSURE_SHIFT: int = -3

# final print settings
PRINT_EXPOSURE: float = -0.1
PRINT_CONTRAST: float = 4

# grain settings
AMPLIFY_GRAIN: float = .15
AMPLIFY_GRAIN_MASK: float = 6.

if uploaded_file is not None:

    # read the file
    image = read_raw(uploaded_file)
    file_name = get_file_name(uploaded_file)

    # normalize by 18% grey
    image = normalize_18pct_grey(image)
    # blur the image
    image = apply_blur(image, BR_COEF, BS_COEF, HALATION)
    # back to the human perception range
    image = log_convert(image)

    # apply film lut
    image = apply_film(image, WB_RED, WB_GREEN, WB_BLUE,
                       SCENE_CONTRAST, EXPOSURE_SHIFT,
                       PRINT_CONTRAST, PRINT_EXPOSURE,
                       END_A_MINUS, END_A_PLUS, END_B_MINUS, END_B_PLUS,
                       SATURATION, AMPLIFY_GRAIN, AMPLIFY_GRAIN_MASK)

    # prepare for the output
    image = prepare_out(image)

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    # show and download the resulting jpeg
    st.image(img_bytes, caption="This is your image!")
    st.download_button(
        label="Download image",
        data=img_bytes,
        file_name=file_name + ".jpg",
        mime="image/jpeg"
    )

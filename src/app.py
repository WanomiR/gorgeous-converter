import streamlit as st
from io import BytesIO
import numpy as np
from components.blur import apply_blur
from components.film import apply_film
from components.utils import (read_raw,
                              get_file_name,
                              normalize_18pct_grey,
                              log_convert,
                              prepare_out)
st.set_page_config(layout="wide")

st.title("Gorgeous Converter")
with st.expander("Upload raw image file"):
    uploaded_file = st.file_uploader("Upload raw image file",
                                     type=["NEF", "cr3", "cr2", "dng", "tiff"],
                                     label_visibility="hidden",)

with st.sidebar:
    st.header("Image parameters")

    with st.expander("Blur"):
        BR_COEF = st.slider("Radius", min_value=.1, max_value=3., value=1.2, step=.1)
        BS_COEF = st.slider("Spread", min_value=.1, max_value=3., value=1., step=.1)
        HALATION = st.slider("Halation", min_value=.1, max_value=3., value=1., step=.1)

    with st.expander("White balance"):
        WB_RED = st.slider("Red", min_value=0., max_value=.1, value=0., step=.01)
        WB_GREEN = st.slider("Green", min_value=0., max_value=.1, value=0., step=.01)
        WB_BLUE = st.slider("Blue", min_value=0., max_value=.1, value=0., step=.01)

    with st.expander("Film"):
        SCENE_CONTRAST = st.slider("Scene contrast range (ev)", min_value=3, max_value=9, value=4, step=1)
        EXPOSURE_SHIFT = st.slider("Exposure shift (ev)", min_value=-3., max_value=3., value=0., step=.1)

    with st.expander("Print"):
        PRINT_EXPOSURE = st.slider("Exposure", min_value=-.5, max_value=.5, value=0., step=.01)
        PRINT_CONTRAST = st.slider("Contrast", min_value=1., max_value=5., value=2., step=.1)
        SATURATION = np.log(st.slider("Saturation", min_value=0., max_value=1., value=.65, step=.05) + 1)

    with st.expander("Grain"):
        AMPLIFY_GRAIN = st.slider("Amplify", min_value=0., max_value=1., value=.15, step=.05)
        AMPLIFY_GRAIN_MASK = st.slider("Amplify mask", min_value=0., max_value=10., value=6., step=.5)

    st.header("Advanced")
    with st.expander("Lab channels compression rate"):
        END_A_PLUS = st.slider("__A+__", min_value=1., max_value=5., value=2.63)
        END_A_MINUS = st.slider("__A-__", min_value=1., max_value=5., value=4.9)
        END_B_PLUS = st.slider("__B+__", min_value=1., max_value=5., value=2.41)
        END_B_MINUS = st.slider("__B-__", min_value=1., max_value=5., value=3.3)


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

    with st.expander("Download options"):
        st.write("Parameters here")

    st.download_button(
        label="Download image",
        data=img_bytes,
        file_name=file_name + ".jpg",
        mime="image/jpeg"
    )

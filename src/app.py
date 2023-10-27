from PIL import Image
import streamlit as st
import rawpy
import re
from io import BytesIO

st.title("Image Converter")

uploaded_file = st.file_uploader("Upload a raw image file")

if uploaded_file is not None:

    file_name = re.search(
        "[\S]*(?=\.)",
        uploaded_file.name
    ).group()

    with rawpy.imread(uploaded_file) as raw:
        rgb = raw.postprocess(use_camera_wb=True)

    st.image(rgb, caption="This is your image!")

    buffer = BytesIO()
    Image.fromarray(rgb).save(buffer, format="JPEG")
    img_bytes = buffer.getvalue()

    st.download_button(
        label="Download image",
        data=img_bytes,
        file_name=file_name + ".jpg",
        mime="image/jpeg"
    )



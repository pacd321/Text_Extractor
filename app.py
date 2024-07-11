import streamlit as st
import easyocr
import cv2
import numpy as np
from googletrans import Translator

st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    h1 {
        color: #1E3A8A;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #1E3A8A;
        border-radius: 5px;
    }
    .stSelectbox {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_image(image_file):
    img = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), 1)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


@st.cache_resource
def get_easyocr_reader():
    return easyocr.Reader(['en', 'hi'])


def extract_text(image):
    reader = get_easyocr_reader()
    result = reader.readtext(image)
    return result


def translate_text(text, target_language):
    translator = Translator()
    translated = translator.translate(text, dest=target_language)
    return translated.text


st.title("🖼️ Text Extraction and Translation App")

st.markdown("---")

st.markdown("""
    <style>
        .uploadedFile {
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

image_file = st.file_uploader("📤 Upload Image", type=['jpg', 'png', 'jpeg'])

if image_file is not None:
    st.markdown(f"<div class='uploadedFile'>Uploaded: {
                image_file.name}</div>", unsafe_allow_html=True)

    if 'image' not in st.session_state:
        st.session_state.image = load_image(image_file)

    col1, col2 = st.columns(2)
    with col1:
        st.image(st.session_state.image,
                 caption='Uploaded Image', use_column_width=True)

    with col2:
        if 'extracted_text' not in st.session_state:
            if st.button("🔍 Extract Text"):
                with st.spinner("Extracting text..."):
                    result = extract_text(st.session_state.image)
                    text_only = [item[1] for item in result]
                    st.session_state.full_text = ' '.join(text_only)
                    st.session_state.extracted_text = True
                    st.session_state.result = result
                st.success("Text extracted successfully!")

        if 'extracted_text' in st.session_state:
            st.markdown("### 📝 Extracted Text:")
            st.markdown(f"<div style='background-color: #ffffff; padding: 1rem; border-radius: 5px;'>{
                        st.session_state.full_text}</div>", unsafe_allow_html=True)

    if 'extracted_text' in st.session_state:
        st.markdown("---")
        st.subheader("🌐 Text Translation")
        col1, col2 = st.columns(2)
        with col1:
            target_language = st.selectbox("Select Target Language",
                                           ["hi", "es", "fr", "de"],
                                           format_func=lambda x: {
                                               "hi": "Hindi 🇮🇳",
                                               "es": "Spanish 🇪🇸",
                                               "fr": "French 🇫🇷",
                                               "de": "German 🇩🇪",
                                           }.get(x, x))
        with col2:
            if st.button("🔄 Translate"):
                with st.spinner("Translating..."):
                    try:
                        st.session_state.translated_text = translate_text(
                            st.session_state.full_text, target_language)
                        st.success("Translation Complete!")
                    except Exception as e:
                        st.error(f"Translation failed: {str(e)}")

        if 'translated_text' in st.session_state:
            st.markdown("### 🗣️ Translated Text:")
            st.markdown(f"<div style='background-color: #ffffff; padding: 1rem; border-radius: 5px;'>{
                        st.session_state.translated_text}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🖼️ Annotated Image")
    img = st.session_state.image.copy()
    spacer = 100
    font = cv2.FONT_HERSHEY_SIMPLEX
    for detection in st.session_state.result:
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))
        text = detection[1]
        img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
        img = cv2.putText(img, text, (20, spacer), font,
                          0.5, (0, 255, 0), 2, cv2.LINE_AA)
        spacer += 15

    st.image(img, caption='Annotated Image', use_column_width=True)

st.markdown("---")

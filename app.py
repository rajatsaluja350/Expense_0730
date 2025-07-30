import streamlit as st
import requests
from PIL import Image
import fitz  # PyMuPDF
import io

OCR_SPACE_API_KEY = "helloworld"  # Replace with your OCR.Space API key

def ocr_space_file(file_bytes, filename):
    url = 'https://api.ocr.space/parse/image'
    payload = {
        'apikey': OCR_SPACE_API_KEY,
        'language': 'eng',
        'isOverlayRequired': False
    }
    files = {
        'file': (filename, file_bytes)
    }
    response = requests.post(url, data=payload, files=files)
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        return f"Error: {result.get('ErrorMessage', ['Unknown error'])[0]}"
    return result.get("ParsedResults", [{}])[0].get("ParsedText", "")

def extract_images_from_pdf(pdf_file):
    images = []
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        images.append(io.BytesIO(img_bytes))
    return images

st.title("🧾 SmartReceipt OCR App")
st.write("Upload receipt images or PDFs to extract text using OCR.Space API.")

uploaded_files = st.file_uploader("Upload receipt files (images or PDFs)", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        st.subheader(f"📄 {file.name}")
        if file.type == "application/pdf":
            images = extract_images_from_pdf(file)
            for i, img_io in enumerate(images):
                st.image(img_io, caption=f"Page {i+1}", use_column_width=True)
                text = ocr_space_file(img_io.getvalue(), f"{file.name}_page{i+1}.png")
                st.text_area(f"Extracted Text (Page {i+1})", text, height=200)
        else:
            image = Image.open(file)
            st.image(image, caption=file.name, use_column_width=True)
            text = ocr_space_file(file.read(), file.name)
            st.text_area("Extracted Text", text, height=200)

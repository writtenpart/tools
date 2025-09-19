import os
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import easyocr
from pdf2image import convert_from_path

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, static_url_path="/static")

# --- OCR helpers ---
def tesseract_ocr(image_path):
    return pytesseract.image_to_string(Image.open(image_path), lang="ben")

def easyocr_ocr(image_path):
    reader = easyocr.Reader(['bn'], gpu=False)
    results = reader.readtext(image_path, detail=0)
    return "\n".join(results)

def pdf_to_text_tesseract(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300)
    parts = []
    for i, page in enumerate(pages, start=1):
        txt = pytesseract.image_to_string(page, lang="ben")
        parts.append(f"--- Page {i} ---\n{txt.strip()}")
    return "\n\n".join(parts)

def pdf_to_text_easyocr(pdf_path):
    reader = easyocr.Reader(['bn'], gpu=False)
    pages = convert_from_path(pdf_path, dpi=300)
    parts = []
    for i, page in enumerate(pages, start=1):
        results = reader.readtext(page, detail=0)
        parts.append(f"--- Page {i} ---\n" + "\n".join(results))
    return "\n\n".join(parts)

# --- Routes ---
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    file = request.files['file']
    engine = request.form.get("engine", "tesseract")
    if file.filename == "":
        return jsonify({"error": "No file selected"})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Run OCR
    if filename.lower().endswith(".pdf"):
        text = pdf_to_text_tesseract(filepath) if engine == "tesseract" else pdf_to_text_easyocr(filepath)
    else:
        text = tesseract_ocr(filepath) if engine == "tesseract" else easyocr_ocr(filepath)

    # Save server-side text
    output_file = os.path.join(OUTPUT_FOLDER, "ocr_result.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    return jsonify({"text": text})

@app.route("/download")
def download():
    return send_from_directory(OUTPUT_FOLDER, "ocr_result.txt", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

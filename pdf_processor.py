import os
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
import pandas as pd
from pathlib import Path

# Set Tesseract OCR path (IMPORTANT: This will only work locally, for deployment you need system path setup)
# Automatically use system-installed Tesseract
pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def extract_drawing_title_ocr(pdf_path):
    """Extracts OCR text from the exact location of 'Drawing Title'."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # First page
        pix = page.get_pixmap()
        
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        x_start, y_start, x_end, y_end = 1500, 1565, 2200, 1600  # Your values
        cropped = gray[y_start:y_end, x_start:x_end]

        text = pytesseract.image_to_string(cropped)
        return text.strip() if text.strip() else "Drawing Title Not Found"

    except Exception as e:
        return f"Error extracting OCR text: {e}"

def parse_filename(filename):
    """Extracts structured metadata from the filename."""
    parts = filename.replace(".pdf", "").split("-")
    if len(parts) < 9:
        return None
    return {
        "Project": parts[0],
        "Phase": parts[1],
        "System": parts[2],
        "Zone": parts[3],
        "Level": parts[4],
        "Document Type": parts[5],
        "Originator": parts[6],
        "Role": parts[7],
        "File Value": parts[8],
        "File Number": filename.replace(".pdf", "")
    }

def process_pdfs(folder_path):
    pdf_files = list(Path(folder_path).glob("*.pdf"))
    extracted_data = []

    for pdf_file in pdf_files:
        metadata = parse_filename(pdf_file.name)
        if metadata:
            metadata["Drawing Title"] = extract_drawing_title_ocr(pdf_file)
            extracted_data.append(metadata)

    if extracted_data:
        df = pd.DataFrame(extracted_data)
        output_file = Path(folder_path) / "Processed_PDF_Metadata.xlsx"
        df.to_excel(output_file, index=False, engine="openpyxl")
        return df, output_file
    else:
        return None, None
import os
import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
import pandas as pd
import re
from pathlib import Path

# Set Tesseract OCR path (IMPORTANT: This will only work locally, for deployment you need system path setup)

# Explicitly set Render's typical path for tesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Keywords that must begin the drawing title (case insensitive)
KEYWORDS = [
    'house', 'duplex', 'block', 'rc', 'road', 'watermain', 'typical', 'combined',
    'proposed', 'foul', 'drainage', 'surface', 'wastewater', 'roads', 'swept',
    'civil', 'structural', 'bulk', 'top', 'mainline', 'general', 'apartment',
    'rear', 'basement', 'roof', 'ground', 'first', 'second', 'third', 'fourth',
    'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth'
]

def safe_crop(gray, x_start, y_start, x_end, y_end):
    h, w = gray.shape
    x_start = min(x_start, w - 1)
    y_start = min(y_start, h - 1)
    x_end = min(x_end, w)
    y_end = min(y_end, h)

    # Ensure valid window
    if x_end <= x_start:
        x_end = x_start + 1
    if y_end <= y_start:
        y_end = y_start + 1

    return gray[y_start:y_end, x_start:x_end]

def extract_drawing_title_ocr(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Define two windows
        window_A = (1500, 1565, 2200, 1600)
        window_B = (2000, 1300, gray.shape[1], gray.shape[0])  # x_end=w, y_end=h

        # Try Window A first
        for window in [window_A, window_B]:
            x_start, y_start, x_end, y_end = window
            cropped = safe_crop(gray, x_start, y_start, x_end, y_end)

            # OCR and process
            text = pytesseract.image_to_string(cropped)
            lines = text.splitlines()

            for line in lines:
                words = line.strip().lower().split()
                if not words:
                    continue
                if any(word in KEYWORDS for word in words[:3]):
                    return line.strip()

        return "Drawing Title Not Found"

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

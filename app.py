import streamlit as st
import pdf_processor as pp
from pathlib import Path

st.set_page_config(page_title="PDF Drawing Title Extractor", layout="wide")

st.title("PDF Drawing Title Extractor")

uploaded_pdfs = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

if st.button("Process PDFs"):
    if not uploaded_pdfs:
        st.warning("Please upload PDF files.")
    else:
        with st.spinner("Processing..."):
            extracted_data = []
            for uploaded_pdf in uploaded_pdfs:
                # Save temporarily
                with open(uploaded_pdf.name, "wb") as f:
                    f.write(uploaded_pdf.getbuffer())

                # Process using your existing logic
                metadata = pp.parse_filename(uploaded_pdf.name)
                if metadata:
                    metadata["Drawing Title"] = pp.extract_drawing_title_ocr(uploaded_pdf.name)
                    extracted_data.append(metadata)

            if extracted_data:
                df = pd.DataFrame(extracted_data)
                st.success("✅ PDFs processed!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", data=csv, file_name="Processed_PDF_Metadata.csv")
            else:
                st.error("❌ No valid PDFs found.")

import streamlit as st
import pdf_processor as pp
from pathlib import Path

st.set_page_config(page_title="PDF Drawing Title Extractor", layout="wide")

st.title("PDF Drawing Title Extractor")

uploaded_pdfs = st.file_uploader("Upload one or more PDF files", type="pdf", accept_multiple_files=True)

if st.button("Process PDFs"):
    if not folder:
        st.warning("Please enter a folder path.")
    else:
        folder_path = Path(folder)
        if not folder_path.exists() or not folder_path.is_dir():
            st.error("The provided path is invalid or does not exist.")
        else:
            with st.spinner("Processing..."):
                df, output_file = pp.process_pdfs(folder_path)
                if df is not None:
                    st.success(f"✅ Processed! Saved to: {output_file}")
                    st.dataframe(df)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download as CSV", data=csv, file_name="Processed_PDF_Metadata.csv")
                else:
                    st.error("No valid PDFs were processed.")

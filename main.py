import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from generate_report import generate_report

st.set_page_config(page_title="Market Valuation App", layout="wide")
st.title("🏡 Market Valuation App")

# Upload comps file
comps_file = st.file_uploader("Upload MLS CSV File", type=["csv"])
pdf_file = st.file_uploader("Upload Subject Property PDF", type=["pdf"])

if comps_file and pdf_file:
    comps_df = pd.read_csv(comps_file)

    # Parse PDF for subject property info
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    real_avm = None
    subject_info = {"Address": "N/A", "Above Grade SF": "N/A", "Bedrooms": "N/A", "Bathrooms": "N/A"}

    for line in text.split("\n"):
        if "Automated Valuation" in line or "Real AVM" in line:
            try:
                real_avm = float("".join([c for c in line if c.isdigit() or c == "."]))
            except:
                pass
        if "Address" in line and ":" in line:
            subject_info["Address"] = line.split(":")[-1].strip()
        if "Above Grade" in line and "SF" in line:
            try:
                subject_info["Above Grade SF"] = int("".join([c for c in line if c.isdigit()]))
            except:
                pass
        if "Bedrooms" in line:
            try:
                subject_info["Bedrooms"] = int("".join([c for c in line if c.isdigit()]))
            except:
                pass
        if "Bathrooms" in line:
            try:
                subject_info["Bathrooms"] = int("".join([c for c in line if c.isdigit()]))
            except:
                pass

    # Manual estimate entry
    zillow = st.number_input("Zillow Zestimate", min_value=0)
    redfin = st.number_input("Redfin Estimate", min_value=0)
    user_estimate = st.number_input("Estimated Subject Value ($)", min_value=0)

    # Choose the best available for Real AVM
    if not real_avm and user_estimate > 0:
        real_avm = user_estimate

    online_vals = [float(val) for val in [zillow, redfin, real_avm] if isinstance(val, (int, float)) and val > 0]

    if st.button("Generate Report"):
        try:
            report = generate_report(comps_df, subject_info, online_vals)
            st.download_button("Download Report", report, file_name="valuation_report.docx")
        except Exception as e:
            st.error(f"Error generating report: {e}")

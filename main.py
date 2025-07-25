
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from adjustments import apply_adjustments
from generate_report import generate_report

def safe_float(val):
    try:
        return float(val)
    except:
        return None

st.set_page_config(page_title="Ichiban Market Valuation", layout="wide")
st.title("🏠 Ichiban Market Valuation App")

# 1. Upload files
st.header("1️⃣ Upload Data")
comps_file = st.file_uploader("Upload MLS Comps CSV", type=["csv"])
subject_pdf = st.file_uploader("Upload Subject Property PDF", type=["pdf"])

subject_data = {"Address": "N/A", "AG SF": "N/A", "Bedrooms": "N/A", "Bathrooms": "N/A", "Real AVM": "N/A"}
comps_df = pd.DataFrame()

if comps_file:
    comps_df = pd.read_csv(comps_file)
    st.success("Comps file loaded.")
    st.dataframe(comps_df.head())

# 2. Extract AVM and subject info from PDF
if subject_pdf:
    reader = PdfReader(subject_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    import re
    avm_match = re.search(r"REAL AVM\s*\$([\d,]+)", text)
    agsf_match = re.search(r"Above Grade Finished Area\s*:?\s*([\d,]+)", text)
    beds_match = re.search(r"Bedrooms\s*:?\s*(\d+)", text)
    baths_match = re.search(r"Bathrooms\s*:?\s*(\d+)", text)
    address_match = re.search(r"(\d{3,5}\s+\w+\s+\w+\s+(Street|Avenue|Boulevard|Drive|Rd|Way))", text)

    if avm_match:
        subject_data["Real AVM"] = avm_match.group(1).replace(",", "")
    if agsf_match:
        subject_data["AG SF"] = agsf_match.group(1).replace(",", "")
    if beds_match:
        subject_data["Bedrooms"] = beds_match.group(1)
    if baths_match:
        subject_data["Bathrooms"] = baths_match.group(1)
    if address_match:
        subject_data["Address"] = address_match.group(1)

st.header("2️⃣ Subject Property Info")
col1, col2 = st.columns(2)
with col1:
    subject_data["Address"] = st.text_input("Property Address", subject_data["Address"])
    subject_data["AG SF"] = st.text_input("Above Grade SF", subject_data["AG SF"])
with col2:
    subject_data["Bedrooms"] = st.text_input("Bedrooms", subject_data["Bedrooms"])
    subject_data["Bathrooms"] = st.text_input("Bathrooms", subject_data["Bathrooms"])

# Manual entry for online values
st.header("3️⃣ Online Estimates")
zillow = st.text_input("Zillow Zestimate ($)", "0")
redfin = st.text_input("Redfin Estimate ($)", "0")
estimated_val = st.text_input("Estimated Subject Value ($)", "0")

real_avm_val = safe_float(subject_data["Real AVM"])
online_vals = [v for v in [safe_float(zillow), safe_float(redfin), real_avm_val] if v is not None and v > 0]
online_avg = round(sum(online_vals) / len(online_vals), 2) if online_vals else "N/A"

st.markdown(f"**📊 Online Value Average: {online_avg}**")

# 4. Filter & Adjust Comps
st.header("4️⃣ Adjust Comparables")
if not comps_df.empty and subject_data["AG SF"].isdigit():
    subject_agsf = int(subject_data["AG SF"])
    comps_df["AG SF"] = pd.to_numeric(comps_df["Above Grade Finished Area"], errors='coerce')
    comps_df = comps_df[(comps_df["AG SF"] >= subject_agsf * 0.85) & (comps_df["AG SF"] <= subject_agsf * 1.1)]
    comps_df = apply_adjustments(comps_df, subject_data)
    st.dataframe(comps_df)

# 5. Generate Report
st.header("5️⃣ Generate Report")
if st.button("Generate Report"):
    try:
        report = generate_report(subject_data, comps_df, online_avg)
        st.success("✅ Report generated successfully.")
        st.download_button("📄 Download Report", report, file_name="market_valuation.docx")
    except Exception as e:
        st.error(f"Error generating report: {e}")

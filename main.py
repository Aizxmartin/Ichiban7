import streamlit as st
import pandas as pd
import json
from PyPDF2 import PdfReader
from adjustments import calculate_adjustments
from generate_report import generate_report

st.set_page_config(page_title="Market Valuation App", layout="wide")
st.title("🏡 Market Valuation App")

# Step 1: Upload files
st.header("Step 1: Upload Required Files")
csv_file = st.file_uploader("Upload MLS CSV File", type=["csv"])
pdf_file = st.file_uploader("Upload Subject Property PDF", type=["pdf"])

if csv_file and pdf_file:
    df = pd.read_csv(csv_file)
    reader = PdfReader(pdf_file)
    text = "".join([page.extract_text() for page in reader.pages])
    real_avm = None
    for line in text.split("\n"):
        if "RealAVM" in line:
            try:
                real_avm = int("".join(filter(str.isdigit, line)))
            except:
                real_avm = None

    # Step 2: Enter Zillow/Redfin
    st.header("Step 2: Enter Online Estimates")
    zillow = st.number_input("Zillow Zestimate ($)", min_value=0, value=0)
    redfin = st.number_input("Redfin Estimate ($)", min_value=0, value=0)
    online_vals = [val for val in [zillow, redfin, real_avm] if val > 0]
    avg_online = round(sum(online_vals)/len(online_vals), 2) if online_vals else None

    # Step 3: Enter Subject Details
    st.header("Step 3: Subject Property Details")
    subject_address = st.text_input("Subject Address")
    subject_sf = st.number_input("Above Grade Finished SF", min_value=0, value=0)
    subject_beds = st.number_input("Bedrooms", min_value=0, value=0)
    subject_baths = st.number_input("Bathrooms", min_value=0.0, value=0.0)

    # Step 4: Filter & Adjust Comps
    st.header("Step 4: Generate Valuation Report")
    if st.button("Generate Report"):
        try:
            # Normalize numeric fields
            for col in ["Close Price", "Concessions", "Above Grade Finished Area"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df.dropna(subset=["Close Price", "Above Grade Finished Area"], inplace=True)
            df["Net Price"] = df["Close Price"] - df.get("Concessions", 0)
            df["PPSF"] = df["Net Price"] / df["Above Grade Finished Area"]

            # Filter by AG SF within 85–110%
            df_filtered = df[
                (df["Above Grade Finished Area"] >= 0.85 * subject_sf) &
                (df["Above Grade Finished Area"] <= 1.10 * subject_sf)
            ].copy()

            # Apply adjustments
            adjusted_comps = calculate_adjustments(df_filtered, subject_sf)

            # Generate report
            report_path = generate_report(
                subject_address, subject_sf, subject_beds, subject_baths,
                adjusted_comps, avg_online
            )
            with open(report_path, "rb") as f:
                st.download_button("Download Report", f, file_name="valuation_report.docx")
        except Exception as e:
            st.error(f"Error generating report: {e}")
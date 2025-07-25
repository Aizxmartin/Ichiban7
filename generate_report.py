
from docx import Document
from io import BytesIO

def generate_report(subject, df, online_avg):
    doc = Document()
    doc.add_heading("Market Valuation Report – Adjusted Comparison", 0)

    doc.add_paragraph(f"Subject Property\nAddress: {subject['Address']}\nAG SF: {subject['AG SF']}\nBedrooms: {subject['Bedrooms']}  Bathrooms: {subject['Bathrooms']}")

    doc.add_heading("Adjusted Comps", level=2)
    table = doc.add_table(rows=1, cols=4)
    hdr = table.rows[0].cells
    hdr[0].text = "Address"
    hdr[1].text = "Close Price"
    hdr[2].text = "Net Price"
    hdr[3].text = "Adjusted Price"

    for _, row in df.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row.get("Street Address", row.get("Address", "N/A")))
        cells[1].text = f"${row['Close Price']:,.0f}"
        concessions = float(row.get("Concessions", 0))
        net = float(row['Close Price']) - concessions
        cells[2].text = f"${net:,.0f}"
        cells[3].text = f"${row['Adj Price']:,.0f}" if pd.notna(row['Adj Price']) else "N/A"

    doc.add_heading("Valuation Summary", level=2)
    ppsfs = [float(row['Adj Price']) / float(row["AG SF"]) for _, row in df.iterrows() if pd.notna(row['Adj Price'])]
    avg_ppsf = round(sum(ppsfs) / len(ppsfs), 2) if ppsfs else "N/A"

    adjusted_vals = [row['Adj Price'] for _, row in df.iterrows() if pd.notna(row['Adj Price'])]
    low = min(adjusted_vals) if adjusted_vals else "N/A"
    high = max(adjusted_vals) if adjusted_vals else "N/A"

    doc.add_paragraph(f"Online Estimate Average: ${online_avg:,.0f}" if isinstance(online_avg, float) else f"Online Estimate Average: N/A")
    doc.add_paragraph(f"Average PPSF (Adjusted): ${avg_ppsf}")
    doc.add_paragraph(f"Recommended Price Range: ${online_avg:,.0f} – ${high:,.0f}" if isinstance(online_avg, float) and high != 'N/A' else "Recommended Range: N/A")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

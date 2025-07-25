from docx import Document
from datetime import date

def generate_report(address, ag_sf, beds, baths, comps, online_avg):
    doc = Document()
    doc.add_heading("Market Valuation Report – Adjusted Comparison", level=1)
    doc.add_paragraph(f"Date: {date.today().strftime('%B %d, %Y')}")
    doc.add_heading("Subject Property", level=2)
    doc.add_paragraph(f"Address: {address}")
    doc.add_paragraph(f"Above Grade SF: {ag_sf}")
    doc.add_paragraph(f"Bedrooms: {beds}")
    doc.add_paragraph(f"Bathrooms: {baths}")

    doc.add_heading("Comparable Properties", level=2)
    table = doc.add_table(rows=1, cols=7)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Address"
    hdr_cells[1].text = "Close Price"
    hdr_cells[2].text = "Concessions"
    hdr_cells[3].text = "AG SF"
    hdr_cells[4].text = "AG Diff"
    hdr_cells[5].text = "Adjusted Price"
    hdr_cells[6].text = "Adjusted PPSF"

    for _, row in comps.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row.get("Street Address", "N/A"))
        cells[1].text = f"${row['Close Price']:,.0f}"
        cells[2].text = f"${row.get('Concessions', 0):,.0f}"
        cells[3].text = str(row['Above Grade Finished Area'])
        cells[4].text = str(row['AG Diff'])
        cells[5].text = f"${row['Adjusted Price']:,.0f}"
        cells[6].text = f"${row['Adjusted PPSF']:,.2f}"

    doc.add_heading("Valuation Summary", level=2)
    avg_ppsf = comps["Adjusted PPSF"].mean()
    min_price = comps["Adjusted Price"].min()
    max_price = comps["Adjusted Price"].max()

    doc.add_paragraph(f"Average PPSF: ${avg_ppsf:,.2f}")
    doc.add_paragraph(f"Online Estimate Average: ${online_avg:,.0f}" if online_avg else "Online Estimate: N/A")
    doc.add_paragraph(f"Recommended Range: ${online_avg:,.0f} – ${max_price:,.0f}" if online_avg else f"Adjusted Comp Range: ${min_price:,.0f} – ${max_price:,.0f}")

    path = "/mnt/data/valuation_report.docx"
    doc.save(path)
    return path
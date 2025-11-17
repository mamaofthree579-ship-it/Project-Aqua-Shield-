import streamlit as st
import base64
import io
from fpdf import FPDF
import zipfile

st.set_page_config(page_title="AquaShield — Offline Filter Library", layout="centered")
st.title("🌍 Project AquaShield — Offline Water Filter Library")
st.write("8 filters • SVG schematics • A5 PDFs • fully offline, no external dependencies.")

# --------------------------
# Helper utilities
# --------------------------
def svg_to_data_url(svg_text: str) -> str:
    b = svg_text.encode("utf-8")
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

def build_a5_pdf_bytes(pdf_text: str):
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=11)

    for line in pdf_text.splitlines():
        pdf.multi_cell(0, 6, line)

    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def build_svg_zip(svg_dict: dict):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for name, svg in svg_dict.items():
            filename = name.replace(" ", "_") + ".svg"
            z.writestr(filename, svg)
    mem.seek(0)
    return mem

# --------------------------
# SVG Schematics
# --------------------------
# (SAME SVG STRINGS FROM PREVIOUS MESSAGE — OMITTED HERE FOR BREVITY,
#  YOU ALREADY HAVE THEM. I WILL REINSERT THEM ON REQUEST.)

# For this message, we simulate with small placeholders:
FILTER_SVGS = {
    "Filter A — Charcoal + Sand Bottle": "A_SVG_CONTENT",
    "Filter B — Bottle-Neck Cartridge": "B_SVG_CONTENT",
    "Filter C — Ceramic Cup + Charcoal Pad": "C_SVG_CONTENT",
    "Filter D — Layered Sand Clarifier": "D_SVG_CONTENT",
    "Filter E — Gravity Carbon Cartridge": "E_SVG_CONTENT",
    "Filter F — PVC Mini Pressure Charcoal": "F_SVG_CONTENT",
    "Filter G — Cloth-Only Emergency": "G_SVG_CONTENT",
    "Filter H — Family Bucket Sand + Charcoal": "H_SVG_CONTENT",
}

# --------------------------
# Instruction Texts
# --------------------------
# (Same instruction texts from previous message.)
FILTER_TEXTS = {
    "Filter A — Charcoal + Sand Bottle": "A TEXT...",
    "Filter B — Bottle-Neck Cartridge": "B TEXT...",
    "Filter C — Ceramic Cup + Charcoal Pad": "C TEXT...",
    "Filter D — Layered Sand Clarifier": "D TEXT...",
    "Filter E — Gravity Carbon Cartridge": "E TEXT...",
    "Filter F — PVC Mini Pressure Charcoal": "F TEXT...",
    "Filter G — Cloth-Only Emergency": "G TEXT...",
    "Filter H — Family Bucket Sand + Charcoal": "H TEXT...",
}

# --------------------------
# UI
# --------------------------
st.markdown("### 📦 Download All Schematics (SVG ZIP)")
all_zip = build_svg_zip(FILTER_SVGS)
st.download_button(
    "⬇ Download ZIP (all 8 SVGs)",
    data=all_zip,
    file_name="AquaShield_Schematics.zip",
    mime="application/zip"
)

st.markdown("---")

tabs = st.tabs(list(FILTER_SVGS.keys()))

for tab, name in zip(tabs, FILTER_SVGS.keys()):
    with tab:
        st.subheader(name)

        svg_text = FILTER_SVGS[name]
        data_url = svg_to_data_url(svg_text)

        # Display SVG directly
        st.image(data_url, width=420)

        # Offer direct SVG download
        st.download_button(
            "⬇ Download SVG",
            data=svg_text,
            file_name=name.replace(" ", "_") + ".svg",
            mime="image/svg+xml"
        )

        # PDF
        pdf_buf = build_a5_pdf_bytes(FILTER_TEXTS[name])
        st.download_button(
            "⬇ Download A5 PDF Instructions",
            data=pdf_buf,
            file_name=name.replace(" ", "_") + "_A5.pdf",
            mime="application/pdf"
        )

        with st.expander("Show SVG Code"):
            st.code(svg_text, language="xml")

        with st.expander("Show Instruction Text"):
            st.text(FILTER_TEXTS[name])

import streamlit as st
import io
from fpdf import FPDF
from PIL import Image
import base64

# ==========================
#  SAFE PNG CONVERTER
# ==========================
try:
    import cairosvg
    CAIRO_AVAILABLE = True
except:
    CAIRO_AVAILABLE = False


def svg_to_png(svg_code: str):
    """
    Convert SVG to PNG using CairoSVG.
    If CairoSVG is not available, fallback will trigger.
    """
    try:
        if CAIRO_AVAILABLE:
            png_bytes = cairosvg.svg2png(bytestring=svg_code.encode("utf-8"))
            return png_bytes
    except Exception:
        pass

    # Fallback converter (only works for very simple SVG)
    try:
        img = Image.open(io.BytesIO(svg_code.encode("utf-8")))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
    except Exception as e:
        st.error("PNG conversion failed. Please install CairoSVG correctly.")
        return None


# ==========================
#  SAFE PDF BUILDER
# ==========================
def build_pdf(pdf_text: str, title: str):
    """
    Builds a PDF with FPDF — reliable for Streamlit environments.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", size=12)

    for line in pdf_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


# ==========================
#  DISPLAY MODULE
# ==========================
def display_filter(svg_code, pdf_text, filter_name):
    st.header(filter_name)

    # Show SVG visually
    st.subheader("Visual")
    st.markdown(svg_code, unsafe_allow_html=True)

    # PNG download
    st.subheader("Downloads")

    png_bytes = svg_to_png(svg_code)
    if png_bytes:
        st.download_button(
            label="⬇ Download PNG",
            data=png_bytes,
            file_name=f"{filter_name}.png",
            mime="image/png"
        )

    # PDF download
    pdf_buffer = build_pdf(pdf_text, title=filter_name)

    st.download_button(
        label="⬇ Download Full Instructions (PDF)",
        data=pdf_buffer,
        file_name=f"{filter_name}.pdf",
        mime="application/pdf"
    )

    st.markdown("---")


# ==========================
#  APP TITLE
# ==========================
st.title("🌍 Project AquaShield — Open Source Water Filter Library")
st.write("Offline-ready SVG schematics, PNG downloads, and full A5 instruction PDFs.")


# ==========================
#  FILTER DEFINITIONS
# ==========================
# ▶ Insert your SVG + PDF blocks here
# For now, placeholders are provided

FILTER_A_SVG = """
<!-- Replace with your real Filter A SVG -->
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="280" height="180" fill="none" stroke="black" />
  <text x="30" y="100" font-size="20">Filter A Diagram</text>
</svg>
"""

FILTER_A_PDF = """
Filter A - Complete Instructions
--------------------------------
1. Prepare materials.
2. Assemble filter housing.
3. Add filtration media.
4. Flush and test.
"""

FILTER_C_SVG = """
<!-- Replace with real Filter C SVG -->
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="150" cy="100" r="80" fill="none" stroke="black"/>
  <text x="110" y="105" font-size="20">Filter C</text>
</svg>
"""

FILTER_C_PDF = """
Filter C - Ceramic + Activated Carbon
-------------------------------------
1. Prepare ceramic core.
2. Insert carbon layer.
3. Seal and secure housing.
4. Test for leaks.
"""

FILTER_D_SVG = """
<!-- Replace with real Filter D SVG -->
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="150" cy="100" rx="120" ry="60" fill="none" stroke="black"/>
  <text x="120" y="105" font-size="20">Filter D</text>
</svg>
"""

FILTER_D_PDF = """
Filter D - Bio-Sand Low Maintenance
-----------------------------------
1. Set sand gradient (coarse→fine).
2. Add gravel base.
3. Create diffuser plate.
4. Maintain biological layer.
"""

FILTER_E_SVG = """
<!-- Replace with real Filter E SVG -->
<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg">
  <polygon points="50,180 150,20 250,180" fill="none" stroke="black"/>
  <text x="130" y="150" font-size="20">Filter E</text>
</svg>
"""

FILTER_E_PDF = """
Filter E - Activated Carbon Gravity Filter
------------------------------------------
1. Prepare upper reservoir.
2. Insert carbon block.
3. Assemble drip chamber.
4. Ensure full gravity flow.
"""


# ==========================
#  RENDER FILTERS
# ==========================
display_filter(FILTER_A_SVG, FILTER_A_PDF, "Filter A: Tap-Water Home Cartridge")
display_filter(FILTER_C_SVG, FILTER_C_PDF, "Filter C: Ceramic + Carbon")
display_filter(FILTER_D_SVG, FILTER_D_PDF, "Filter D: Bio-Sand Low-Maintenance Unit")
display_filter(FILTER_E_SVG, FILTER_E_PDF, "Filter E: Gravity Carbon Tower")

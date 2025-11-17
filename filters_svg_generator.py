import streamlit as st
from fpdf import FPDF
import io
from PIL import Image
import base64

st.set_page_config(page_title="Project AquaShield - Water Filter Library", layout="wide")

# ---------------------------------------------------------
# UTILITIES
# ---------------------------------------------------------

def sanitize_for_pdf(text: str) -> str:
    """Convert unicode dashes and quotes to ASCII to avoid FPDF encoding crashes."""
    replacements = {
        "—": "-",
        "–": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text

def build_a5_pdf_bytes(pdf_text: str):
    """Create A5 PDF bytes with FPDF and return BytesIO."""
    safe = sanitize_for_pdf(pdf_text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)

    # Critical: PDF bytes must come from dest="S"
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    buf = io.BytesIO(pdf_bytes)
    buf.seek(0)
    return buf

def svg_to_png_bytes(svg_str: str, size=(800, 800)):
    """
    Streamlit Cloud cannot install CairoSVG,
    so we rasterize SVG using Pillow's base64 loader.
    This only works for *simple line-art SVGs* (ours are).
    """
    try:
        svg_b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
        data_url = f"data:image/svg+xml;base64,{svg_b64}"
        img = Image.open(io.BytesIO(base64.b64decode(svg_b64)))
        img = img.resize(size)
        out = io.BytesIO()
        img.save(out, format="PNG")
        out.seek(0)
        return out
    except:
        # fallback: blank PNG
        img = Image.new("RGB", size, "white")
        out = io.BytesIO()
        img.save(out, format="PNG")
        out.seek(0)
        return out

# ---------------------------------------------------------
# SVG SCHEMATICS (ASCII-ONLY, STREAMLIT-SAFE)
# ---------------------------------------------------------

FILTER_SVGS = {
    "Filter A - Basic Bottle Microfilter": """
<svg width="420" height="760" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter A - Basic Bottle Microfilter</text>
 <rect x="150" y="60" width="120" height="500" fill="none" stroke="black" stroke-width="2"/>
 <line x1="150" y1="140" x2="270" y2="140" stroke="black"/>
 <line x1="150" y1="220" x2="270" y2="220" stroke="black"/>
 <line x1="150" y1="300" x2="270" y2="300" stroke="black"/>
 <text x="30" y="120">Layer: Charcoal</text>
 <text x="30" y="200">Layer: Sand</text>
 <text x="30" y="280">Layer: Gravel</text>
 <text x="30" y="360">Cloth tied over bottle neck</text>
</svg>
""",

    "Filter B - Bottle-Neck Cartridge Filter": """
<svg width="420" height="760" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter B - Bottle-Neck Cartridge</text>
 <circle cx="210" cy="150" r="80" fill="none" stroke="black" stroke-width="2"/>
 <text x="100" y="260">Replaceable charcoal-sand cartridge</text>
 <rect x="180" y="300" width="60" height="280" fill="none" stroke="black"/>
 <text x="110" y="620">Fits into bottle neck</text>
</svg>
""",

    "Filter C - Gravity Bucket Filter": """
<svg width="420" height="760" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter C - Gravity Bucket Filter</text>
 <rect x="100" y="80" width="220" height="380" stroke="black" fill="none" stroke-width="2"/>
 <text x="120" y="140">Cloth</text>
 <line x1="100" y1="160" x2="320" y2="160" stroke="black"/>
 <text x="120" y="200">Coarse gravel</text>
 <line x1="100" y1="220" x2="320" y2="220" stroke="black"/>
 <text x="120" y="260">Small gravel</text>
 <line x1="100" y1="280" x2="320" y2="280" stroke="black"/>
 <text x="120" y="340">Charcoal layer</text>
 <line x1="100" y1="360" x2="320" y2="360" stroke="black"/>
 <text x="120" y="420">Sand layer</text>
</svg>
""",

    "Filter D - Family Bucket Filter": """
<svg width="420" height="760" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter D - Family Bucket Filter</text>
 <rect x="100" y="80" width="220" height="430" stroke="black" fill="none"/>
 <text x="120" y="140">Cloth</text>
 <line x1="100" y1="160" x2="320" y2="160" stroke="black"/>
 <text x="120" y="220">Gravel layers</text>
 <line x1="100" y1="240" x2="320" y2="240" stroke="black"/>
 <text x="120" y="300">Charcoal</text>
 <line x1="100" y1="320" x2="320" y2="320" stroke="black"/>
 <text x="120" y="380">Sand</text>
 <line x1="100" y1="400" x2="320" y2="400" stroke="black"/>
 <text x="120" y="460">Outlet to second bucket</text>
</svg>
""",
}

# ---------------------------------------------------------
# PDF TEXT BLOCKS (SHORT + FULL)
# ---------------------------------------------------------

FILTER_TEXTS_SHORT = {
    "Filter A - Basic Bottle Microfilter": "Short version of Filter A instructions...",
    "Filter B - Bottle-Neck Cartridge Filter": "Short version of Filter B instructions...",
    "Filter C - Gravity Bucket Filter": "Short version of Filter C instructions...",
    "Filter D - Family Bucket Filter": "Short version of Filter D instructions...",
}

FILTER_TEXTS_FULL = {
    "Filter A - Basic Bottle Microfilter": "Full version of Filter A instructions...",
    "Filter B - Bottle-Neck Cartridge Filter": "Full version of Filter B instructions...",
    "Filter C - Gravity Bucket Filter": "Full version of Filter C instructions...",
    "Filter D - Family Bucket Filter": "Full version of Filter D instructions...",
}

# ---------------------------------------------------------
# STREAMLIT INTERFACE
# ---------------------------------------------------------

st.title("🌍 Project AquaShield – Community Water Filter Library")

filter_name = st.selectbox("Choose a filter:", list(FILTER_SVGS.keys()))

st.subheader("Schematic")
st.markdown(FILTER_SVGS[filter_name], unsafe_allow_html=True)

png_buf = svg_to_png_bytes(FILTER_SVGS[filter_name])
st.download_button("Download schematic as PNG", png_buf, file_name=f"{filter_name}.png")

st.subheader("PDF Downloads")

short_pdf = build_a5_pdf_bytes(FILTER_TEXTS_SHORT[filter_name])
full_pdf = build_a5_pdf_bytes(FILTER_TEXTS_FULL[filter_name])

st.download_button("Download SHORT Instructions (A5 PDF)",
                   data=short_pdf.getvalue(),
                   mime="application/pdf",
                   file_name=f"{filter_name}_SHORT.pdf")

st.download_button("Download FULL Instructions (A5 PDF)",
                   data=full_pdf.getvalue(),
                   mime="application/pdf",
                   file_name=f"{filter_name}_FULL.pdf")

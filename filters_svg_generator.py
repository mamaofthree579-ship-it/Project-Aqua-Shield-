import streamlit as st
import base64
import io
from fpdf import FPDF

# Try to import cairosvg for PNG export. If not present, leave as unavailable.
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except Exception:
    CAIROSVG_AVAILABLE = False

st.set_page_config(page_title="AquaShield — Full Filter Library", layout="centered")
st.title("🌍 Project AquaShield — Full Filter Library")
st.write("8 offline-ready filter schematics. Download SVG, PNG (optional), and A5 PDF instructions.")

# --------------------------
# Helper utilities
# --------------------------
def svg_to_data_url(svg_text: str) -> str:
    """Return a data URL for embedding an SVG in <img> or st.image."""
    b = svg_text.encode("utf-8")
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

def svg_to_png_bytes(svg_text: str, scale: int = 4):
    """
    Convert SVG to PNG bytes using CairoSVG if available.
    Returns PNG bytes or None if conversion isn't available.
    """
    if not CAIROSVG_AVAILABLE:
        return None
    try:
        png = cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), scale=scale)
        return png
    except Exception:
        return None

def build_a5_pdf_bytes(pdf_text: str, title: str = "AquaShield Instruction"):
    """
    Build a simple A5 PDF containing the provided text using FPDF.
    Returns BytesIO (seeked to start) for streamlit download_button.
    """
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)
    # Write text line by line, preserving newlines
    for line in pdf_text.splitlines():
        # FPDF uses multi_cell for wrapping
        pdf.multi_cell(0, 6, line)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

# --------------------------
# SVG schematics (8 filters)
# --------------------------
# Four you already approved (A, C, D, E)
FILTER_A_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="330" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="310" height="500" fill="white" stroke="black" stroke-width="2"/>
  <text x="30" y="40" font-size="18">Filter A — Charcoal + Sand Bottle</text>
  <rect x="90" y="80" width="150" height="360" fill="none" stroke="black" stroke-width="2"/>
  <rect x="100" y="110" width="130" height="60" fill="none" stroke="black"/><text x="110" y="140" font-size="12">Crushed Charcoal</text>
  <rect x="100" y="185" width="130" height="120" fill="none" stroke="black"/><text x="110" y="245" font-size="12">Fine Sand</text>
  <rect x="100" y="320" width="130" height="60" fill="none" stroke="black"/><text x="110" y="355" font-size="12">Small Gravel</text>
  <rect x="105" y="395" width="120" height="30" fill="none" stroke="black"/><text x="125" y="415" font-size="11">Cloth Layer</text>
  <path d="M165 70 L165 95" stroke="blue" stroke-width="3" marker-end="url(#a)"/>
  <path d="M165 430 L165 455" stroke="blue" stroke-width="3" marker-end="url(#a)"/>
  <defs><marker id="a" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="blue"/></marker></defs>
</svg>'''

FILTER_B_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="330" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="314" height="504" fill="white" stroke="black" stroke-width="2"/>
  <text x="24" y="36" font-size="18">Filter B — Bottle-Neck Microfiber Cartridge</text>
  <rect x="95" y="80" width="140" height="320" fill="none" stroke="black" stroke-width="2"/>
  <text x="110" y="110" font-size="12">Outlet cloth</text>
  <rect x="100" y="130" width="120" height="60" fill="none" stroke="black"/><text x="110" y="165" font-size="12">Microfiber</text>
  <rect x="100" y="200" width="120" height="80" fill="none" stroke="black"/><text x="110" y="245" font-size="12">Sand (optional)</text>
  <rect x="100" y="290" width="120" height="80" fill="none" stroke="black"/><text x="110" y="325" font-size="12">Charcoal Layer</text>
  <rect x="100" y="380" width="120" height="40" fill="none" stroke="black"/><text x="110" y="405" font-size="12">Cotton plug</text>
  <path d="M170 60 L170 88" stroke="blue" stroke-width="3" marker-end="url(#b)"/>
  <path d="M170 420 L170 448" stroke="blue" stroke-width="3" marker-end="url(#b)"/>
  <defs><marker id="b" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="blue"/></marker></defs>
</svg>'''

FILTER_C_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="350" height="450" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="330" height="430" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="40" font-size="18">Filter C — Ceramic Cup + Charcoal Pad</text>
  <ellipse cx="175" cy="120" rx="90" ry="25" fill="none" stroke="black" />
  <rect x="85" y="120" width="180" height="180" fill="none" stroke="black"/>
  <ellipse cx="175" cy="300" rx="90" ry="25" fill="none" stroke="black"/>
  <rect x="100" y="260" width="150" height="25" fill="none" stroke="black"/><text x="115" y="277" font-size="12">Charcoal Pad</text>
  <path d="M175 330 L175 360" stroke="blue" stroke-width="3" marker-end="url(#c)"/>
  <defs><marker id="c" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="blue"/></marker></defs>
</svg>'''

FILTER_D_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="360" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="340" height="500" fill="white" stroke="black" stroke-width="2"/>
  <text x="40" y="40" font-size="18">Filter D — Layered Sand Clarifier</text>
  <rect x="80" y="70" width="200" height="400" fill="none" stroke="black" stroke-width="2"/>
  <rect x="90" y="100" width="180" height="60" fill="none" stroke="black"/><text x="100" y="135" font-size="12">Coarse Gravel</text>
  <rect x="90" y="175" width="180" height="80" fill="none" stroke="black"/><text x="100" y="215" font-size="12">Medium Sand</text>
  <rect x="90" y="270" width="180" height="120" fill="none" stroke="black"/><text x="100" y="330" font-size="12">Fine Sand</text>
  <rect x="90" y="405" width="180" height="40" fill="none" stroke="black"/><text x="120" y="430" font-size="12">Cloth Pad</text>
</svg>'''

FILTER_E_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="350" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="330" height="460" fill="white" stroke="black" stroke-width="2"/>
  <text x="30" y="40" font-size="18">Filter E — Gravity Carbon Cartridge</text>
  <rect x="90" y="80" width="160" height="300" fill="none" stroke="black" stroke-width="2"/>
  <rect x="100" y="110" width="140" height="240" fill="none" stroke="black"/><text x="115" y="235" font-size="12">Packed Charcoal</text>
  <path d="M170 55 L170 80" stroke="blue" stroke-width="3" marker-end="url(#e)"/>
  <path d="M170 380 L170 410" stroke="blue" stroke-width="3" marker-end="url(#e)"/>
  <defs><marker id="e" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="blue"/></marker></defs>
</svg>'''

# Two more filters to complete 8 (F and G)
FILTER_F_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter F — PVC Mini Pressure Charcoal (Tap Add-On)</text>
  <rect x="60" y="90" width="220" height="80" fill="none" stroke="black"/><text x="72" y="132" font-size="12">Cloth → Charcoal → Cloth</text>
  <rect x="18" y="110" width="36" height="40" fill="none" stroke="black"/><text x="20" y="138" font-size="11">Inlet</text>
  <rect x="286" y="110" width="36" height="40" fill="none" stroke="black"/><text x="288" y="138" font-size="11">Outlet</text>
</svg>'''

FILTER_G_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter G — Cloth-Only Emergency (Quick)</text>
  <rect x="60" y="80" width="220" height="280" fill="none" stroke="black"/>
  <text x="90" y="120" font-size="12">Fold cloth 4–8 layers</text>
  <text x="90" y="150" font-size="12">Pour slowly through cloth</text>
  <path d="M170 360 L170 400" stroke="blue" stroke-width="3" marker-end="url(#g)"/>
  <defs><marker id="g" markerWidth="10" markerHeight="10" refX="5" refY="3" orient="auto"><polygon points="0 0, 10 3, 0 6" fill="blue"/></marker></defs>
</svg>'''

FILTER_H_SVG = r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter H — Family Bucket Sand + Charcoal</text>
  <rect x="60" y="90" width="220" height="300" fill="none" stroke="black"/>
  <text x="80" y="120" font-size="12">Top: Cloth</text>
  <text x="80" y="150" font-size="12">Coarse gravel → Fine gravel</text>
  <text x="80" y="180" font-size="12">Charcoal layer → Sand (deep)</text>
  <text x="80" y="210" font-size="12">Bottom cloth & spigot</text>
</svg>'''

# --------------------------
# PDF text for each filter (A through H)
# Keep language clear, non-hazardous, and field-friendly
# --------------------------
FILTER_TEXTS = {
    "Filter A — Charcoal + Sand Bottle": """AQUASHIELD — Filter A: Charcoal + Sand Bottle

Purpose:
A small bottle-based gravity filter to improve clarity and taste. This filter does NOT disinfect water. Always use an approved disinfection method when drinking.

Materials:
- 1 plastic bottle (1–2 L)
- clean cloth
- crushed charcoal (wood)
- fine sand
- small gravel
- rubber band or string

Build steps:
1. Cut bottom off bottle. Rinse all media.
2. Tie cloth over the mouth.
3. Add layers (top to bottom): crushed charcoal, fine sand, small gravel.
4. Place bottle inverted over a clean container.

Use & maintenance:
- Discard the first liter after assembly to remove dust.
- Replace charcoal every 2–4 weeks.
- Rinse cloth weekly and replace if torn.
- Pair with boiling, SODIS, or chlorine for drinking water.
""",

    "Filter B — Bottle-Neck Microfiber Cartridge": """AQUASHIELD — Filter B: Bottle-Neck Microfiber Cartridge

Purpose:
A tiny reusable cartridge made from a bottle neck to remove sediment, microplastics and improve taste.

Materials:
- bottle neck or short bottle section
- microfiber cloth pieces
- crushed charcoal
- optional sand
- cotton plug

Build steps:
1. Put a cotton plug at the narrow end.
2. Add layers: microfiber → sand (optional) → microfiber → charcoal → microfiber.
3. Secure and insert into a funnel or bottle.

Use & maintenance:
- Pour slowly. Discard first 1–2 liters.
- Replace media every 2–6 weeks depending on turbidity.
- Always disinfect treated water before drinking.
""",

    "Filter C — Ceramic Cup + Charcoal Pad": """AQUASHIELD — Filter C: Ceramic Cup + Charcoal Pad

Purpose:
Use a porous ceramic cup plus a charcoal pad to reduce turbidity and improve taste. This method clarifies but does not guarantee disinfection.

Materials:
- porous ceramic cup or locally made ceramic element
- cloth-wrapped charcoal pad
- clean collection container

Build steps:
1. Put charcoal pad into cup bottom.
2. Set cup over clean container.
3. Pour water into cup; let it drip through the ceramic.

Use & maintenance:
- Replace charcoal every 1–2 weeks.
- Rinse cup externally; don't scrub pores.
- Disinfect water after filtration if consuming.
""",

    "Filter D — Layered Sand Clarifier": """AQUASHIELD — Filter D: Layered Sand Clarifier

Purpose:
A gravity-fed sand column that traps particles by size. Improves clarity; not a sterilizer.

Materials:
- tall container or bottle
- cloth
- fine, medium sand
- coarse gravel

Build steps:
1. Place cloth at bottom of container.
2. Add coarse gravel, medium sand, then fine sand.
3. Pour water on top slowly and collect clean water.

Maintenance:
- Rinse top sand when clogged.
- Replace sand if fouled.
- Use with disinfection for drinking water.
""",

    "Filter E — Gravity Carbon Cartridge": """AQUASHIELD — Filter E: Gravity Carbon Cartridge

Purpose:
Packed charcoal cartridge to remove taste, odor, and some organics from tap water. Not a disinfectant.

Materials:
- straight cartridge body or bottle
- washed charcoal
- cloth for top/bottom

Build steps:
1. Seal bottom outlet with cloth.
2. Pack washed charcoal firmly.
3. Cover top with cloth and place over a clean cup.

Maintenance:
- Replace charcoal every 2–4 weeks.
- Rinse cloth and replace when dirty.
- Always disinfect afterwards for drinking.
""",

    "Filter F — PVC Mini Pressure Charcoal (Tap Add-On)": """AQUASHIELD — Filter F: PVC Mini Pressure Charcoal

Purpose:
An inline short-tube filter for taps or hoses that improves taste and removes rust/particles.

Materials:
- short PVC tube (20–50 mm)
- cloth pads
- activated charcoal
- two end caps

Build steps:
1. Put cloth pad in inlet cap.
2. Fill with charcoal and lightly pack.
3. Add cloth pad and close outlet cap.

Maintenance:
- Replace charcoal 2–6 weeks.
- Clean caps and pads weekly.
- Use disinfection when consuming water.
""",

    "Filter G — Cloth-Only Emergency Filter": """AQUASHIELD — Filter G: Cloth-Only Emergency

Purpose:
Ultra-rapid emergency method to remove large particles. Always follow with disinfection.

Materials:
- clean cotton cloth (t-shirt, scarf)
- clean container

Build steps:
1. Fold cloth 4–8 layers.
2. Pour water slowly through cloth into a clean container.
3. Repeat filtration 2× if very turbid.

Maintenance:
- Wash cloth daily and dry in sun.
- Replace when torn.

Important:
This only removes large particles; disinfect after using.
""",

    "Filter H — Family Bucket Sand + Charcoal": """AQUASHIELD — Filter H: Family Bucket Sand + Charcoal

Purpose:
Community-scale gravity filter using two buckets. Good for family supply and training.

Materials:
- 2 buckets (one with spigot)
- gravel, sand, charcoal
- cloth or mesh

Build steps:
1. Drill spigot in lower bucket.
2. In upper filter bucket add (top→bottom): cloth, coarse gravel, fine gravel, charcoal, deep sand, cloth.
3. Fill from top; collect filtered water from spigot.

Maintenance:
- Replace charcoal every month.
- Clean spigot and lower bucket weekly.
- Disinfect water for drinking.
"""
}

# --------------------------
# UI: Tabbed layout for 8 filters
# --------------------------
filter_items = [
    ("Filter A — Charcoal + Sand Bottle", FILTER_A_SVG),
    ("Filter B — Bottle-Neck Cartridge", FILTER_B_SVG),
    ("Filter C — Ceramic Cup + Charcoal Pad", FILTER_C_SVG),
    ("Filter D — Layered Sand Clarifier", FILTER_D_SVG),
    ("Filter E — Gravity Carbon Cartridge", FILTER_E_SVG),
    ("Filter F — PVC Mini Pressure Charcoal", FILTER_F_SVG),
    ("Filter G — Cloth-Only Emergency", FILTER_G_SVG),
    ("Filter H — Family Bucket Sand + Charcoal", FILTER_H_SVG),
]

# Use tabs so the UI is compact
tabs = st.tabs([name for name, _ in filter_items])

for tab_obj, (display_title, svg_text) in zip(tabs, filter_items):
    with tab_obj:
        st.subheader(display_title)

        # Show SVG visually via data URL (safe cross-version)
        data_url = svg_to_data_url(svg_text)
        st.image(data_url, width=420)

        # Offer SVG download
        st.download_button(
            label="⬇ Download SVG",
            data=svg_text,
            file_name=f"{display_title.replace(' ', '_')}.svg",
            mime="image/svg+xml"
        )

        # Offer PNG (only if cairosvg available)
        png_bytes = svg_to_png_bytes(svg_text, scale=3)
        if png_bytes:
            st.download_button(
                label="⬇ Download PNG",
                data=png_bytes,
                file_name=f"{display_title.replace(' ', '_')}.png",
                mime="image/png"
            )
        else:
            st.info("PNG export available when 'cairosvg' is installed in the environment. (Optional)")

        # Offer A5 PDF
        pdf_buf = build_a5_pdf_bytes(FILTER_TEXTS[display_title], title=display_title)
        st.download_button(
            label="⬇ Download A5 PDF (instructions)",
            data=pdf_buf,
            file_name=f"{display_title.replace(' ', '_')}_A5.pdf",
            mime="application/pdf"
        )

        # Expandable raw sources
        with st.expander("Show raw SVG code"):
            st.code(svg_text, language="xml")
        with st.expander("Show instruction text"):
            st.text(FILTER_TEXTS[display_title])

# Footer
st.markdown("---")
st.caption("AquaShield — Open-source, low-cost, humanitarian water guidance. These methods improve clarity and taste but are not guaranteed to remove all pathogens or chemicals. Always disinfect water for drinking when possible.")
                    

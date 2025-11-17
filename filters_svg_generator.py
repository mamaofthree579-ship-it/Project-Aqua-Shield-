import streamlit as st
import base64
import io
import zipfile
from fpdf import FPDF
import html

st.set_page_config(page_title="AquaShield — Filters (SVG + PDF + client PNG)", layout="centered")
st.title("🌍 AquaShield — Filter Library (SVG + PDFs + client PNGs)")
st.write("View SVG schematics, download SVG, download A5 PDFs (Short & Full). PNG downloads are generated in your browser (no server binaries).")

# --------------------------
# Utilities
# --------------------------
def sanitize_for_pdf(text: str) -> str:
    """Replace Unicode punctuation that FPDF (latin-1) cannot encode."""
    replacements = {
        "—": "-",
        "–": "-",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "•": "-",  # bullet
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # drop any remaining non-latin-1 chars (safe fallback)
    text = text.encode('latin-1', errors='replace').decode('latin-1')
    return text

def build_a5_pdf_bytes(pdf_text: str, title: str = "AquaShield"):
    """Create A5 PDF bytes (FPDF) from plain ASCII-safe text."""
    safe = sanitize_for_pdf(pdf_text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return buf

def svg_to_data_url(svg_text: str) -> str:
    b = svg_text.encode("utf-8")
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

def build_svg_zip(svg_dict: dict):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for title, svg in svg_dict.items():
            fname = title.replace(" ", "_") + ".svg"
            z.writestr(fname, svg)
    mem.seek(0)
    return mem

def build_pdfs_zip(pdf_bytes_dict: dict):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, b in pdf_bytes_dict.items():
            z.writestr(fname, b.getvalue())
    mem.seek(0)
    return mem

# --------------------------
# SVG schematics (8 filters) - full SVG strings (ASCII-friendly)
# --------------------------
FILTER_SVGS = {
    "Filter A — Charcoal + Sand Bottle": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="330" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="310" height="500" fill="white" stroke="black" stroke-width="2"/>
  <text x="30" y="40" font-size="18">Filter A - Charcoal + Sand Bottle</text>
  <rect x="90" y="80" width="150" height="360" fill="none" stroke="black" stroke-width="2"/>
  <rect x="100" y="110" width="130" height="60" fill="none" stroke="black"/><text x="110" y="140" font-size="12">Crushed Charcoal</text>
  <rect x="100" y="185" width="130" height="120" fill="none" stroke="black"/><text x="110" y="245" font-size="12">Fine Sand</text>
  <rect x="100" y="320" width="130" height="60" fill="none" stroke="black"/><text x="110" y="355" font-size="12">Small Gravel</text>
  <rect x="105" y="395" width="120" height="30" fill="none" stroke="black"/><text x="125" y="415" font-size="11">Cloth Layer</text>
  <path d="M165 70 L165 95" stroke="blue" stroke-width="3"/><path d="M165 430 L165 455" stroke="blue" stroke-width="3"/>
</svg>''',

    "Filter B — Bottle-Neck Cartridge": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="330" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="314" height="504" fill="white" stroke="black" stroke-width="2"/>
  <text x="24" y="36" font-size="18">Filter B - Bottle-Neck Cartridge</text>
  <rect x="95" y="80" width="140" height="320" fill="none" stroke="black" stroke-width="2"/>
  <text x="110" y="110" font-size="12">Outlet cloth</text>
  <rect x="100" y="130" width="120" height="60" fill="none" stroke="black"/><text x="110" y="165" font-size="12">Microfiber</text>
  <rect x="100" y="200" width="120" height="80" fill="none" stroke="black"/><text x="110" y="245" font-size="12">Sand (optional)</text>
  <rect x="100" y="290" width="120" height="80" fill="none" stroke="black"/><text x="110" y="325" font-size="12">Charcoal Layer</text>
  <rect x="100" y="380" width="120" height="40" fill="none" stroke="black"/><text x="110" y="405" font-size="12">Cotton plug</text>
  <path d="M170 60 L170 88" stroke="blue" stroke-width="3"/><path d="M170 420 L170 448" stroke="blue" stroke-width="3"/>
</svg>''',

    "Filter C — Ceramic Cup + Charcoal Pad": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="350" height="450" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="330" height="430" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="40" font-size="18">Filter C - Ceramic Cup + Charcoal Pad</text>
  <ellipse cx="175" cy="120" rx="90" ry="25" fill="none" stroke="black" />
  <rect x="85" y="120" width="180" height="180" fill="none" stroke="black"/>
  <ellipse cx="175" cy="300" rx="90" ry="25" fill="none" stroke="black"/>
  <rect x="100" y="260" width="150" height="25" fill="none" stroke="black"/><text x="115" y="277" font-size="12">Charcoal Pad</text>
  <path d="M175 330 L175 360" stroke="blue" stroke-width="3"/>
</svg>''',

    "Filter D — Layered Sand Clarifier": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="360" height="520" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="340" height="500" fill="white" stroke="black" stroke-width="2"/>
  <text x="40" y="40" font-size="18">Filter D - Layered Sand Clarifier</text>
  <rect x="80" y="70" width="200" height="400" fill="none" stroke="black" stroke-width="2"/>
  <rect x="90" y="100" width="180" height="60" fill="none" stroke="black"/><text x="100" y="135" font-size="12">Coarse Gravel</text>
  <rect x="90" y="175" width="180" height="80" fill="none" stroke="black"/><text x="100" y="215" font-size="12">Medium Sand</text>
  <rect x="90" y="270" width="180" height="120" fill="none" stroke="black"/><text x="100" y="330" font-size="12">Fine Sand</text>
  <rect x="90" y="405" width="180" height="40" fill="none" stroke="black"/><text x="120" y="430" font-size="12">Cloth Pad</text>
</svg>''',

    "Filter E — Gravity Carbon Cartridge": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="350" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="10" width="330" height="460" fill="white" stroke="black" stroke-width="2"/>
  <text x="30" y="40" font-size="18">Filter E - Gravity Carbon Cartridge</text>
  <rect x="90" y="80" width="160" height="300" fill="none" stroke="black" stroke-width="2"/>
  <rect x="100" y="110" width="140" height="240" fill="none" stroke="black"/><text x="115" y="235" font-size="12">Packed Charcoal</text>
  <path d="M170 55 L170 80" stroke="blue" stroke-width="3"/><path d="M170 380 L170 410" stroke="blue" stroke-width="3"/>
</svg>''',

    "Filter F — PVC Mini Pressure Charcoal": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter F - PVC Mini Pressure Charcoal (Tap Add-On)</text>
  <rect x="60" y="90" width="220" height="80" fill="none" stroke="black"/><text x="72" y="132" font-size="12">Cloth -> Charcoal -> Cloth</text>
  <rect x="18" y="110" width="36" height="40" fill="none" stroke="black"/><text x="20" y="138" font-size="11">Inlet</text>
  <rect x="286" y="110" width="36" height="40" fill="none" stroke="black"/><text x="288" y="138" font-size="11">Outlet</text>
</svg>''',

    "Filter G — Cloth-Only Emergency": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter G - Cloth-Only Emergency (Quick)</text>
  <rect x="60" y="80" width="220" height="280" fill="none" stroke="black"/>
  <text x="90" y="120" font-size="12">Fold cloth 4-8 layers</text>
  <text x="90" y="150" font-size="12">Pour slowly through cloth</text>
  <path d="M170 360 L170 400" stroke="blue" stroke-width="3"/>
</svg>''',

    "Filter H — Family Bucket Sand + Charcoal": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="340" height="480" xmlns="http://www.w3.org/2000/svg">
  <rect x="8" y="8" width="324" height="464" fill="white" stroke="black" stroke-width="2"/>
  <text x="20" y="36" font-size="18">Filter H - Family Bucket Sand + Charcoal</text>
  <rect x="60" y="90" width="220" height="300" fill="none" stroke="black"/>
  <text x="80" y="120" font-size="12">Top: Cloth</text>
  <text x="80" y="150" font-size="12">Coarse gravel -> Fine gravel</text>
  <text x="80" y="180" font-size="12">Charcoal layer -> Sand (deep)</text>
  <text x="80" y="210" font-size="12">Bottom cloth & spigot</text>
</svg>'''
}

# --------------------------
# Short + Full instruction texts (ASCII-safe: avoid smart quotes, em-dash, bullets)
# --------------------------
FILTER_TEXTS_SHORT = {
    "Filter A — Charcoal + Sand Bottle": (
        "Filter A - Short\n\n"
        "Make: Cut bottle, tie cloth over mouth, add crushed charcoal, sand, gravel.\n"
        "Use: Pour slowly. Discard first liter. Disinfect water before drinking.\n"
    ),
    "Filter B — Bottle-Neck Cartridge": (
        "Filter B - Short\n\n"
        "Make: Pack bottle neck with microfiber, optional sand, charcoal, microfiber.\n"
        "Use: Pour slowly. Discard first 1-2 L. Change media every 2-6 weeks.\n"
    ),
    "Filter C — Ceramic Cup + Charcoal Pad": (
        "Filter C - Short\n\n"
        "Make: Place charcoal pad in porous ceramic cup. Set over clean container.\n"
        "Use: Pour water and let drip. Replace charcoal 1-2 weeks. Disinfect before drinking.\n"
    ),
    "Filter D — Layered Sand Clarifier": (
        "Filter D - Short\n\n"
        "Make: Cloth at bottom, coarse gravel, medium sand, fine sand on top.\n"
        "Use: Pour slowly; collect clearer water. Replace sand when fouled. Disinfect before drinking.\n"
    ),
    "Filter E — Gravity Carbon Cartridge": (
        "Filter E - Short\n\n"
        "Make: Pack washed charcoal in cartridge; cloth top and bottom.\n"
        "Use: Pour; collect filtered water. Replace charcoal every 2-4 weeks. Disinfect before drinking.\n"
    ),
    "Filter F — PVC Mini Pressure Charcoal": (
        "Filter F - Short\n\n"
        "Make: Short tube: cloth, charcoal, cloth. Attach inline to tap or hose.\n"
        "Use: Discard first 1-2 L. Change charcoal 2-6 weeks. Disinfect before drinking.\n"
    ),
    "Filter G — Cloth-Only Emergency": (
        "Filter G - Short\n\n"
        "Make: Fold clean cloth 4-8 layers.\n"
        "Use: Pour water through cloth 1-2 times. Disinfect after.\n"
    ),
    "Filter H — Family Bucket Sand + Charcoal": (
        "Filter H - Short\n\n"
        "Make: Two-bucket filter: top cloth, coarse gravel, fine gravel, charcoal, sand, cloth, spigot.\n"
        "Use: Fill top; collect from spigot. Replace charcoal monthly. Disinfect before drinking.\n"
    )
}

FILTER_TEXTS_FULL = {
    "Filter A — Charcoal + Sand Bottle": (
        "AQUASHIELD - Filter A (Full)\n\n"
        "Purpose:\n"
        "A low-cost gravity bottle filter to improve clarity and taste. This filter does NOT disinfect water.\n\n"
        "Materials:\n"
        "- 1 plastic bottle (1-2 L)\n"
        "- clean cloth\n"
        "- crushed wood charcoal (washed)\n"
        "- fine sand\n"
        "- small gravel\n\n"
        "Build steps:\n"
        "1. Cut the bottom off the bottle and clean all parts.\n"
        "2. Tie cloth over the mouth of the bottle to hold filter media.\n"
        "3. Add layers (from top down): crushed charcoal, fine sand, small gravel.\n"
        "4. Place the bottle inverted over a clean container.\n\n"
        "Use and maintenance:\n"
        "- Discard the first liter after assembly to remove dust.\n"
        "- Replace charcoal every 2-4 weeks depending on turbidity.\n"
        "- Rinse the cloth weekly and replace when worn.\n"
        "- Always apply an approved disinfection step (boiling, SODIS, or chlorine) before drinking.\n"
    ),

    "Filter B — Bottle-Neck Cartridge": (
        "AQUASHIELD - Filter B (Full)\n\n"
        "Purpose:\n"
        "A reusable cartridge using a bottle neck to filter sediment and improve taste.\n\n"
        "Materials:\n"
        "- bottle neck section\n"
        "- microfiber cloth pieces\n"
        "- crushed charcoal\n"
        "- optional clean sand\n\n"
        "Build steps:\n"
        "1. Place a cotton plug at the narrow end to hold media.\n"
        "2. Add layers: microfiber, optional sand, microfiber, crushed charcoal, microfiber.\n"
        "3. Secure the cartridge and use in a funnel or bottle.\n\n"
        "Use and maintenance:\n"
        "- Discard the first 1-2 liters after assembly.\n"
        "- Replace media every 2-6 weeks.\n"
        "- Rinse external cloth daily and dry in sun.\n"
    ),

    "Filter C — Ceramic Cup + Charcoal Pad": (
        "AQUASHIELD - Filter C (Full)\n\n"
        "Purpose:\n"
        "Use a porous ceramic cup with a charcoal pad to reduce turbidity and improve taste.\n\n"
        "Materials:\n"
        "- porous ceramic cup or locally made ceramic element\n"
        "- cloth-wrapped charcoal pad\n"
        "- clean collection container\n\n"
        "Build steps:\n"
        "1. Place charcoal pad at bottom inside ceramic cup.\n"
        "2. Set the cup over a clean container and pour water in.\n"
        "3. Let water slowly drip through the ceramic.\n\n"
        "Use and maintenance:\n"
        "- Replace charcoal every 1-2 weeks.\n"
        "- Rinse the exterior of the ceramic; do not scrub pores.\n"
        "- Disinfect water after filtration when using for drinking.\n"
    ),

    "Filter D — Layered Sand Clarifier": (
        "AQUASHIELD - Filter D (Full)\n\n"
        "Purpose:\n"
        "A layered sand column that traps particles by size. Improves clarity but does not sterilize.\n\n"
        "Materials:\n"
        "- tall container or bottle\n"
        "- cloth\n"
        "- fine, medium sand\n"
        "- coarse gravel\n\n"
        "Build steps:\n"
        "1. Place cloth at the bottom to hold sand.\n"
        "2. Add bottom coarse gravel, then medium sand, then fine sand on top.\n"
        "3. Pour water slowly on top and collect clearer water at the bottom.\n\n"
        "Use and maintenance:\n"
        "- Rinse or replace top sand when clogged.\n"
        "- Replace sand when visibly fouled.\n"
        "- Disinfect before drinking.\n"
    ),

    "Filter E — Gravity Carbon Cartridge": (
        "AQUASHIELD - Filter E (Full)\n\n"
        "Purpose:\n"
        "A packed charcoal cartridge to improve taste and remove odors and some organics.\n\n"
        "Materials:\n"
        "- cartridge body or straight bottle\n"
        "- washed charcoal\n"
        "- cloth for top and bottom\n\n"
        "Build steps:\n"
        "1. Seal the bottom with cloth to hold media.\n"
        "2. Pack washed charcoal into the cartridge.\n"
        "3. Cover top with cloth and place over a clean container.\n\n"
        "Use and maintenance:\n"
        "- Replace charcoal every 2-4 weeks.\n"
        "- Rinse cloths and replace when dirty.\n"
        "- Disinfect before drinking.\n"
    ),

    "Filter F — PVC Mini Pressure Charcoal": (
        "AQUASHIELD - Filter F (Full)\n\n"
        "Purpose:\n"
        "A short inline tube for taps and hoses that reduces turbidity and improves taste.\n\n"
        "Materials:\n"
        "- short PVC tube (20-50 mm)\n"
        "- cloth pads\n"
        "- activated charcoal\n"
        "- two end caps\n\n"
        "Build steps:\n"
        "1. Insert cloth pad into inlet cap.\n"
        "2. Fill with activated charcoal and pack lightly.\n"
        "3. Add cloth pad and secure outlet cap.\n\n"
        "Use and maintenance:\n"
        "- Replace charcoal every 2-6 weeks.\n"
        "- Clean caps and pads weekly.\n"
        "- Disinfect water before drinking.\n"
    ),

    "Filter G — Cloth-Only Emergency": (
        "AQUASHIELD - Filter G (Full)\n\n"
        "Purpose:\n"
        "A minimal method using cloth to remove large particles and debris.\n\n"
        "Materials:\n"
        "- clean cotton cloth (t-shirt or scarf)\n"
        "- clean container\n\n"
        "Build steps:\n"
        "1. Fold cloth 4-8 layers and secure over container or use as funnel.\n"
        "2. Pour water slowly through cloth. Repeat if needed.\n\n"
        "Use and maintenance:\n"
        "- Wash and sun-dry cloth daily.\n"
        "- Replace when torn.\n"
        "- Always disinfect after using.\n"
    ),

    "Filter H — Family Bucket Sand + Charcoal": (
        "AQUASHIELD - Filter H (Full)\n\n"
        "Purpose:\n"
        "A two-bucket family-scale gravity filter using sand, gravel and charcoal.\n\n"
        "Materials:\n"
        "- two buckets (one with spigot)\n"
        "- cloth or mesh\n"
        "- gravel, sand, charcoal\n\n"
        "Build steps:\n"
        "1. Install spigot in lower bucket.\n"
        "2. In upper bucket add layers (top to bottom): cloth, coarse gravel, fine gravel, charcoal, deep sand, cloth.\n"
        "3. Fill top bucket and collect from spigot.\n\n"
        "Use and maintenance:\n"
        "- Replace charcoal monthly.\n"
        "- Clean spigot weekly.\n"
        "- Disinfect water for drinking.\n"
    )
}

# --------------------------
# UI: download full set of SVGs as ZIP
# --------------------------
st.markdown("### Download all schematics")
svg_zip = build_svg_zip(FILTER_SVGS)
st.download_button("⬇ Download all SVGs (ZIP)", data=svg_zip, file_name="AquaShield_Schematics_8_SVG.zip", mime="application/zip")
st.markdown("---")

# --------------------------
# Tabs for each filter
# --------------------------
tabs = st.tabs(list(FILTER_SVGS.keys()))

# We will also prepare a dictionary of PDFs to allow a "download all PDFs" ZIP later if desired
pdfs_short = {}
pdfs_full = {}

for tab_obj, (title, svg_text) in zip(tabs, FILTER_SVGS.items()):
    with tab_obj:
        st.subheader(title)

        # Show SVG visually: use data URL
        data_url = svg_to_data_url(svg_text)
        st.image(data_url, width=480)

        # Download SVG
        st.download_button("⬇ Download SVG", data=svg_text, file_name=f"{title.replace(' ', '_')}.svg", mime="image/svg+xml")

        # Client-side PNG generator: embed HTML+JS that creates a PNG from the SVG and triggers a download
        # We use base64 SVG data URL and a canvas; this runs in the user's browser (no server binaries)
        safe_svg_b64 = base64.b64encode(svg_text.encode('utf-8')).decode('ascii')
        html_code = f"""
        <div>
          <p><small>Click to generate a PNG of this SVG in your browser (works offline in the browser).</small></p>
          <button id="btn_{html.escape(title)}">Download PNG</button>
        </div>
        <script>
        const svgB64 = "data:image/svg+xml;base64,{safe_svg_b64}";
        document.getElementById("btn_{html.escape(title)}").addEventListener("click", function(){{
            var img = new Image();
            img.onload = function() {{
                var canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                var ctx = canvas.getContext('2d');
                // white background
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(0,0,canvas.width,canvas.height);
                ctx.drawImage(img, 0, 0);
                canvas.toBlob(function(blob) {{
                    var url = URL.createObjectURL(blob);
                    var a = document.createElement('a');
                    a.href = url;
                    a.download = "{html.escape(title)}.png";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);
                }}, "image/png");
            }};
            // set crossOrigin to avoid tainting - not always necessary for data URL
            img.crossOrigin = "anonymous";
            img.src = svgB64;
        }});
        </script>
        """
        st.components.v1.html(html_code, height=100)

        # PDF downloads: short + full
        short_text = FILTER_TEXTS_SHORT[title]
        full_text = FILTER_TEXTS_FULL[title]
        short_pdf_buf = build_a5_pdf_bytes(short_text, title=title + " - Short")
        full_pdf_buf = build_a5_pdf_bytes(full_text, title=title + " - Full")
        pdfs_short[f"{title.replace(' ', '_')}_short.pdf"] = short_pdf_buf
        pdfs_full[f"{title.replace(' ', '_')}_full.pdf"] = full_pdf_buf

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇ Download A5 PDF (Short)", data=short_pdf_buf, file_name=f"{title.replace(' ', '_')}_short_A5.pdf", mime="application/pdf")
        with c2:
            st.download_button("⬇ Download A5 PDF (Full)", data=full_pdf_buf, file_name=f"{title.replace(' ', '_')}_full_A5.pdf", mime="application/pdf")

        # Expanders for raw SVG and full text
        with st.expander("Show raw SVG code"):
            st.code(svg_text, language="xml")
        with st.expander("Show instruction text (Full)"):
            st.text(full_text)
        with st.expander("Show instruction text (Short)"):
            st.text(short_text)

# Option: Download all PDFs as ZIP (Short or Full)
st.markdown("---")
all_pdfs_short_zip = build_pdfs_zip(pdfs_short)
all_pdfs_full_zip = build_pdfs_zip(pdfs_full)
st.download_button("⬇ Download ALL Short PDFs (ZIP)", data=all_pdfs_short_zip, file_name="AquaShield_Short_PDFs.zip", mime="application/zip")
st.download_button("⬇ Download ALL Full PDFs (ZIP)", data=all_pdfs_full_zip, file_name="AquaShield_Full_PDFs.zip", mime="application/zip")

st.markdown("---")
st.caption("AquaShield — open-source, low-cost water guidance. These filters improve clarity and taste but are not guaranteed to remove all pathogens or chemicals. Always disinfect water for drinking when possible.")

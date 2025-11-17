import streamlit as st
from fpdf import FPDF
import io
import base64
import zipfile
import html

st.set_page_config(page_title="Project AquaShield — Filters A–H", layout="wide")
st.title("🌍 Project AquaShield — Filter Library (A–H)")
st.write("Tabbed reading view: Schematic | Short instructions | Full instructions. Client-side PNG generation (in-browser).")

# ---------------------------
# Utilities
# ---------------------------
def sanitize_for_pdf(text: str) -> str:
    """Replace problematic Unicode punctuation with ASCII equivalents."""
    replacements = {
        "—": "-",
        "–": "-",
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "…": "...",
        "•": "-",  # bullet
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # final fallback: replace any non-latin-1 chars with '?'
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text

def build_a5_pdf_bytes(pdf_text: str):
    """Return a BytesIO containing an A5 PDF built with FPDF (latin-1)."""
    safe = sanitize_for_pdf(pdf_text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    # get bytes correctly
    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    buf = io.BytesIO(pdf_bytes)
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

def build_pdfs_zip(pdf_bytesio_dict: dict):
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, b in pdf_bytesio_dict.items():
            z.writestr(fname, b.getvalue())
    mem.seek(0)
    return mem

# ---------------------------
# Normalized filter keys (ASCII hyphen)
# ---------------------------
FILTER_KEYS = [
    "Filter A - Basic Bottle Microfilter",
    "Filter B - Bottle-Neck Cartridge Filter",
    "Filter C - Gravity Bucket Filter",
    "Filter D - Family Bucket Filter",
    "Filter E - Clay-Sawdust Ceramic Filter",
    "Filter F - Cloth Emergency Filter",
    "Filter G - SODIS Solar Disinfection",
    "Filter H - Crisis-Zone 3-Tier Method",
]

# ---------------------------
# SVG schematics (simple, ASCII-friendly)
# ---------------------------
FILTER_SVGS = {
    "Filter A - Basic Bottle Microfilter": r'''<?xml version="1.0" encoding="UTF-8"?>
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
</svg>''',

    "Filter B - Bottle-Neck Cartridge Filter": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="420" height="760" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter B - Bottle-Neck Cartridge Filter</text>
 <rect x="160" y="100" width="100" height="420" fill="none" stroke="black" stroke-width="2"/>
 <text x="40" y="140">Microfiber / Cloth</text>
 <line x1="160" y1="180" x2="260" y2="180" stroke="black"/>
 <text x="40" y="220">Optional Sand</text>
 <line x1="160" y1="260" x2="260" y2="260" stroke="black"/>
 <text x="40" y="300">Charcoal Layer</text>
 <line x1="160" y1="340" x2="260" y2="340" stroke="black"/>
 <text x="40" y="380">Outlet plug</text>
</svg>''',

    "Filter C - Gravity Bucket Filter": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="480" height="640" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter C - Gravity Bucket Filter</text>
 <rect x="120" y="60" width="240" height="420" stroke="black" fill="none" stroke-width="2"/>
 <text x="40" y="120">Top: Cloth / Diffuser</text>
 <line x1="120" y1="140" x2="360" y2="140" stroke="black"/>
 <text x="40" y="190">Coarse Gravel</text>
 <line x1="120" y1="220" x2="360" y2="220" stroke="black"/>
 <text x="40" y="260">Medium Gravel</text>
 <line x1="120" y1="300" x2="360" y2="300" stroke="black"/>
 <text x="40" y="340">Charcoal Layer</text>
 <line x1="120" y1="380" x2="360" y2="380" stroke="black"/>
 <text x="40" y="420">Sand (deep)</text>
</svg>''',

    "Filter D - Family Bucket Filter": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="480" height="680" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="20">Filter D - Family Bucket Filter</text>
 <rect x="100" y="70" width="260" height="480" stroke="black" fill="none" stroke-width="2"/>
 <text x="120" y="120">Top cloth</text>
 <line x1="100" y1="150" x2="360" y2="150" stroke="black"/>
 <text x="120" y="190">Coarse gravel</text>
 <line x1="100" y1="230" x2="360" y2="230" stroke="black"/>
 <text x="120" y="270">Fine gravel</text>
 <line x1="100" y1="310" x2="360" y2="310" stroke="black"/>
 <text x="120" y="350">Charcoal</text>
 <line x1="100" y1="390" x2="360" y2="390" stroke="black"/>
 <text x="120" y="430">Deep sand</text>
 <line x1="100" y1="470" x2="360" y2="470" stroke="black"/>
 <text x="120" y="520">Bottom cloth & spigot</text>
</svg>''',

    "Filter E - Clay-Sawdust Ceramic Filter": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="420" height="520" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="18">Filter E - Clay-Sawdust Ceramic Filter</text>
 <ellipse cx="210" cy="140" rx="140" ry="40" fill="none" stroke="black"/>
 <rect x="70" y="140" width="280" height="200" fill="none" stroke="black"/>
 <ellipse cx="210" cy="340" rx="140" ry="30" fill="none" stroke="black"/>
 <text x="30" y="180">Porous ceramic pot (locally fired)</text>
 <text x="30" y="200">Optional colloidal silver coating (if available)</text>
 <text x="30" y="240">Charcoal pad at bottom (optional)</text>
</svg>''',

    "Filter F - Cloth Emergency Filter": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="420" height="420" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="18">Filter F - Cloth Emergency Filter</text>
 <rect x="60" y="70" width="300" height="260" fill="none" stroke="black"/>
 <text x="80" y="120">Fold cloth 4-8 layers</text>
 <text x="80" y="160">Secure over clean container</text>
 <text x="80" y="200">Pour slowly; repeat if turbid</text>
</svg>''',

    "Filter G - SODIS Solar Disinfection": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="480" height="300" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="18">Filter G - SODIS Solar Disinfection</text>
 <rect x="40" y="60" width="160" height="120" fill="none" stroke="black"/><text x="50" y="140">Clear PET bottle</text>
 <rect x="260" y="60" width="160" height="120" fill="none" stroke="black"/><text x="270" y="140">Sunny surface (metal/rock)</text>
 <text x="50" y="200">Expose full sun 6 hours (clear) or 2 days partial</text>
</svg>''',

    "Filter H - Crisis-Zone 3-Tier Method": r'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="520" height="420" xmlns="http://www.w3.org/2000/svg">
 <text x="20" y="30" font-size="18">Filter H - Crisis-Zone 3-Tier Method</text>
 <rect x="40" y="60" width="420" height="300" fill="none" stroke="black"/>
 <text x="60" y="110">Tier 1: Settling + Cloth</text>
 <text x="60" y="150">Tier 2: Charcoal + Sand microfilter</text>
 <text x="60" y="190">Tier 3: Disinfection (SODIS/boil/chlorine)</text>
</svg>'''
}

# ---------------------------
# Instruction texts (short + full) ASCII-clean
# ---------------------------
FILTER_TEXTS_SHORT = {
    "Filter A - Basic Bottle Microfilter":
        "Filter A - Short\n\nMake: Cut bottle, tie cloth over mouth, add crushed charcoal, sand, gravel.\nUse: Pour slowly. Discard first liter. Disinfect water before drinking.\n",
    "Filter B - Bottle-Neck Cartridge Filter":
        "Filter B - Short\n\nMake: Pack neck with microfiber, optional sand and charcoal. Use as cartridge.\nUse: Pour slowly. Discard first 1-2 L. Replace media based on turbidity.\n",
    "Filter C - Gravity Bucket Filter":
        "Filter C - Short\n\nMake: Stack layers in bucket: cloth, gravel, charcoal, sand.\nUse: Fill top, collect from bottom. Disinfect before drinking.\n",
    "Filter D - Family Bucket Filter":
        "Filter D - Short\n\nMake: Two-bucket system with spigot. Top filter contains gravel, charcoal, sand.\nUse: Replace charcoal monthly. Disinfect before drinking.\n",
    "Filter E - Clay-Sawdust Ceramic Filter":
        "Filter E - Short\n\nMake: Locally fire clay+sawdust pot. Use as porous cup; optional silver coat.\nUse: Pour and collect; disinfect after if drinking.\n",
    "Filter F - Cloth Emergency Filter":
        "Filter F - Short\n\nMake: Fold clean cloth 4-8 layers.\nUse: Pour slowly, repeat if turbid, then disinfect.\n",
    "Filter G - SODIS Solar Disinfection":
        "Filter G - Short\n\nMake water clear (cloth), fill PET bottle, expose full sun 6 hours (clear) or 2 days partial.\nUse: Suitable for bactericidal and viral reduction in clear water. Disinfected water is for drinking.\n",
    "Filter H - Crisis-Zone 3-Tier Method":
        "Filter H - Short\n\nTier 1: Settling + cloth. Tier 2: Charcoal+sand microfilter. Tier 3: Disinfection (SODIS/boil/chlorine).\nUse: Follow the 3 tiers for best household safety in crisis.\n"
}

FILTER_TEXTS_FULL = {
    "Filter A - Basic Bottle Microfilter":
        "AQUASHIELD - Filter A (Full)\n\nPurpose:\nA low-cost gravity bottle filter to improve clarity and taste. This filter does NOT disinfect water.\n\nMaterials:\n- 1 plastic bottle (1-2 L)\n- clean cloth\n- crushed wood charcoal (washed)\n- fine sand\n- small gravel\n- rubber band or string\n\nBuild steps:\n1. Cut the bottle bottom off and clean all parts.\n2. Tie cloth over mouth of bottle to hold media.\n3. Add layers from top down: crushed charcoal, fine sand, small gravel.\n4. Place bottle inverted over a clean container.\n\nUse & maintenance:\n- Discard the first liter after assembly to remove dust.\n- Replace charcoal every 2-4 weeks depending on turbidity.\n- Rinse cloth weekly and replace when worn.\n- Always apply an approved disinfection step before drinking (boil, SODIS, or chlorine).\n",

    "Filter B - Bottle-Neck Cartridge Filter":
        "AQUASHIELD - Filter B (Full)\n\nPurpose:\nA small cartridge using a bottle neck to remove sediment and improve taste.\n\nMaterials:\n- bottle neck section\n- microfiber cloth pieces\n- crushed charcoal\n- optional clean sand\n- cotton plug\n\nBuild steps:\n1. Place a cotton plug at the narrow end to hold media.\n2. Add layers: microfiber, optional sand, microfiber, crushed charcoal, microfiber.\n3. Secure the cartridge and use in a funnel or bottle.\n\nUse & maintenance:\n- Discard first 1-2 liters after assembly.\n- Replace media every 2-6 weeks depending on turbidity.\n- Rinse external cloth daily and dry in sun.\n",

    "Filter C - Gravity Bucket Filter":
        "AQUASHIELD - Filter C (Full)\n\nPurpose:\nCommunity-scale gravity bucket filter improving clarity and taste.\n\nMaterials:\n- bucket with lid\n- cloth or diffuser plate\n- coarse gravel\n- small gravel\n- charcoal\n- clean sand\n\nBuild steps:\n1. Place diffuser cloth at top to avoid channeling.\n2. Add layers: coarse gravel, small gravel, charcoal layer, deep sand.\n3. Fit spigot or allow slow drip into collection container.\n\nUse & maintenance:\n- Discard first run to flush dust.\n- Replace charcoal monthly.\n- Rinse top sand when clogged; replace if fouled.\n- Disinfect water for drinking.\n",

    "Filter D - Family Bucket Filter":
        "AQUASHIELD - Filter D (Full)\n\nPurpose:\nFamily-scale two-bucket gravity system for household supply.\n\nMaterials:\n- two buckets (one with spigot)\n- cloth or mesh\n- gravel, sand, charcoal\n\nBuild steps:\n1. Drill spigot in lower bucket.\n2. In upper bucket add (top->bottom): cloth, coarse gravel, fine gravel, charcoal, deep sand, cloth.\n3. Place upper bucket over lower bucket and fill with source water.\n\nUse & maintenance:\n- Replace charcoal monthly.\n- Clean spigot weekly.\n- Disinfect drinking water after filtration.\n",

    "Filter E - Clay-Sawdust Ceramic Filter":
        "AQUASHIELD - Filter E (Full)\n\nPurpose:\nLocally fired porous ceramic pot made with clay+sawdust; pores allow water passage and trap particulates.\n\nMaterials:\n- clean clay\n- fine sawdust or rice hulls\n- simple mold or pot shape\n- access to firing method (community kiln, barrel kiln)\n\nBuild steps:\n1. Mix 3 parts clay with 1 part sawdust; add water to workable consistency.\n2. Shape into a pot/bowl with walls ~1-2 cm thick.\n3. Dry in shade 2-3 days, then fire to recommended temperature (local kiln guidance).\n4. Optionally coat interior with colloidal silver if available.\n\nUse & maintenance:\n- Pour water in the top; collect drip below.\n- Clean exterior; do not scrub pores.\n- Replace if cracked. Pair with disinfection for drinking.\n",

    "Filter F - Cloth Emergency Filter":
        "AQUASHIELD - Filter F (Full)\n\nPurpose:\nAn emergency method using layered cloth to remove large particles; always disinfect after use.\n\nMaterials:\n- clean cotton cloth (t-shirt, scarf)\n- clean container\n\nBuild steps:\n1. Fold cloth multiple times to create 4-8 layers.\n2. Secure cloth over container or use as a funnel and pour slowly.\n3. Repeat filtration if very turbid.\n\nUse & maintenance:\n- Wash cloth daily and sun-dry.\n- Replace when torn.\n- Disinfect water before drinking.\n",

    "Filter G - SODIS Solar Disinfection":
        "AQUASHIELD - Filter G (Full)\n\nPurpose:\nSolar disinfection (SODIS) in clear PET bottles for bactericidal/viral reduction in clear water.\n\nMaterials:\n- clear PET bottles (1-2 L)\n- clean surface with strong sun or reflective surface\n\nBuild steps:\n1. Pre-filter water with cloth until visually clear.\n2. Fill bottles, shake 20 seconds, close caps.\n3. Lay bottles on metal roof, rock, or reflective surface in full sun for at least 6 hours (clear) or 2 days (partial sun).\n\nUse & maintenance:\n- Works best with clear water.\n- Does not remove chemicals or heavy metals.\n- Store disinfected water covered.\n",

    "Filter H - Crisis-Zone 3-Tier Method":
        "AQUASHIELD - Filter H (Full)\n\nPurpose:\nA practical 3-tier approach for crisis zones: settling+cloth, charcoal+sand microfilter, and disinfection.\n\nMaterials:\n- buckets or containers\n- cloth, sand, charcoal\n- PET bottles for SODIS or means to boil\n\nBuild steps:\n1. Tier 1: Collect and let water settle 6-12 hours; pour upper water through folded cloth.\n2. Tier 2: Pour through a charcoal+sand microfilter slowly.\n3. Tier 3: Disinfect by SODIS, boiling, or chlorine before drinking.\n\nUse & maintenance:\n- If water smells like fuel/solvent, do not use these methods.\n- Heavy metals require advanced treatment.\n- Train community on steps and watch for cross-contamination.\n"
}

# ---------------------------
# Build ZIPs of all SVGs and all PDFs (Short + Full)
# ---------------------------
# Build SVG ZIP now
svg_zip_io = io.BytesIO()
with zipfile.ZipFile(svg_zip_io, "w", zipfile.ZIP_DEFLATED) as z:
    for k, v in FILTER_SVGS.items():
        z.writestr(f"{k.replace(' ', '_')}.svg", v)
svg_zip_io.seek(0)

# We'll build PDF ZIPs on-demand after generating each PDF bytes object

# ---------------------------
# App layout: select filter (or show tabs for all)
# ---------------------------
st.sidebar.markdown("## Download bundles")
st.sidebar.download_button("⬇ Download all SVGs (ZIP)", data=svg_zip_io.getvalue(), file_name="AquaShield_All_SVGs.zip", mime="application/zip")

st.sidebar.markdown(" ")
st.sidebar.markdown("Help / Notes")
st.sidebar.info("PNG downloads are generated in your browser (click 'Download PNG' on schematic tab). PDFs are A5 and ASCII-sanitized for compatibility.")

st.markdown("---")

# Main: create tabs for each filter (R2: Tab layout for schematic / short / full)
for key in FILTER_KEYS:
    st.header(key)
    tab1, tab2, tab3 = st.tabs(["Schematic", "Short Instructions", "Full Instructions"])

    # Schematic tab
    with tab1:
        st.subheader("Schematic")
        svg_code = FILTER_SVGS.get(key, "<svg></svg>")
        # Display SVG as data URL image
        st.image(svg_to_data_url(svg_code), width=520)

        # Download SVG button
        st.download_button("⬇ Download SVG", data=svg_code, file_name=f"{key.replace(' ', '_')}.svg", mime="image/svg+xml")

        # Client-side PNG generator (in-browser). Use base64 embed and JS to draw to canvas and download.
        safe_svg_b64 = base64.b64encode(svg_code.encode("utf-8")).decode("ascii")
        escaped_id = html.escape(key).replace(" ", "_")
        html_code = f"""
        <div>
          <p style="margin:0 0 6px 0;"><small>Generate PNG in your browser (no server binaries required).</small></p>
          <button id="btn_{escaped_id}">Download PNG</button>
        </div>
        <script>
        (function(){{
            const svgB64 = "data:image/svg+xml;base64,{safe_svg_b64}";
            const btn = document.getElementById("btn_{escaped_id}");
            btn.addEventListener("click", function(){{
                var img = new Image();
                img.onload = function() {{
                    var canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth || 800;
                    canvas.height = img.naturalHeight || 600;
                    var ctx = canvas.getContext('2d');
                    ctx.fillStyle = "#ffffff";
                    ctx.fillRect(0,0,canvas.width,canvas.height);
                    ctx.drawImage(img, 0, 0);
                    canvas.toBlob(function(blob) {{
                        var url = URL.createObjectURL(blob);
                        var a = document.createElement('a');
                        a.href = url;
                        a.download = "{escaped_id}.png";
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        URL.revokeObjectURL(url);
                    }}, "image/png");
                }};
                img.crossOrigin = "anonymous";
                img.src = svgB64;
            }});
        }})();
        </script>
        """
        # Render the HTML for client-side PNG generation
        st.components.v1.html(html_code, height=90)

    # Short instructions tab
    with tab2:
        st.subheader("Short Instructions")
        short_text = FILTER_TEXTS_SHORT.get(key, "Short instructions not available.")
        st.markdown("```text\n" + short_text + "\n```")
        # Build short PDF and offer download
        short_pdf_buf = build_a5_pdf_bytes(short_text)
        st.download_button("⬇ Download Short PDF (A5)", data=short_pdf_buf.getvalue(), file_name=f"{key.replace(' ', '_')}_SHORT_A5.pdf", mime="application/pdf")

    # Full instructions tab
    with tab3:
        st.subheader("Full Instructions")
        full_text = FILTER_TEXTS_FULL.get(key, "Full instructions not available.")
        st.markdown("```text\n" + full_text + "\n```")
        # Build full PDF and offer download
        full_pdf_buf = build_a5_pdf_bytes(full_text)
        st.download_button("⬇ Download Full PDF (A5)", data=full_pdf_buf.getvalue(), file_name=f"{key.replace(' ', '_')}_FULL_A5.pdf", mime="application/pdf")

    st.markdown("---")

# After loop: offer ZIP downloads of all PDFs (generate now)
# Rebuild pdf dicts
pdfs_short = {}
pdfs_full = {}
for key in FILTER_KEYS:
    s = FILTER_TEXTS_SHORT.get(key, "")
    f = FILTER_TEXTS_FULL.get(key, "")
    s_buf = build_a5_pdf_bytes(s)
    f_buf = build_a5_pdf_bytes(f)
    pdfs_short[f"{key.replace(' ', '_')}_SHORT.pdf"] = s_buf
    pdfs_full[f"{key.replace(' ', '_')}_FULL.pdf"] = f_buf

short_zip_io = build_pdfs_zip(pdfs_short)
full_zip_io  = build_pdfs_zip(pdfs_full)

st.sidebar.download_button("⬇ Download ALL Short PDFs (ZIP)", data=short_zip_io.getvalue(), file_name="AquaShield_Short_PDFs.zip", mime="application/zip")
st.sidebar.download_button("⬇ Download ALL Full PDFs (ZIP)", data=full_zip_io.getvalue(), file_name="AquaShield_Full_PDFs.zip", mime="application/zip")

st.markdown("---")
st.caption("AquaShield — open-source, low-cost, humanitarian water guidance. These methods improve clarity and taste but are NOT guaranteed to remove all pathogens or chemicals. Always disinfect water for drinking when possible.")

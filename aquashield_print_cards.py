import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import zipfile
import tempfile
import os
import html

st.set_page_config(page_title="AquaShield — Print-ready A5 Cards", layout="wide")
st.title("AquaShield — Print-ready A5 Cards (Text-only + Image cards)")

# -------------------------
# Utilities
# -------------------------
def sanitize_for_pdf(text: str) -> str:
    """Sanitize text to Latin-1 friendly characters to avoid FPDF crashes."""
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
    # fallback: replace any non-latin1 chars with '?'
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text

def build_a5_pdf_text_only(text: str):
    """Return BytesIO with A5 PDF (text only)."""
    safe = sanitize_for_pdf(text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    output = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(output)

def build_a5_pdf_with_image(text: str, png_bytes: bytes):
    """
    Return BytesIO with A5 PDF that places a PNG at the top and text below.
    png_bytes: raw PNG bytes
    """
    safe = sanitize_for_pdf(text)
    # Write png_bytes to a temp file because fpdf.image() needs a filename
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpimg:
        tmpimg.write(png_bytes)
        tmpimg.flush()
        img_path = tmpimg.name

    try:
        pdf = FPDF(format='A5')
        pdf.add_page()
        # Place image at top with margins
        margin = 10  # mm
        page_w = pdf.w - 2 * margin  # printable width in mm
        # Insert image width = page_w (fpdf will scale height proportionally)
        pdf.image(img_path, x=margin, y=margin, w=page_w)
        # Move below image
        # Estimate image height in mm: FPDF calculates internally but we can add spacing
        # Add a spacer
        pdf.ln(5)
        pdf.set_font("Arial", size=11)
        pdf.set_left_margin(margin)
        pdf.set_right_margin(margin)
        pdf.multi_cell(0, 6, safe)
        output = pdf.output(dest="S").encode("latin-1")
        return io.BytesIO(output)
    finally:
        # Cleanup temp file
        try:
            os.remove(img_path)
        except Exception:
            pass

def create_schematic_png(filter_key: str, size=(800, 600)) -> bytes:
    """
    Programmatically draw a PNG schematic for the given filter_key using Pillow.
    Returns PNG bytes.
    """
    w, h = size
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    # Basic header text
    draw.text((20, 12), filter_key, fill="black", font=font)

    # Simple diagrams per filter_key
    # We'll draw simple shapes that mirror the SVG line-art used earlier
    if "Basic Bottle" in filter_key:
        # vertical bottle
        left = w//2 - 60
        top = 60
        right = w//2 + 60
        bottom = h - 120
        draw.rectangle([left, top, right, bottom], outline="black", width=2)
        # layers
        y1 = top + 80
        y2 = y1 + 80
        y3 = y2 + 80
        draw.line([left, y1, right, y1], fill="black")
        draw.text((20, y1-10), "Charcoal layer", fill="black", font=font)
        draw.line([left, y2, right, y2], fill="black")
        draw.text((20, y2-10), "Sand layer", fill="black", font=font)
        draw.line([left, y3, right, y3], fill="black")
        draw.text((20, y3-10), "Gravel layer", fill="black", font=font)

    elif "Bottle-Neck" in filter_key:
        # cartridge rectangle and labels
        cx = w//2
        draw.rectangle([cx-40, 100, cx+40, 480], outline="black", width=2)
        draw.text((20, 130), "Microfiber / Cloth", fill="black", font=font)
        draw.line([cx-40, 180, cx+40, 180], fill="black")
        draw.text((20, 210), "Optional sand", fill="black", font=font)
        draw.line([cx-40, 260, cx+40, 260], fill="black")
        draw.text((20, 290), "Charcoal", fill="black", font=font)

    elif "Gravity Bucket" in filter_key or "Family Bucket" in filter_key:
        left = 100
        right = w - 100
        top = 80
        bottom = h - 120
        draw.rectangle([left, top, right, bottom], outline="black", width=2)
        # draw layered lines
        step = (bottom - top) // 6
        labels = ["Cloth/diffuser", "Coarse gravel", "Medium gravel", "Charcoal", "Deep sand"]
        for i, lab in enumerate(labels):
            y = top + (i+1)*step
            draw.line([left, y, right, y], fill="black")
            draw.text((20, y-10), lab, fill="black", font=font)

    elif "Clay-Sawdust" in filter_key:
        # draw pot
        cx = w//2
        draw.ellipse([cx-160, 120, cx+160, 200], outline="black")
        draw.rectangle([cx-160, 200, cx+160, 360], outline="black")
        draw.ellipse([cx-140, 360, cx+140, 400], outline="black")
        draw.text((20, 220), "Porous ceramic pot (locally fired)", fill="black", font=font)
        draw.text((20, 240), "Optional silver coating; charcoal pad bottom", fill="black", font=font)

    elif "Cloth Emergency" in filter_key:
        draw.rectangle([100, 120, w-100, h-220], outline="black", width=2)
        draw.text((120, 140), "Fold cloth 4-8 layers", fill="black", font=font)
        draw.text((120, 170), "Secure over container; pour slowly", fill="black", font=font)

    elif "SODIS" in filter_key:
        draw.rectangle([80, 100, 220, 260], outline="black")
        draw.text((90, 200), "Clear PET bottle", fill="black", font=font)
        draw.rectangle([300, 100, 440, 260], outline="black")
        draw.text((310, 200), "Sunny surface", fill="black", font=font)
        draw.text((20, 280), "Expose in full sun 6 hours (clear) or 2 days partial", fill="black", font=font)

    elif "Crisis-Zone" in filter_key:
        draw.rectangle([60, 100, w-60, h-120], outline="black")
        draw.text((80, 140), "Tier 1: Settling + Cloth", fill="black", font=font)
        draw.text((80, 180), "Tier 2: Charcoal + Sand microfilter", fill="black", font=font)
        draw.text((80, 220), "Tier 3: Disinfection (SODIS/boil/chlorine)", fill="black", font=font)

    else:
        draw.text((20, 80), "Schematic not available", fill="black", font=font)

    # Save to bytes
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.getvalue()

# -------------------------
# Sample filters and texts (English & Spanish)
# You should reuse your existing dictionaries; for brevity, we include 8 keys and reuse earlier text.
# Replace or extend the strings as needed.
# -------------------------
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

# Short and full texts in English
FILTER_TEXTS_SHORT_EN = {
    "Filter A - Basic Bottle Microfilter": "Filter A - Short\n\nMake: ...\nUse: ...\n",
    "Filter B - Bottle-Neck Cartridge Filter": "Filter B - Short\n\nMake: ...\nUse: ...\n",
    "Filter C - Gravity Bucket Filter": "Filter C - Short\n\nMake: ...\nUse: ...\n",
    "Filter D - Family Bucket Filter": "Filter D - Short\n\nMake: ...\nUse: ...\n",
    "Filter E - Clay-Sawdust Ceramic Filter": "Filter E - Short\n\nMake: ...\nUse: ...\n",
    "Filter F - Cloth Emergency Filter": "Filter F - Short\n\nMake: ...\nUse: ...\n",
    "Filter G - SODIS Solar Disinfection": "Filter G - Short\n\nMake: ...\nUse: ...\n",
    "Filter H - Crisis-Zone 3-Tier Method": "Filter H - Short\n\nMake: ...\nUse: ...\n",
}

FILTER_TEXTS_FULL_EN = {
    "Filter A - Basic Bottle Microfilter": "AQUASHIELD - Filter A (Full)\n\nFull text instructions...\n",
    "Filter B - Bottle-Neck Cartridge Filter": "AQUASHIELD - Filter B (Full)\n\nFull text instructions...\n",
    "Filter C - Gravity Bucket Filter": "AQUASHIELD - Filter C (Full)\n\nFull text instructions...\n",
    "Filter D - Family Bucket Filter": "AQUASHIELD - Filter D (Full)\n\nFull text instructions...\n",
    "Filter E - Clay-Sawdust Ceramic Filter": "AQUASHIELD - Filter E (Full)\n\nFull text instructions...\n",
    "Filter F - Cloth Emergency Filter": "AQUASHIELD - Filter F (Full)\n\nFull text instructions...\n",
    "Filter G - SODIS Solar Disinfection": "AQUASHIELD - Filter G (Full)\n\nFull text instructions...\n",
    "Filter H - Crisis-Zone 3-Tier Method": "AQUASHIELD - Filter H (Full)\n\nFull text instructions...\n",
}

# Spanish short/full (you can replace with the translations you already have)
FILTER_TEXTS_SHORT_ES = {k: "ES short: " + (FILTER_TEXTS_SHORT_EN[k] or "") for k in FILTER_KEYS}
FILTER_TEXTS_FULL_ES = {k: "ES full: " + (FILTER_TEXTS_FULL_EN[k] or "") for k in FILTER_KEYS}

# -------------------------
# Sidebar options & language
# -------------------------
st.sidebar.header("Print-ready A5 Cards")
lang = st.sidebar.selectbox("Language / Idioma", ("English", "Español"))
st.sidebar.markdown("Choose format and download cards for single filter or all filters as ZIP.")
format_choice = st.sidebar.selectbox("Format", ("Text-only A5", "Image + Text A5"))

st.sidebar.markdown("---")
st.sidebar.info("Text-only = smallest files. Image+Text includes a simple schematic PNG generated server-side.")

# -------------------------
# Per-filter generation
# -------------------------
st.header("Generate print-ready A5 cards")

col1, col2 = st.columns([1, 3])
with col1:
    selected = st.selectbox("Select filter", FILTER_KEYS)
    preview_only = st.checkbox("Preview only (don't create ZIP)", value=False)
with col2:
    st.write("Choose single card or produce ZIP of all cards in selected language/format.")

# Get selected texts
def get_texts(key, lang):
    if lang == "English":
        short = FILTER_TEXTS_SHORT_EN.get(key, "Short instructions not available.")
        full = FILTER_TEXTS_FULL_EN.get(key, "Full instructions not available.")
    else:
        short = FILTER_TEXTS_SHORT_ES.get(key, "Instrucciones cortas no disponibles.")
        full = FILTER_TEXTS_FULL_ES.get(key, "Instrucciones completas no disponibles.")
    return short, full

short_text, full_text = get_texts(selected, lang)

st.subheader(f"Preview — {selected} ({lang})")
st.markdown("**Short (preview):**")
st.text(short_text)
st.markdown("**Full (preview):**")
st.text(full_text)

# Buttons to create and download single PDFs
st.markdown("### Download single card")
if format_choice == "Text-only A5":
    buf_short = build_a5_pdf_text_only(short_text)
    buf_full = build_a5_pdf_text_only(full_text)
    st.download_button("⬇ Download SHORT A5 (text-only)", data=buf_short.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_SHORT_{lang}.pdf", mime="application/pdf")
    st.download_button("⬇ Download FULL A5 (text-only)", data=buf_full.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_FULL_{lang}.pdf", mime="application/pdf")
else:
    # Image + text: generate PNG and embed
    png_bytes = create_schematic_png(selected, size=(1200, 900))
    buf_short_img = build_a5_pdf_with_image(short_text, png_bytes)
    buf_full_img = build_a5_pdf_with_image(full_text, png_bytes)
    st.download_button("⬇ Download SHORT A5 (image+text)", data=buf_short_img.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_SHORT_IMG_{lang}.pdf", mime="application/pdf")
    st.download_button("⬇ Download FULL A5 (image+text)", data=buf_full_img.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_FULL_IMG_{lang}.pdf", mime="application/pdf")

# Option: Build ZIP for all filters
st.markdown("---")
st.markdown("### Build ZIP of all cards")
if st.button("Create ZIP of all cards (may take a few seconds)"):
    # create zip in memory
    zipbuf = io.BytesIO()
    with zipfile.ZipFile(zipbuf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for key in FILTER_KEYS:
            short_t, full_t = get_texts(key, lang)
            if format_choice == "Text-only A5":
                s_buf = build_a5_pdf_text_only(short_t)
                f_buf = build_a5_pdf_text_only(full_t)
            else:
                png_b = create_schematic_png(key, size=(1200, 900))
                s_buf = build_a5_pdf_with_image(short_t, png_b)
                f_buf = build_a5_pdf_with_image(full_t, png_b)
            z.writestr(f"{key.replace(' ', '_')}_SHORT_{lang}.pdf", s_buf.getvalue())
            z.writestr(f"{key.replace(' ', '_')}_FULL_{lang}.pdf", f_buf.getvalue())
    zipbuf.seek(0)
    st.download_button("⬇ Download ZIP (all cards)", data=zipbuf.getvalue(), file_name=f"AquaShield_All_Cards_{format_choice}_{lang}.zip", mime="application/zip")

st.caption("Print-ready A5 cards: text-only and image+text options. Images are simple schematic drawings programmatically generated for reliability.")

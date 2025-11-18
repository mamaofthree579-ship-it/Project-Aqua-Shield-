import streamlit as st
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io
import base64
import zipfile
import tempfile
import os
import html

st.set_page_config(page_title="AquaShield — Filters (Expanders)", layout="wide")
st.title("🌍 AquaShield — Filter Library (Short + Expandable Fulls)")

# -------------------------
# Utilities: sanitize, PDF builders, SVG helpers
# -------------------------
def sanitize_for_pdf(text: str) -> str:
    replacements = {
        "—": "-","–": "-","‘": "'","’": "'","“": '"',"”": '"',"…": "...","•": "-",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # ensure latin-1
    return text.encode("latin-1", errors="replace").decode("latin-1")

def build_a5_pdf_bytes_from_text(text: str):
    safe = sanitize_for_pdf(text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    return io.BytesIO(pdf.output(dest="S").encode("latin-1"))

def build_a5_pdf_with_image_and_text(text: str, png_bytes: bytes):
    safe = sanitize_for_pdf(text)
    # write png to temp file for FPDF.image
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(png_bytes)
        tmp.flush()
        img_path = tmp.name
    try:
        pdf = FPDF(format='A5')
        pdf.add_page()
        margin = 10
        page_w = pdf.w - 2*margin
        pdf.image(img_path, x=margin, y=margin, w=page_w)
        pdf.ln(5)
        pdf.set_font("Arial", size=11)
        pdf.set_left_margin(margin)
        pdf.set_right_margin(margin)
        pdf.multi_cell(0, 6, safe)
        return io.BytesIO(pdf.output(dest="S").encode("latin-1"))
    finally:
        try:
            os.remove(img_path)
        except:
            pass

def svg_to_data_url(svg_text: str) -> str:
    b = svg_text.encode("utf-8")
    b64 = base64.b64encode(b).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"

# -------------------------
# Simple programmatic schematic PNG (Pillow)
# -------------------------
def create_schematic_png(filter_key: str, size=(1200, 900)):
    w, h = size
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    try:
        font_h = ImageFont.truetype("DejaVuSans.ttf", 20)
        font_b = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font_h = ImageFont.load_default()
        font_b = ImageFont.load_default()
    draw.text((20, 12), filter_key, fill="black", font=font_h)
    # draw simple shapes per key
    if "Basic Bottle" in filter_key:
        left = w//2 - 140; top = 80; right = w//2 + 140; bottom = h - 160
        draw.rectangle([left, top, right, bottom], outline="black", width=3)
        layer_h = (bottom - top) / 4
        labels = ["Charcoal", "Fine sand", "Small gravel", "Cloth plug"]
        for i, lab in enumerate(labels):
            y = int(top + (i+1)*layer_h)
            draw.line([left, y, right, y], fill="black", width=2)
            draw.text((40, int(y - layer_h/2)), f"Layer: {lab}", fill="black", font=font_b)
    elif "Bottle-Neck" in filter_key:
        cx = w//2
        draw.rectangle([cx-60, 120, cx+60, h-120], outline="black", width=3)
        parts = ["Microfiber", "Optional sand", "Charcoal", "Outlet plug"]
        segment = (h-240)/len(parts)
        for idx, p in enumerate(parts):
            y = 120 + int((idx+1)*segment)
            draw.line([cx-60, y, cx+60, y], fill="black", width=2)
            draw.text((40, y - int(segment/2)), p, fill="black", font=font_b)
    elif "Gravity Bucket" in filter_key or "Family Bucket" in filter_key:
        left = 120; right = w - 120; top = 80; bottom = h - 160
        draw.rectangle([left, top, right, bottom], outline="black", width=3)
        layers = ["Cloth/diffuser", "Coarse gravel", "Small gravel", "Charcoal", "Deep sand"]
        step = (bottom - top) / (len(layers) + 1)
        for i, lab in enumerate(layers):
            y = int(top + (i+1)*step)
            draw.line([left, y, right, y], fill="black", width=2)
            draw.text((40, y - int(step/2)), lab, fill="black", font=font_b)
    elif "Clay-Sawdust" in filter_key:
        cx = w//2
        draw.ellipse([cx-200, 120, cx+200, 220], outline="black", width=3)
        draw.rectangle([cx-180, 220, cx+180, 420], outline="black", width=3)
        draw.ellipse([cx-160, 420, cx+160, 460], outline="black", width=3)
        draw.text((40, 240), "Porous ceramic pot (locally fired)", fill="black", font=font_b)
    elif "Cloth Emergency" in filter_key:
        draw.rectangle([80, 120, w-80, h-180], outline="black", width=3)
        draw.text((100, 160), "Fold cloth 4-8 layers", fill="black", font=font_b)
        draw.text((100, 190), "Secure over container; pour slowly", fill="black", font=font_b)
    elif "SODIS" in filter_key:
        draw.rectangle([60, 100, 220, 260], outline="black", width=2)
        draw.text((70, 230), "Clear PET bottle", fill="black", font=font_b)
        draw.rectangle([320, 100, 480, 260], outline="black", width=2)
        draw.text((330, 230), "Sunny surface", fill="black", font=font_b)
        draw.text((60, 300), "Expose 6 hours (clear) or 2 days (partial)", fill="black", font=font_b)
    elif "Crisis-Zone" in filter_key:
        draw.text((60, 140), "Tier 1: Settling + Cloth", fill="black", font=font_b)
        draw.text((60, 180), "Tier 2: Charcoal + Sand microfilter", fill="black", font=font_b)
        draw.text((60, 220), "Tier 3: Disinfection (SODIS/boil/chlorine)", fill="black", font=font_b)
    else:
        draw.text((40, 120), "Schematic not available", fill="black", font=font_b)
    out = io.BytesIO(); img.save(out, format="PNG"); out.seek(0)
    return out.getvalue()

def create_qr_png(payload: str, box_size=4, border=2):
    q = qrcode.QRCode(box_size=box_size, border=border)
    q.add_data(payload)
    q.make(fit=True)
    img = q.make_image(fill_color="black", back_color="white").convert("RGB")
    out = io.BytesIO(); img.save(out, format="PNG"); out.seek(0)
    return out.getvalue()

def compose_card_image(filter_key: str, short_text: str, include_schematic=True, qr_payload=None, card_size=(1200,900)):
    w, h = card_size
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    try:
        font_h = ImageFont.truetype("DejaVuSans.ttf", 20)
        font_b = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font_h = ImageFont.load_default()
        font_b = ImageFont.load_default()
    draw.text((20, 10), filter_key, fill="black", font=font_h)
    if include_schematic:
        schematic = create_schematic_png(filter_key, size=(int(w*0.55), int(h*0.45)))
        s_img = Image.open(io.BytesIO(schematic))
        s_w, s_h = s_img.size
        img.paste(s_img, (w - s_w - 20, 40))
    text_area_x = 20
    text_area_y = 60
    text_area_w = w - (int(w*0.55) + 60) if include_schematic else w - 40
    # simple wrap
    words = short_text.split()
    line = ""
    y = text_area_y
    for word in words:
        test = (line + " " + word).strip()
        if draw.textlength(test, font=font_b) <= text_area_w:
            line = test
        else:
            draw.text((text_area_x, y), line, fill="black", font=font_b)
            y += 18
            line = word
    if line:
        draw.text((text_area_x, y), line, fill="black", font=font_b)
        y += 20
    if qr_payload:
        qr_png = create_qr_png(qr_payload, box_size=6, border=1)
        qr_img = Image.open(io.BytesIO(qr_png))
        qr_w, qr_h = qr_img.size
        qr_pos = (w - qr_w - 20, h - qr_h - 20)
        img.paste(qr_img, qr_pos)
        draw.text((qr_pos[0]-10, qr_pos[1]-20), "Scan for short instructions", fill="black", font=font_b)
    out = io.BytesIO(); img.save(out, format="PNG"); out.seek(0); return out.getvalue()

# -------------------------
# Data: keys, SVGs, EN/ES short+full texts
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

# Simple SVGs (kept ASCII-safe)
FILTER_SVGS = {
    "Filter A - Basic Bottle Microfilter": """<svg ...> ... </svg>""",
    "Filter B - Bottle-Neck Cartridge Filter": """<svg ...> ... </svg>""",
    "Filter C - Gravity Bucket Filter": """<svg ...> ... </svg>""",
    "Filter D - Family Bucket Filter": """<svg ...> ... </svg>""",
    "Filter E - Clay-Sawdust Ceramic Filter": """<svg ...> ... </svg>""",
    "Filter F - Cloth Emergency Filter": """<svg ...> ... </svg>""",
    "Filter G - SODIS Solar Disinfection": """<svg ...> ... </svg>""",
    "Filter H - Crisis-Zone 3-Tier Method": """<svg ...> ... </svg>""",
}
# NOTE: Replace the placeholder SVG strings above with your detailed SVG text if you prefer.

# English short/full
FILTER_TEXTS_SHORT_EN = {
    "Filter A - Basic Bottle Microfilter": "Filter A - Short\n\nCut bottle, tie cloth, add charcoal, sand, gravel. Pour slowly; discard first liter; disinfect before drinking.",
    "Filter B - Bottle-Neck Cartridge Filter": "Filter B - Short\n\nPack neck with microfiber, optional sand and charcoal. Pour slowly; discard first 1-2 L; replace media when turbid.",
    "Filter C - Gravity Bucket Filter": "Filter C - Short\n\nStack layers in bucket: cloth, gravel, charcoal, sand. Fill top, collect from bottom. Disinfect before drinking.",
    "Filter D - Family Bucket Filter": "Filter D - Short\n\nTwo-bucket system with spigot. Top filter: gravel, charcoal, sand. Replace charcoal monthly; disinfect before drinking.",
    "Filter E - Clay-Sawdust Ceramic Filter": "Filter E - Short\n\nMake porous pot (clay+sawdust). Use as cup; optional silver coat. Pour and collect; disinfect after if drinking.",
    "Filter F - Cloth Emergency Filter": "Filter F - Short\n\nFold clean cloth 4-8 layers. Pour slowly, repeat if turbid, then disinfect.",
    "Filter G - SODIS Solar Disinfection": "Filter G - Short\n\nPre-filter to clear, fill PET bottle, expose to full sun 6 hours (clear) or 2 days (partial).",
    "Filter H - Crisis-Zone 3-Tier Method": "Filter H - Short\n\nTier 1: Settling + cloth. Tier 2: Charcoal+sand microfilter. Tier 3: Disinfection (SODIS/boil/chlorine).",
}

FILTER_TEXTS_FULL_EN = {
    "Filter A - Basic Bottle Microfilter": "AQUASHIELD - Filter A (Full)\n\nPurpose: Low-cost gravity bottle filter to improve clarity and taste. Not a disinfectant.\n\nMaterials: 1 bottle, cloth, charcoal, fine sand, gravel.\n\nSteps: ... (full instructions as provided earlier).",
    "Filter B - Bottle-Neck Cartridge Filter": "AQUASHIELD - Filter B (Full)\n\n... (full text).",
    "Filter C - Gravity Bucket Filter": "AQUASHIELD - Filter C (Full)\n\n... (full text).",
    "Filter D - Family Bucket Filter": "AQUASHIELD - Filter D (Full)\n\n... (full text).",
    "Filter E - Clay-Sawdust Ceramic Filter": "AQUASHIELD - Filter E (Full)\n\n... (full text).",
    "Filter F - Cloth Emergency Filter": "AQUASHIELD - Filter F (Full)\n\n... (full text).",
    "Filter G - SODIS Solar Disinfection": "AQUASHIELD - Filter G (Full)\n\n... (full text).",
    "Filter H - Crisis-Zone 3-Tier Method": "AQUASHIELD - Filter H (Full)\n\n... (full text).",
}

# Spanish short/full (you can replace with the exact translations you want)
FILTER_TEXTS_SHORT_ES = {
    k: ("ES short: " + FILTER_TEXTS_SHORT_EN[k]) for k in FILTER_KEYS
}
FILTER_TEXTS_FULL_ES = {
    k: ("ES full: " + FILTER_TEXTS_FULL_EN[k]) for k in FILTER_KEYS
}

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Options")
lang = st.sidebar.selectbox("Language default for downloads", ("English", "Español"))
st.sidebar.markdown("PNG schematic and card images are generated server-side for reliability.")
st.sidebar.markdown("---")
st.sidebar.info("Short instructions are shown; open 'Full' expanders to read full instructions (English then Spanish).")

# -------------------------
# Main interface: list filters
# -------------------------
for key in FILTER_KEYS:
    st.header(key)

    # layout: schematic left, texts right
    col_svg, col_text = st.columns([1, 1.2])
    with col_svg:
        st.subheader("Schematic")
        svg_code = FILTER_SVGS.get(key, "<svg></svg>")
        st.image(svg_to_data_url(svg_code), width=420)
        st.download_button("⬇ Download SVG", data=svg_code, file_name=f"{key.replace(' ', '_')}.svg", mime="image/svg+xml")
        # server PNG schematic
        png_bytes = create_schematic_png(key, size=(900,600))
        st.download_button("⬇ Download schematic PNG", data=png_bytes, file_name=f"{key.replace(' ', '_')}.png", mime="image/png")

    with col_text:
        st.subheader("Short instructions (English then Spanish)")
        short_en = FILTER_TEXTS_SHORT_EN.get(key, "Short instructions not available.")
        short_es = FILTER_TEXTS_SHORT_ES.get(key, "Instrucciones cortas no disponibles.")
        st.markdown("**English (short):**")
        st.text(short_en)
        st.markdown("**Español (resumen):**")
        st.text(short_es)

        # Expanders for full text (English then Spanish)
        with st.expander("Show full instructions — English"):
            full_en = FILTER_TEXTS_FULL_EN.get(key, "Full instructions not available.")
            st.text(full_en)
            # download full english PDF
            pdf_en = build_a5_pdf_bytes_from_text(full_en)
            st.download_button("⬇ Download Full (English) A5 PDF", data=pdf_en.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_FULL_EN_A5.pdf", mime="application/pdf")
        with st.expander("Mostrar instrucciones completas — Español"):
            full_es = FILTER_TEXTS_FULL_ES.get(key, "Instrucciones completas no disponibles.")
            st.text(full_es)
            pdf_es = build_a5_pdf_bytes_from_text(full_es)
            st.download_button("⬇ Descargar completo (Español) A5 PDF", data=pdf_es.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_FULL_ES_A5.pdf", mime="application/pdf")

        # Short PDFs for quick download
        short_pdf_en = build_a5_pdf_bytes_from_text(short_en)
        short_pdf_es = build_a5_pdf_bytes_from_text(short_es)
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇ Short PDF (English)", data=short_pdf_en.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_SHORT_EN_A5.pdf", mime="application/pdf")
        with c2:
            st.download_button("⬇ Resumen PDF (Español)", data=short_pdf_es.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_SHORT_ES_A5.pdf", mime="application/pdf")

        # option to create an A5 card with image + QR embedded (for print)
        st.markdown("---")
        if st.button(f"Create card image + PDF for {key}"):
            qr_payload = short_en if lang == "English" else short_es
            card_png = compose_card_image(key, short_en if lang=="English" else short_es, include_schematic=True, qr_payload=qr_payload)
            # A5 PDF with image + text
            a5_img_pdf = build_a5_pdf_with_image_and_text(short_en if lang=="English" else short_es, card_png)
            st.success("Card created — download below")
            st.download_button("⬇ Download card PDF (A5, image+text)", data=a5_img_pdf.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_CARD_{lang}.pdf", mime="application/pdf")
            st.image(card_png, width=420)

    st.markdown("---")

# -------------------------
# Bulk ZIP downloads: all SVGs / all Short PDFs / all Full PDFs (EN/ES)
# -------------------------
st.sidebar.header("Bulk downloads")
# Build SVG zip
svg_zip = io.BytesIO()
with zipfile.ZipFile(svg_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for k, v in FILTER_SVGS.items():
        z.writestr(f"{k.replace(' ', '_')}.svg", v)
svg_zip.seek(0)
st.sidebar.download_button("⬇ Download ALL SVGs (ZIP)", data=svg_zip.getvalue(), file_name="AquaShield_All_SVGs.zip", mime="application/zip")

# Build PDFs zip for current language selection
def build_pdf_zips_for_language(language):
    pdf_short_dict = {}
    pdf_full_dict = {}
    for k in FILTER_KEYS:
        if language == "English":
            s = FILTER_TEXTS_SHORT_EN.get(k, "")
            f = FILTER_TEXTS_FULL_EN.get(k, "")
            s_name = f"{k.replace(' ', '_')}_SHORT_EN.pdf"
            f_name = f"{k.replace(' ', '_')}_FULL_EN.pdf"
        else:
            s = FILTER_TEXTS_SHORT_ES.get(k, "")
            f = FILTER_TEXTS_FULL_ES.get(k, "")
            s_name = f"{k.replace(' ', '_')}_SHORT_ES.pdf"
            f_name = f"{k.replace(' ', '_')}_FULL_ES.pdf"
        pdf_short_dict[s_name] = build_a5_pdf_bytes_from_text(s)
        pdf_full_dict[f_name] = build_a5_pdf_bytes_from_text(f)
    # zip them
    short_zip = io.BytesIO()
    with zipfile.ZipFile(short_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for name, buf in pdf_short_dict.items():
            z.writestr(name, buf.getvalue())
    short_zip.seek(0)
    full_zip = io.BytesIO()
    with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for name, buf in pdf_full_dict.items():
            z.writestr(name, buf.getvalue())
    full_zip.seek(0)
    return short_zip, full_zip

short_zip_en, full_zip_en = build_pdf_zips_for_language("English")
short_zip_es, full_zip_es = build_pdf_zips_for_language("Español")

st.sidebar.download_button("⬇ Download ALL Short PDFs (EN)", data=short_zip_en.getvalue(), file_name="AquaShield_Short_PDFs_EN.zip", mime="application/zip")
st.sidebar.download_button("⬇ Download ALL Full PDFs (EN)", data=full_zip_en.getvalue(), file_name="AquaShield_Full_PDFs_EN.zip", mime="application/zip")
st.sidebar.download_button("⬇ Download ALL Short PDFs (ES)", data=short_zip_es.getvalue(), file_name="AquaShield_Short_PDFs_ES.zip", mime="application/zip")
st.sidebar.download_button("⬇ Download ALL Full PDFs (ES)", data=full_zip_es.getvalue(), file_name="AquaShield_Full_PDFs_ES.zip", mime="application/zip")

st.markdown("---")
st.caption("AquaShield — short instructions visible by default. Open the Full expanders (English then Spanish) to read the detailed instructions. PDFs are A5 and sanitized for compatibility.")
    

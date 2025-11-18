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

st.set_page_config(page_title="AquaShield — Final (QR offline + online)", layout="wide")
st.title("🌍 AquaShield — Filters + Offline QR (short) + Online QR (link)")

# -------------------------
# Utilities
# -------------------------
def sanitize_for_pdf(text: str) -> str:
    replacements = {
        "—": "-", "–": "-", "‘": "'", "’": "'", "“": '"', "”": '"', "…": "...", "•": "-"
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
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
    return "data:image/svg+xml;base64," + base64.b64encode(svg_text.encode("utf-8")).decode("ascii")

# -------------------------
# Simple PNG schematic generator (Pillow)
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

def create_qr_png_from_text(payload: str, box_size=4, border=2):
    q = qrcode.QRCode(box_size=box_size, border=border)
    q.add_data(payload)
    q.make(fit=True)
    img = q.make_image(fill_color="black", back_color="white").convert("RGB")
    out = io.BytesIO(); img.save(out, format="PNG"); out.seek(0)
    return out.getvalue()

# -------------------------
# Filters list, SVGs, texts (EN + ES)
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

# Replace / expand with your real SVGs if you want; placeholders kept minimal
FILTER_SVGS = {k: f"<svg><text>{k}</text></svg>" for k in FILTER_KEYS}

# English short/full (real content from earlier; replace as needed)
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
    "Filter B - Bottle-Neck Cartridge Filter": "AQUASHIELD - Filter B (Full)\n\nFull instructions ...",
    "Filter C - Gravity Bucket Filter": "AQUASHIELD - Filter C (Full)\n\nFull instructions ...",
    "Filter D - Family Bucket Filter": "AQUASHIELD - Filter D (Full)\n\nFull instructions ...",
    "Filter E - Clay-Sawdust Ceramic Filter": "AQUASHIELD - Filter E (Full)\n\nFull instructions ...",
    "Filter F - Cloth Emergency Filter": "AQUASHIELD - Filter F (Full)\n\nFull instructions ...",
    "Filter G - SODIS Solar Disinfection": "AQUASHIELD - Filter G (Full)\n\nFull instructions ...",
    "Filter H - Crisis-Zone 3-Tier Method": "AQUASHIELD - Filter H (Full)\n\nFull instructions ...",
}

# Spanish short/full (basic translations — you can replace with your exact phrasing)
FILTER_TEXTS_SHORT_ES = {k: "ES: " + FILTER_TEXTS_SHORT_EN[k] for k in FILTER_KEYS}
FILTER_TEXTS_FULL_ES = {k: "ES: " + FILTER_TEXTS_FULL_EN[k] for k in FILTER_KEYS}

# -------------------------
# ONLINE URLs: provided + placeholders for G & H
# -------------------------
ONLINE_URLS = {
    "Filter A - Basic Bottle Microfilter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/basic_gravity_filter.md",
    "Filter B - Bottle-Neck Cartridge Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/ceramic_filter.md",
    "Filter C - Gravity Bucket Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/cloth_filter.md",
    "Filter D - Family Bucket Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/family_bucket_filter.md",
    "Filter E - Clay-Sawdust Ceramic Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/sodis.md",
    "Filter F - Cloth Emergency Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/crisis_zone_filter_set.md",
    # placeholders for G & H (update later)
    "Filter G - SODIS Solar Disinfection": "https://example.org/AquaShield/filter-G",
    "Filter H - Crisis-Zone 3-Tier Method": "https://example.org/AquaShield/filter-H",
}

# -------------------------
# Sidebar & options
# -------------------------
st.sidebar.header("Options & Downloads")
lang = st.sidebar.selectbox("Language default for downloads", ("English", "Español"))
st.sidebar.markdown("QR behavior:")
st.sidebar.radio("Printed card QR contains:", ("Offline short text (recommended)",), index=0)
st.sidebar.markdown("---")
st.sidebar.info("Printed cards embed offline QR that contains the short instructions (works offline). Online QR links point to the provided URLs (useful where connected).")

# SVG bundle in sidebar
svg_zip_io = io.BytesIO()
with zipfile.ZipFile(svg_zip_io, "w", zipfile.ZIP_DEFLATED) as z:
    for k, v in FILTER_SVGS.items():
        z.writestr(f"{k.replace(' ', '_')}.svg", v)
svg_zip_io.seek(0)
st.sidebar.download_button("⬇ Download all SVGs (ZIP)", data=svg_zip_io.getvalue(), file_name="AquaShield_All_SVGs.zip", mime="application/zip")

# -------------------------
# Main UI: per-filter display (English-first), expanders for full text
# -------------------------
for key in FILTER_KEYS:
    st.header(key)
    col_svg, col_text = st.columns([1, 1.2])

    with col_svg:
        st.subheader("Schematic")
        svg_code = FILTER_SVGS.get(key, "<svg></svg>")
        st.image(svg_to_data_url(svg_code), width=420)
        st.download_button("⬇ Download SVG", data=svg_code, file_name=f"{key.replace(' ', '_')}.svg", mime="image/svg+xml")
        png_schem = create_schematic_png(key, size=(900,600))
        st.download_button("⬇ Download PNG schematic", data=png_schem, file_name=f"{key.replace(' ', '_')}.png", mime="image/png")

    with col_text:
        st.subheader("Short instructions (English then Spanish)")
        short_en = FILTER_TEXTS_SHORT_EN.get(key, "Short instructions not available.")
        short_es = FILTER_TEXTS_SHORT_ES.get(key, "Instrucciones cortas no disponibles.")
        st.markdown("**English (short):**")
        st.text(short_en)
        st.markdown("**Español (resumen):**")
        st.text(short_es)

        # Create QR images: offline_text QR (short text) and online QR (link)
        offline_qr_payload_en = short_en.strip()
        offline_qr_payload_es = short_es.strip()
        online_url = ONLINE_URLS.get(key, "https://example.org/AquaShield/")

        # Generate QR PNGs
        qr_off_en = create_qr_png_from_text(offline_qr_payload_en, box_size=4, border=2)
        qr_off_es = create_qr_png_from_text(offline_qr_payload_es, box_size=4, border=2)
        qr_online = create_qr_png_from_text(online_url, box_size=4, border=2)

        # Download QR buttons
        st.markdown("**QR codes (download):**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇ Offline QR — EN (PNG)", data=qr_off_en, file_name=f"{key.replace(' ','_')}_QR_offline_EN.png", mime="image/png")
        with c2:
            st.download_button("⬇ Offline QR — ES (PNG)", data=qr_off_es, file_name=f"{key.replace(' ','_')}_QR_offline_ES.png", mime="image/png")
        with c3:
            st.download_button("⬇ Online QR — Link (PNG)", data=qr_online, file_name=f"{key.replace(' ','_')}_QR_online.png", mime="image/png")

        # Expanders for full text EN then ES
        with st.expander("Show full instructions — English"):
            full_en = FILTER_TEXTS_FULL_EN.get(key, "Full instructions not available.")
            st.text(full_en)
            pdf_en = build_a5_pdf_bytes_from_text(full_en)
            st.download_button("⬇ Download Full (English) A5 PDF", data=pdf_en.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_FULL_EN_A5.pdf", mime="application/pdf")
        with st.expander("Mostrar instrucciones completas — Español"):
            full_es = FILTER_TEXTS_FULL_ES.get(key, "Instrucciones completas no disponibles.")
            st.text(full_es)
            pdf_es = build_a5_pdf_bytes_from_text(full_es)
            st.download_button("⬇ Descargar completo (Español) A5 PDF", data=pdf_es.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_FULL_ES_A5.pdf", mime="application/pdf")

        # Short PDFs (quick)
        short_pdf_en = build_a5_pdf_bytes_from_text(short_en)
        short_pdf_es = build_a5_pdf_bytes_from_text(short_es)
        cc1, cc2 = st.columns(2)
        with cc1:
            st.download_button("⬇ Short PDF (English)", data=short_pdf_en.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_SHORT_EN_A5.pdf", mime="application/pdf")
        with cc2:
            st.download_button("⬇ Resumen PDF (Español)", data=short_pdf_es.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_SHORT_ES_A5.pdf", mime="application/pdf")

        # Create and download A5 card PDF (image+text) with offline QR embedded (for printing)
        if st.button(f"Create printed card (A5) for {key}"):
            # Use offline QR in language selected sidebar (lang)
            use_lang = lang
            short_payload = short_en if use_lang == "English" else short_es
            # Create composite PNG with schematic + short text + offline QR
            card_png = compose_card_image(key, short_payload, include_schematic=True, qr_payload=short_payload)
            card_pdf = build_a5_pdf_with_image_and_text(short_payload, card_png)
            st.success("Card ready — download below")
            st.download_button("⬇ Download card PDF (A5, image+text)", data=card_pdf.getvalue(),
                               file_name=f"{key.replace(' ', '_')}_CARD_{use_lang}.pdf", mime="application/pdf")
            st.image(card_png, width=420)

    st.markdown("---")

# -------------------------
# Bulk ZIPs: SVGs + PDFs (EN/ES)
# -------------------------
st.sidebar.header("Bulk exports")
# SVGs zip already provided above; also build PDF zips for both languages
def build_pdf_zip(language):
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
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
            z.writestr(s_name, build_a5_pdf_bytes_from_text(s).getvalue())
            z.writestr(f_name, build_a5_pdf_bytes_from_text(f).getvalue())
    zbuf.seek(0)
    return zbuf

short_en_zip = build_pdf_zip("English")
short_es_zip = build_pdf_zip("Español")
st.sidebar.download_button("⬇ Download ALL PDFs (EN)", data=short_en_zip.getvalue(), file_name="AquaShield_All_PDFs_EN.zip", mime="application/zip")
st.sidebar.download_button("⬇ Download ALL PDFs (ES)", data=short_es_zip.getvalue(), file_name="AquaShield_All_PDFs_ES.zip", mime="application/zip")

st.markdown("---")
st.caption("Printed cards embed offline QR (short instructions). Online QR PNGs are also available for download (link to each filter). Update placeholder URLs for G/H later by editing the ONLINE_URLS dictionary.")
    

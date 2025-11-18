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
import math

st.set_page_config(page_title="AquaShield — Print Layouts + QR", layout="wide")
st.title("AquaShield — Print-ready Cards + Print Sheets + QR (EN/ES)")

# -------------------------
# Utilities
# -------------------------
def sanitize_for_pdf(text: str) -> str:
    """Make text safe for FPDF (latin-1)."""
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
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text

def build_a5_pdf_text_only(text: str):
    safe = sanitize_for_pdf(text)
    pdf = FPDF(format='A5')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_font("Arial", size=11)
    for line in safe.splitlines():
        pdf.multi_cell(0, 6, line)
    output = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(output)

def build_a4_two_up_a5(pages_buffers):
    """
    Build A4 PDF with two A5 pages per A4 sheet.
    pages_buffers: list of BytesIO objects each containing an A5 PDF (single page).
    We'll rasterize each A5 page into PNG via FPDF export -> but simpler: 
    We'll render cards as image buffers (PIL) instead and compose them on A4.
    """
    # Expect pages_buffers given as PNG bytes (we will use image composition approach)
    # pages_buffers here will be list of PNG bytes representing A5 card images at high res.
    # Create A4 canvas (landscape or portrait?) We'll use portrait A4 and place two A5 vertically.
    # A4 mm -> points: FPDF uses mm; we'll create final PDF via FPDF placing images.
    pdf = FPDF(format='A4', unit='mm')
    pdf.set_auto_page_break(False)
    # A4 size in mm: 210 x 297; A5 is 148 x 210
    a4_w_mm, a4_h_mm = 210, 297
    card_w_mm, card_h_mm = 148, 210  # A5 portrait
    # For each pair of PNGs, create a page
    i = 0
    while i < len(pages_buffers):
        pdf.add_page()
        # top card (centered horizontally)
        top_img = pages_buffers[i]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as t1:
            t1.write(top_img)
            t1.flush()
            img1 = t1.name
        pdf.image(img1, x=(a4_w_mm - card_w_mm)/2.0, y=10, w=card_w_mm)
        # bottom card if exists
        if i+1 < len(pages_buffers):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as t2:
                t2.write(pages_buffers[i+1])
                t2.flush()
                img2 = t2.name
            pdf.image(img2, x=(a4_w_mm - card_w_mm)/2.0, y=10 + card_h_mm + 10, w=card_w_mm)
            # cleanup
            try:
                os.remove(img2)
            except:
                pass
        try:
            os.remove(img1)
        except:
            pass
        i += 2
    out = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(out)

def build_a4_four_up_a6(png_buffers):
    """
    Compose 4 A6 cards onto one A4 page (2x2 grid).
    png_buffers: list of PNG bytes for A6-sized cards (or we'll scale).
    """
    # Create PDF A4 and place four images per page
    pdf = FPDF(format='A4', unit='mm')
    pdf.set_auto_page_break(False)
    a4_w_mm, a4_h_mm = 210, 297
    # A6 size in mm: 105 x 148 (portrait)
    a6_w_mm, a6_h_mm = 105, 148
    i = 0
    while i < len(png_buffers):
        pdf.add_page()
        positions = [
            ((a4_w_mm/4.0) - (a6_w_mm/2.0), 10),  # upper-left approx center quarter
            ((3*a4_w_mm/4.0) - (a6_w_mm/2.0), 10),  # upper-right
            ((a4_w_mm/4.0) - (a6_w_mm/2.0), 10 + a6_h_mm + 10),  # lower-left
            ((3*a4_w_mm/4.0) - (a6_w_mm/2.0), 10 + a6_h_mm + 10),  # lower-right
        ]
        for slot in range(4):
            if i+slot >= len(png_buffers):
                break
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as t:
                t.write(png_buffers[i+slot])
                t.flush()
                path = t.name
            x_mm, y_mm = positions[slot]
            pdf.image(path, x=x_mm, y=y_mm, w=a6_w_mm)
            try:
                os.remove(path)
            except:
                pass
        i += 4
    out = pdf.output(dest="S").encode("latin-1")
    return io.BytesIO(out)

def pil_text_wrap(draw, text, font, max_width):
    """Simple helper to wrap text for PIL drawing; returns list of lines"""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        wwidth = draw.textbbox((0,0), test, font=font)[2]
        if wwidth <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# -------------------------
# Schematic & QR生成 helpers
# -------------------------
def create_schematic_png(filter_key: str, size=(1200, 900)):
    """Return PNG bytes for schematic (same as prior helper, slightly refined)."""
    w, h = size
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
    draw.text((20, 12), filter_key, fill="black", font=font)
    # simple shapes per key
    if "Basic Bottle" in filter_key:
        left = w//2 - 140
        top = 80
        right = w//2 + 140
        bottom = h - 160
        draw.rectangle([left, top, right, bottom], outline="black", width=3)
        # layers: charcoal, sand, gravel, cloth
        layer_h = (bottom - top) / 4
        labels = ["Charcoal", "Fine sand", "Small gravel", "Cloth plug"]
        for i, lab in enumerate(labels):
            y = int(top + (i+1)*layer_h)
            draw.line([left, y, right, y], fill="black", width=2)
            draw.text((40, int(y - layer_h/2)), f"Layer: {lab}", fill="black", font=font)
    elif "Bottle-Neck" in filter_key:
        cx = w//2
        draw.rectangle([cx-60, 120, cx+60, h-120], outline="black", width=3)
        parts = ["Microfiber", "Optional sand", "Charcoal", "Outlet plug"]
        segment = (h-240)/len(parts)
        for idx, p in enumerate(parts):
            y = 120 + int((idx+1)*segment)
            draw.line([cx-60, y, cx+60, y], fill="black", width=2)
            draw.text((40, y - int(segment/2)), p, fill="black", font=font)
    elif "Gravity Bucket" in filter_key or "Family Bucket" in filter_key:
        left = 120
        right = w - 120
        top = 80
        bottom = h - 160
        draw.rectangle([left, top, right, bottom], outline="black", width=3)
        layers = ["Cloth/diffuser", "Coarse gravel", "Small gravel", "Charcoal", "Deep sand"]
        step = (bottom - top) / (len(layers) + 1)
        for i, lab in enumerate(layers):
            y = int(top + (i+1)*step)
            draw.line([left, y, right, y], fill="black", width=2)
            draw.text((40, y - int(step/2)), lab, fill="black", font=font)
    elif "Clay-Sawdust" in filter_key:
        cx = w//2
        draw.ellipse([cx-200, 120, cx+200, 220], outline="black", width=3)
        draw.rectangle([cx-180, 220, cx+180, 420], outline="black", width=3)
        draw.ellipse([cx-160, 420, cx+160, 460], outline="black", width=3)
        draw.text((40, 240), "Porous ceramic pot (locally fired)", fill="black", font=font)
    elif "Cloth Emergency" in filter_key:
        draw.rectangle([80, 120, w-80, h-180], outline="black", width=3)
        draw.text((100, 160), "Fold cloth 4-8 layers", fill="black", font=font)
        draw.text((100, 190), "Secure over clean container; pour slowly", fill="black", font=font)
    elif "SODIS" in filter_key:
        draw.rectangle([60, 100, 220, 260], outline="black", width=2)
        draw.text((70, 230), "Clear PET bottle", fill="black", font=font)
        draw.rectangle([320, 100, 480, 260], outline="black", width=2)
        draw.text((330, 230), "Sunny surface", fill="black", font=font)
        draw.text((60, 300), "Expose 6 hours (clear) or 2 days (partial)", fill="black", font=font)
    elif "Crisis-Zone" in filter_key:
        draw.text((60, 140), "Tier 1: Settling + Cloth", fill="black", font=font)
        draw.text((60, 180), "Tier 2: Charcoal + Sand microfilter", fill="black", font=font)
        draw.text((60, 220), "Tier 3: Disinfection (SODIS/boil/chlorine)", fill="black", font=font)
    else:
        draw.text((40, 120), "Schematic not available", fill="black", font=font)

    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.getvalue()

def create_qr_png(payload: str, box_size=4, border=2):
    q = qrcode.QRCode(box_size=box_size, border=border)
    q.add_data(payload)
    q.make(fit=True)
    img = q.make_image(fill_color="black", back_color="white").convert("RGB")
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.getvalue()

def compose_card_image(filter_key: str, lang_short_text: str, include_schematic=True, qr_payload=None, card_size=(1200, 900)):
    """Create a composite PNG for a single A5 card: schematic (optional), text, QR."""
    w, h = card_size
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    try:
        font_h = ImageFont.truetype("DejaVuSans.ttf", 20)
        font_b = ImageFont.truetype("DejaVuSans.ttf", 14)
    except:
        font_h = ImageFont.load_default()
        font_b = ImageFont.load_default()
    # Header
    draw.text((20, 10), filter_key, fill="black", font=font_h)
    # If schematic include at top-right
    if include_schematic:
        schematic = create_schematic_png(filter_key, size=(int(w*0.55), int(h*0.45)))
        s_img = Image.open(io.BytesIO(schematic))
        s_w, s_h = s_img.size
        img.paste(s_img, (w - s_w - 20, 40))
    # Text area left side below header
    text_area_x = 20
    text_area_y = 60
    text_area_w = w - (int(w*0.55) + 60) if include_schematic else w - 40
    lines = pil_text_wrap(draw, lang_short_text, font_b, text_area_w)
    y = text_area_y
    for line in lines:
        draw.text((text_area_x, y), line, fill="black", font=font_b)
        y += 18
    # QR code in bottom-right
    if qr_payload:
        qr_png = create_qr_png(qr_payload, box_size=6, border=1)
        qr_img = Image.open(io.BytesIO(qr_png))
        qr_w, qr_h = qr_img.size
        qr_pos = (w - qr_w - 20, h - qr_h - 20)
        img.paste(qr_img, qr_pos)
        # label
        draw.text((qr_pos[0]-10, qr_pos[1]-20), "Scan for short instructions", fill="black", font=font_b)
    out = io.BytesIO()
    img.save(out, format="PNG")
    out.seek(0)
    return out.getvalue()

# -------------------------
# Filter data (texts in EN/ES)
# Use your real texts here; I reuse previous dictionaries but recommend replacing with your final wording.
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

# Short and full texts in English (use the full versions from prior)
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

# Spanish translations — you can refine these. They use latin-1 characters supported by FPDF.
FILTER_TEXTS_SHORT_ES = {
    "Filter A - Basic Bottle Microfilter": "Filtro A - Resumen\n\nCorte la botella, ate paño, agregue carbón, arena, grava. Vierta despacio; deseche primer litro; desinfecte antes de beber.",
    "Filter B - Bottle-Neck Cartridge Filter": "Filtro B - Resumen\n\nEmpaque el cuello con microfibra, arena y carbón opcionales. Vierta despacio; deseche 1-2 L iniciales; reemplace medios según turbidez.",
    "Filter C - Gravity Bucket Filter": "Filtro C - Resumen\n\nApile capas: paño, grava, carbón, arena. Llene arriba; recoja abajo. Desinfectar antes de beber.",
    "Filter D - Family Bucket Filter": "Filtro D - Resumen\n\nSistema de dos cubetas con llave. Filtro superior: grava, carbón, arena. Reemplace carbón mensualmente; desinfecte antes de beber.",
    "Filter E - Clay-Sawdust Ceramic Filter": "Filtro E - Resumen\n\nFabricar vasija porosa (arcilla+aserrín). Usar como taza; capa de plata opcional. Vierta y recoja; desinfecte para beber.",
    "Filter F - Cloth Emergency Filter": "Filtro F - Resumen\n\nDoble paño limpio 4-8 capas. Vierta despacio, repita si está turbio, luego desinfecte.",
    "Filter G - SODIS Solar Disinfection": "Filtro G - Resumen\n\nPrefiltrar hasta claro, llenar botella PET, exponer al sol 6 horas (claro) o 2 días (parcial).",
    "Filter H - Crisis-Zone 3-Tier Method": "Filtro H - Resumen\n\nNivel 1: Sedimentación + paño. Nivel 2: Carbón+arena microfiltro. Nivel 3: Desinfección (SODIS/hervir/cloro).",
}

FILTER_TEXTS_FULL_ES = {
    "Filter A - Basic Bottle Microfilter": "AQUASHIELD - Filtro A (Completo)\n\nPropósito: Filtro por gravedad de bajo costo... (texto completo)...",
    "Filter B - Bottle-Neck Cartridge Filter": "AQUASHIELD - Filtro B (Completo)\n\n... (texto completo).",
    "Filter C - Gravity Bucket Filter": "AQUASHIELD - Filtro C (Completo)\n\n... (texto completo).",
    "Filter D - Family Bucket Filter": "AQUASHIELD - Filtro D (Completo)\n\n... (texto completo).",
    "Filter E - Clay-Sawdust Ceramic Filter": "AQUASHIELD - Filtro E (Completo)\n\n... (texto completo).",
    "Filter F - Cloth Emergency Filter": "AQUASHIELD - Filtro F (Completo)\n\n... (texto completo).",
    "Filter G - SODIS Solar Disinfection": "AQUASHIELD - Filtro G (Completo)\n\n... (texto completo).",
    "Filter H - Crisis-Zone 3-Tier Method": "AQUASHIELD - Filtro H (Completo)\n\n... (texto completo).",
}

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.header("Print + QR Options")
lang = st.sidebar.selectbox("Language / Idioma", ("English", "Español"))
format_choice = st.sidebar.selectbox("Card format", ("Text-only A5", "Image+Text A5"))
print_layout = st.sidebar.selectbox("Print sheet layout", ("Single A5", "Two-up A5 per A4", "Four-up A6 per A4"))
st.sidebar.markdown("---")
st.sidebar.info("QR codes embed the short instruction text (language-aware). Image+Text uses a programmatic PNG schematic.")

# -------------------------
# Per-filter UI
# -------------------------
st.header("Generate Cards and Print Sheets")
col1, col2 = st.columns([1, 3])
with col1:
    selected = st.selectbox("Select filter", FILTER_KEYS)
    preview_only = st.checkbox("Preview only (no ZIP)", value=False)
with col2:
    st.write("Preview below. Download single cards or create print-ready ZIP of all cards/layouts.")

# Get texts
def get_texts(key, lang):
    if lang == "English":
        short = FILTER_TEXTS_SHORT_EN.get(key, "")
        full = FILTER_TEXTS_FULL_EN.get(key, "")
    else:
        short = FILTER_TEXTS_SHORT_ES.get(key, "")
        full = FILTER_TEXTS_FULL_ES.get(key, "")
    return short, full

short_text, full_text = get_texts(selected, lang)

st.subheader(f"Preview — {selected} ({lang})")
st.markdown("**Short (preview):**")
st.text(short_text)
st.markdown("**Full (preview):**")
st.text(full_text)

# Build QR payload (short text)
qr_payload = short_text.strip()

# Single-card downloads
st.markdown("### Download single card (selected filter)")
if format_choice == "Text-only A5":
    buf_short = build_a5_pdf_text_only(short_text)
    buf_full = build_a5_pdf_text_only(full_text)
    st.download_button("⬇ Download SHORT A5 (text-only)", data=buf_short.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_SHORT_{lang}.pdf", mime="application/pdf")
    st.download_button("⬇ Download FULL A5 (text-only)", data=buf_full.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_FULL_{lang}.pdf", mime="application/pdf")
else:
    # create composite PNG for card including QR and schematic
    card_png = compose_card_image(selected, short_text if lang=="English" else short_text, include_schematic=True, qr_payload=qr_payload)
    buf_short_img = build_a5_pdf_with_image = None  # we'll create with helper below
    # for convenience, produce A5 PDF with image + text
    buf_short_img = build_a5_pdf_with_image_func(short_text if lang=="English" else short_text, card_png) if 'build_a5_pdf_with_image_func' in globals() else None

        # Since we didn't yet define build_a5_pdf_with_image_func inside this script, let's use existing helper:
    def build_a5_pdf_with_image_local(text, png_bytes):
        # Similar to earlier: place image at top and text below
        safe = sanitize_for_pdf(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpimg:
            tmpimg.write(png_bytes)
            tmpimg.flush()
            img_path = tmpimg.name
        try:
            pdf = FPDF(format='A5')
            pdf.add_page()
            margin = 10
            page_w = pdf.w - 2 * margin
            pdf.image(img_path, x=margin, y=margin, w=page_w)
            pdf.ln(5)
            pdf.set_font("Arial", size=11)
            pdf.set_left_margin(margin)
            pdf.set_right_margin(margin)
            pdf.multi_cell(0, 6, safe)
            out = pdf.output(dest="S").encode("latin-1")
            return io.BytesIO(out)
        finally:
            try:
                os.remove(img_path)
            except:
                pass

    buf_short_img = build_a5_pdf_with_image_local(short_text if lang=="English" else short_text, card_png)
    buf_full_img = build_a5_pdf_with_image_local(full_text if lang=="English" else full_text, card_png)

    st.download_button("⬇ Download SHORT A5 (image+text)", data=buf_short_img.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_SHORT_IMG_{lang}.pdf", mime="application/pdf")
    st.download_button("⬇ Download FULL A5 (image+text)", data=buf_full_img.getvalue(),
                       file_name=f"{selected.replace(' ', '_')}_FULL_IMG_{lang}.pdf", mime="application/pdf")

# Bulk ZIP creation: all cards in selected format and layout
st.markdown("---")
st.markdown("### Create ZIP for all filters (selected language & format)")

if st.button("Create ZIP for all cards"):
    with st.spinner("Generating cards and packaging ZIP..."):
        zipbuf = io.BytesIO()
        with zipfile.ZipFile(zipbuf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            # create single card PDFs and also compose print-sheet PDFs
            single_short_bufs = []
            single_full_bufs = []
            # also create PNG card images for layouts
            png_cards_for_layout = []
            for key in FILTER_KEYS:
                s_text, f_text = get_texts(key, lang)
                # QR content is short text
                qr_payload_local = s_text.strip()
                if format_choice == "Text-only A5":
                    s_buf = build_a5_pdf_text_only(s_text)
                    f_buf = build_a5_pdf_text_only(f_text)
                else:
                    png_card = compose_card_image(key, s_text, include_schematic=True, qr_payload=qr_payload_local)
                    # produce A5 PDF with image+text
                    s_buf = build_a5_pdf_with_image_local(s_text, png_card)
                    f_buf = build_a5_pdf_with_image_local(f_text, png_card)
                    png_cards_for_layout.append(png_card)
                # write single PDFs into zip
                z.writestr(f"{key.replace(' ', '_')}_SHORT_{lang}.pdf", s_buf.getvalue())
                z.writestr(f"{key.replace(' ', '_')}_FULL_{lang}.pdf", f_buf.getvalue())
                single_short_bufs.append(s_buf)
                single_full_bufs.append(f_buf)

            # Now produce print layouts: two-up A5 and four-up A6 if requested
            # Generate PNG images for each card if not already (for text-only we need to create simple PNG from PDF; easier: create PNG from compose_card_image using include_schematic=False)
            if format_choice == "Text-only A5":
                png_cards_for_layout = []
                for key in FILTER_KEYS:
                    s_text, _ = get_texts(key, lang)
                    png = compose_card_image(key, s_text, include_schematic=False, qr_payload=s_text.strip(), card_size=(1200,900))
                    png_cards_for_layout.append(png)

            # Build two-up A5 per A4 PDF
            two_up_pdf = build_a4_two_up_a5(png_cards_for_layout)
            z.writestr(f"AquaShield_two_up_A5_{lang}.pdf", two_up_pdf.getvalue())

            # Build four-up A6 per A4 PDF
            four_up_pdf = build_a4_four_up_a6(png_cards_for_layout)
            z.writestr(f"AquaShield_four_up_A6_{lang}.pdf", four_up_pdf.getvalue())

        zipbuf.seek(0)
        st.download_button("⬇ Download ZIP (all cards + print sheets)", data=zipbuf.getvalue(),
                           file_name=f"AquaShield_All_Cards_{format_choice}_{lang}.zip", mime="application/zip")
    st.success("ZIP ready for download.")

st.caption("Notes: QR codes encode the short instruction text for quick access. Two-up A5 and four-up A6 sheets are print-ready. If you want different margins, bleed, or crop marks for a specific printer, tell me which offset and I will add them.")

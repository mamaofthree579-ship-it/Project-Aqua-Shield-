import streamlit as st
import segno
import base64
import io

st.set_page_config(
    page_title="Project Aqua Shield — Offline QR Generator",
    layout="wide"
)

st.title("🔷 Project Aqua Shield — Offline QR Generator")
st.write("Each QR contains full EN/ES instructions inside the QR code (no internet required).")

# -------------------------------------------------------------------
# OFFLINE PAYLOADS (English + Spanish)
# -------------------------------------------------------------------

qr_payloads = {
    "Basic Gravity Micro-Bio Sand + Charcoal Filter": """AQUA SHIELD v1.0
BASIC GRAVITY SAND + CHARCOAL FILTER
EN: Cloth on bottle mouth → gravel → sand → charcoal. Discard first 1L. Pour slowly. Always disinfect after filtering: boil 1 min OR SODIS 6 hrs sun OR 1 drop bleach per cup (if unscented).
ES: Tela en la boca → grava → arena → carbón. Desechar 1L inicial. Verter despacio. Desinfectar: hervir 1 min, o SODIS 6 h sol, o 1 gota de cloro por taza.
""",

    "Ceramic Clay–Sawdust Emergency Filter": """AQUA SHIELD v1.0
CERAMIC CLAY FILTER
EN: Mix clay + sawdust 3:1. Shape bowl. Dry 2–3 days. Fire until hard (kiln or barrel). Optional: coat inside with silver. Pour water in top; collect clean water below.
ES: Mezclar arcilla + aserrín 3:1. Formar cuenco. Secar 2–3 días. Cocer. Opcional: plata coloidal. Verter agua arriba; recoger agua limpia abajo.
""",

    "Cloth-Only Emergency Filter": """AQUA SHIELD v1.0
CLOTH EMERGENCY FILTER
EN: Fold clean cloth 4–8 layers. Pour water slowly. Repeat 2–3×. Must disinfect afterward.
ES: Doblar tela limpia 4–8 capas. Verter agua. Repetir 2–3×. Debe desinfectarse después.
""",

    "Family Bucket Filter (Sand + Charcoal)": """AQUA SHIELD v1.0
BUCKET FILTER
EN: Bucket → cloth → coarse gravel → small gravel → charcoal (5–8 cm) → sand (15–25 cm) → cloth bottom. First 2L discard. Then filter. Disinfect afterward.
ES: Cubeta → tela → grava gruesa → grava fina → carbón 5–8 cm → arena 15–25 cm → tela abajo. Desechar 2L inicial. Luego filtrar. Desinfectar después.
""",

    "Solar Disinfection (SODIS)": """AQUA SHIELD v1.0
SOLAR DISINFECTION (SODIS)
EN: Use clear PET bottle. Filter water until clear. Fill 3/4; shake 20 sec. Fill full. Leave in sun 6 hrs (full sun) or 2 days (cloudy).
ES: Botella PET clara. Filtrar hasta clara. Llenar 3/4; agitar 20 seg. Llenar. Sol 6 h (sol pleno) o 2 días (nublado).
""",

    "Crisis-Zone 3-Tier Method": """AQUA SHIELD v1.0
CRISIS-ZONE 3-TIER WATER SAFETY
EN: Tier1 settle 6–12h → cloth filter. Tier2 sand+charcoal filter if possible. Tier3 disinfect (boil, SODIS, or bleach). Avoid water smelling like fuel.
ES: Nivel1 decantar 6–12h → filtrar tela. Nivel2 arena+carbón si posible. Nivel3 desinfectar. Evitar agua con olor a combustible.
""",

    "Full Guidebook Summary": """AQUA SHIELD v1.0
SUMMARY
EN: Multi-layer safety: settle → filter → disinfect. Do not rely on filtering alone for sewage-contaminated water.
ES: Seguridad por capas: decantar → filtrar → desinfectar. No confiar solo en filtrado para agua con aguas residuales.
""",

    "All Filters Index (Offline Text)": """AQUA SHIELD v1.0
INDEX
"Basic Gravity Micro-Bio Sand + Charcoal Filter": """AQUA SHIELD v1.0
BASIC GRAVITY SAND + CHARCOAL FILTER
EN: Cloth on bottle mouth → gravel → sand → charcoal. Discard first 1L. Pour slowly. Always disinfect after filtering: boil 1 min OR SODIS 6 hrs sun OR 1 drop bleach per cup (if unscented).
ES: Tela en la boca → grava → arena → carbón. Desechar 1L inicial. Verter despacio. Desinfectar: hervir 1 min, o SODIS 6 h sol, o 1 gota de cloro por taza.
"Ceramic Clay–Sawdust Emergency Filter": """AQUA SHIELD v1.0
CERAMIC CLAY FILTER
EN: Mix clay + sawdust 3:1. Shape bowl. Dry 2–3 days. Fire until hard (kiln or barrel). Optional: coat inside with silver. Pour water in top; collect clean water below.
ES: Mezclar arcilla + aserrín 3:1. Formar cuenco. Secar 2–3 días. Cocer. Opcional: plata coloidal. Verter agua arriba; recoger agua limpia abajo.
"Cloth-Only Emergency Filter": """AQUA SHIELD v1.0
CLOTH EMERGENCY FILTER
EN: Fold clean cloth 4–8 layers. Pour water slowly. Repeat 2–3×. Must disinfect afterward.
ES: Doblar tela limpia 4–8 capas. Verter agua. Repetir 2–3×. Debe desinfectarse después.
"Family Bucket Filter (Sand + Charcoal)": """AQUA SHIELD v1.0
BUCKET FILTER
EN: Bucket → cloth → coarse gravel → small gravel → charcoal (5–8 cm) → sand (15–25 cm) → cloth bottom. First 2L discard. Then filter. Disinfect afterward.
ES: Cubeta → tela → grava gruesa → grava fina → carbón 5–8 cm → arena 15–25 cm → tela abajo. Desechar 2L inicial. Luego filtrar. Desinfectar después.
"Solar Disinfection (SODIS)": """AQUA SHIELD v1.0
SOLAR DISINFECTION (SODIS)
EN: Use clear PET bottle. Filter water until clear. Fill 3/4; shake 20 sec. Fill full. Leave in sun 6 hrs (full sun) or 2 days (cloudy).
ES: Botella PET clara. Filtrar hasta clara. Llenar 3/4; agitar 20 seg. Llenar. Sol 6 h (sol pleno) o 2 días (nublado).
"Crisis-Zone 3-Tier Method": """AQUA SHIELD v1.0
CRISIS-ZONE 3-TIER WATER SAFETY
EN: Tier1 settle 6–12h → cloth filter. Tier2 sand+charcoal filter if possible. Tier3 disinfect (boil, SODIS, or bleach). Avoid water smelling like fuel.
ES: Nivel1 decantar 6–12h → filtrar tela. Nivel2 arena+carbón si posible. Nivel3 desinfectar. Evitar agua con olor a combustible.
"Full Guidebook Summary": """AQUA SHIELD v1.0
SUMMARY
EN: Multi-layer safety: settle → filter → disinfect. Do not rely on filtering alone for sewage-contaminated water.
ES: Seguridad por capas: decantar → filtrar → desinfectar. No confiar solo en filtrado para agua con aguas residuales.
""",
}

# -------------------------------------------------------------------
# QR GENERATION + DISPLAY
# -------------------------------------------------------------------

def generate_qr(data: str):
    """Generate QR with Segno."""
    return segno.make(data, error="M")

st.subheader("QR Codes")

for name, payload in qr_payloads.items():

    st.markdown(f"### {name}")

    qr = generate_qr(payload)

    # --- PNG ---
    png_buf = io.BytesIO()
    qr.save(png_buf, scale=10, border=2, kind="png")
    png_buf.seek(0)
    png_b64 = base64.b64encode(png_buf.getvalue()).decode()

    st.image(f"data:image/png;base64,{png_b64}", width=240)

    # --- SVG ---
    svg_buf = io.BytesIO()
    qr.save(svg_buf, scale=4, border=2, kind="svg")
    svg_buf.seek(0)

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇ Download PNG",
            data=png_buf.getvalue(),
            file_name=f"{name.replace(' ', '_').lower()}.png",
            mime="image/png"
        )

    with col2:
        st.download_button(
            "⬇ Download SVG",
            data=svg_buf.getvalue(),
            file_name=f"{name.replace(' ', '_').lower()}.svg",
            mime="image/svg+xml"
        )

    # Optional: show SVG text
    with st.expander("View SVG Code"):
        st.code(svg_buf.getvalue().decode(), language="xml")

    st.markdown("---")

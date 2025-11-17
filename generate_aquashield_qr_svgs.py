import streamlit as st
import segno
import base64
import io

st.set_page_config(
    page_title="AquaShield QR Library",
    layout="centered",
)

# -------------------------------------------------------------
# QR RENDERING UTILITIES
# -------------------------------------------------------------

def to_svg_base64(qr_obj, scale=4, border=4):
    """Convert Segno QR object into Base64-encoded SVG."""
    svg = qr_obj.svg_inline(scale=scale, border=border)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}", svg

def create_qr(payload):
    """Create a QR code object from text payload."""
    return segno.make(payload, error="M")


# -------------------------------------------------------------
# PAYLOADS — 8 AquaShield Instructions (EN + ES)
# -------------------------------------------------------------

QR_PAYLOADS = {
    "Bottle Filter": """AQUASHIELD v1.0
BOTTLE FILTER (EN/ES)

EN:
Cloth on bottle mouth. Add gravel, sand, charcoal. Discard first 1L.
Pour slowly. Always disinfect after: boil, SODIS, chlorine.

ES:
Tela en la boca. Agrega grava, arena, carbón. Desecha 1L inicial.
Verter despacio. Desinfecta siempre: hervir, SODIS o cloro.
""",

    "Cloth Filter": """AQUASHIELD v1.0
CLOTH FILTER (EN/ES)

EN:
Fold clean cloth 4–8 layers. Filter twice. Must disinfect after: boil, SODIS, chlorine.

ES:
Dobla tela 4–8 capas. Filtra dos veces. Debes desinfectar: hervir, SODIS o cloro.
""",

    "Bucket Filter": """AQUASHIELD v1.0
BUCKET FILTER (EN/ES)

EN:
Layers top→bottom: cloth, gravel, fine gravel, charcoal, sand, cloth.
Let drip into clean bucket. Disinfect after.

ES:
Capas arriba→abajo: tela, grava, grava fina, carbón, arena, tela.
Dejar gotear. Desinfectar después.
""",

    "Ceramic Filter": """AQUASHIELD v1.0
CERAMIC FILTER (EN/ES)

EN:
Clay + fine sawdust 3:1. Shape. Dry 2–3 days. Fire. Filters microbes, not chemicals.

ES:
Arcilla + aserrín 3:1. Moldea. Seca 2–3 días. Cuece. Filtra microbios, no químicos.
""",

    "SODIS": """AQUASHIELD v1.0
SOLAR DISINFECTION (EN/ES)

EN:
Clear PET bottle. Shake 20 sec. Leave in sun 6 hrs (cloudy: 2 days).
Kills microbes, not chemicals.

ES:
Botella PET clara. Agita 20 seg. Sol 6 hrs (nublado: 2 días).
Mata microbios, no químicos.
""",

    "3-Tier Method": """AQUASHIELD v1.0
3-TIER SAFE WATER METHOD (EN/ES)

EN:
1) Settle 6–12h + cloth.
2) Sand + charcoal filter.
3) Disinfect (boil / SODIS / chlorine).

ES:
1) Reposar 6–12h + tela.
2) Arena + carbón.
3) Desinfectar (hervir / SODIS / cloro).
""",

    "Safe Water Rules": """AQUASHIELD v1.0
HOUSEHOLD SAFE WATER RULES (EN/ES)

EN:
Use clean containers with lids. Don’t touch inside. Always filter + disinfect.
If water smells like fuel or chemicals DO NOT use.

ES:
Usa envases limpios con tapa. No toques adentro. Filtrar + desinfectar siempre.
Si huele a combustible o químicos NO usar.
""",

    "Emergency Fast": """AQUASHIELD v1.0
EMERGENCY FAST WATER METHOD (EN/ES)

EN:
Cloth filter → SODIS 6 hrs. If very turbid: settle 6–12h. Do NOT drink water that smells like fuel.

ES:
Tela → SODIS 6 hrs. Si está turbia: reposar 6–12h. No beber agua con olor a combustible.
"""
}


# -------------------------------------------------------------
# STREAMLIT APP UI
# -------------------------------------------------------------

st.title("🌍 AquaShield — QR Instruction Library")
st.write("Eight crisis-zone safe-water methods in QR format.\nAll instructions are bilingual (EN/ES).")

for name, payload in QR_PAYLOADS.items():
    st.markdown("---")
    st.subheader(name)

    qr = create_qr(payload)

# Generate PNG in-memory
png_buffer = io.BytesIO()
qr.save(png_buffer, kind="png", scale=8, border=4)
png_buffer.seek(0)

# Generate SVG in-memory
svg_buffer = io.BytesIO()
qr.save(svg_buffer, kind="svg", scale=8, border=4)
svg_buffer.seek(0)

# Convert PNG to base64 for display
png_base64 = base64.b64encode(png_buffer.getvalue()).decode()
png_data_url = f"data:image/png;base64,{png_base64}"

# Show the QR visually
st.image(png_data_url, width=250)

# Download buttons
col1, col2 = st.columns(2)

with col1:
    st.download_button(
        label="⬇ Download PNG",
        data=png_buffer.getvalue(),
        file_name=f"{name.replace(' ','_')}.png",
        mime="image/png",
    )

with col2:
    st.download_button(
        label="⬇ Download SVG",
        data=svg_buffer.getvalue(),
        file_name=f"{name.replace(' ','_')}.svg",
        mime="image/svg+xml",
    )

# Optional: show SVG code in an expander
with st.expander("View SVG Code"):
    st.code(svg_buffer.getvalue().decode(), language="xml")

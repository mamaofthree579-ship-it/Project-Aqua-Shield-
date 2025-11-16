import streamlit as st
import segno

st.title("AquaShield QR Library")

# Your QR data
payloads = {
    "qr01_bottle": """AQUASHIELD v1.0,BOTTLE FILTER (EN/ES), EN: Cloth on bottle mouth. Add gravel, sand, charcoal. Discard first 1L. Pour slow. Always disinfect after: boil, SODIS, or chlorine., ES: Tela en la boca. Agrega grava, arena, carbón. Desecha 1L inicial. Verter despacio. Desinfecta siempre: hervir, SODIS o cloro.""",
    "qr02_cloth": """AQUASHIELD v1.0
CLOTH FILTER (EN/ES)

EN:
Fold clean cloth 4–8 layers. Filter twice. Must disinfect after: boil, SODIS, chlorine.

ES:
Dobla tela 4–8 capas. Filtra dos veces. Debes desinfectar: hervir, SODIS o cloro.
""",

    "qr03_bucket": """AQUASHIELD v1.0
BUCKET FILTER (EN/ES)

EN:
Layers top→bottom: cloth, gravel, fine gravel, charcoal, sand, cloth. Let drip into clean bucket. Disinfect after.

ES:
Capas arriba→abajo: tela, grava, grava fina, carbón, arena, tela. Dejar gotear. Desinfectar después.
""",

    "qr04_ceramic": """AQUASHIELD v1.0
CERAMIC FILTER (EN/ES)

EN:
Clay+fine sawdust 3:1. Shape. Dry 2–3 days. Fire to harden. Filters microbes, not chemicals. Disinfect water after.

ES:
Arcilla+aserrín 3:1. Moldea. Seca 2–3 días. Cuece. Filtra microbios, no químicos. Desinfecta el agua después.
""",

    "qr05_sodis": """AQUASHIELD v1.0
SODIS (EN/ES)

EN:
Clear PET bottle. Shake 20 sec. Sun 6 hrs (cloudy: 2 days). Kills microbes, not chemicals.

ES:
Botella PET clara. Agita 20 seg. Sol 6 hrs (nublado: 2 días). Mata microbios, no químicos.
""",

    "qr06_3tier": """AQUASHIELD v1.0
3-TIER METHOD (EN/ES)

EN:
1) Settle 6–12h + cloth.
2) Sand+charcoal filter.
3) Disinfect (boil/SODIS/chlorine).
Do NOT use water smelling like fuel/chemicals.

ES:
1) Reposar 6–12h + tela.
2) Arena+carbón.
3) Desinfectar (hervir/SODIS/cloro).
NO usar agua con olor a combustible/químicos.
""",

    "qr07_safe_rules": """AQUASHIELD v1.0
SAFE WATER (EN/ES)

EN:
Use clean containers with lids. Don’t touch inside. Filter+disinfect always. If water smells like fuel, chemicals, or sewage, DO NOT use.

ES:
Usa envases limpios con tapa. No tocar adentro. Filtrar+desinfectar siempre. Si huele a combustible, químicos o aguas negras, NO usar.
""",

    "qr08_emergency_fast": """AQUASHIELD v1.0
EMERGENCY WATER (EN/ES)

EN:
Fast method: Cloth filter → SODIS 6 hrs → Use. If water dark, let settle 6–12h. Don’t drink water that smells like fuel.

ES:
Método rápido: Tela → SODIS 6 hrs → Usar. Si el agua está turbia, reposar 6–12h. No beber agua con olor a combustible.
"""
}

for name, text in payloads.items():
    qr = segno.make(text, error="M")
    
    # Convert QR → inline SVG text
    svg = qr.svg_inline(scale=8, border=4)
    
    # Streamlit can render SVG via markdown (unsafe allows raw SVG)
    st.subheader(name)
    st.markdown(svg, unsafe_allow_html=True)

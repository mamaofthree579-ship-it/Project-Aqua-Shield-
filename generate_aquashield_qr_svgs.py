import streamlit as st
import segno

# Your QR data
payloads = {
    "Bottle Filter": "AQUASHIELD v1.0\nBottle filter instructions...",
    "Cloth Filter": "AQUASHIELD v1.0\nCloth filter instructions...",
    "Bucket Filter": "AQUASHIELD v1.0\nBucket filter instructions...",
    # add all 8 as needed...
}

st.title("AquaShield QR Library")

for name, text in payloads.items():
    qr = segno.make(text, error="M")
    
    # Convert QR → inline SVG text
    svg = qr.svg_inline(scale=8, border=4)
    
    # Streamlit can render SVG via markdown (unsafe allows raw SVG)
    st.subheader(name)
    st.markdown(svg, unsafe_allow_html=True)
    

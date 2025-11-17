import streamlit as st
import segno
import base64
import io

st.set_page_config(page_title="Project Aqua Shield — QR Generator", layout="wide")

st.title("🔷 Project Aqua Shield — QR Card Generator")
st.write("Generates QR codes pointing to filter instructions or downloadable resources.")

# -------------------------------------------------------------------
# QR LIST — REPLACE URLS WITH YOUR FINAL LINKS WHEN READY
# -------------------------------------------------------------------

qr_targets = {
    "Basic Gravity Micro-Bio Sand + Charcoal Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/basic_gravity_filter.md",
    "Ceramic Emergency Clay Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/ceramic_filter.md",
    "Cloth-Only Emergency Filter": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/cloth_filter.md",
    "Family Bucket Filter (Sand + Charcoal)": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/family_bucket_filter.md",
    "Solar Disinfection (SODIS)": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/filters/sodis.md",
    "Crisis-Zone 3-Tier Water Safety Method": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation/english/crisis_zone_filter_set.md",
    "All Files / Downloads Index": "https://github.com/mamaofthree579-ship-it/Project-Aqua-Shield-/tree/main/documentation"
}

# -------------------------------------------------------------------
# QR CODE FUNCTION
# -------------------------------------------------------------------

def generate_qr(url: str):
    """Create QR using Segno."""
    return segno.make(url, micro=False, error="M")

# -------------------------------------------------------------------
# QR RENDERING LOOP
# -------------------------------------------------------------------

st.subheader("QR Codes")

for name, url in qr_targets.items():
    st.markdown(f"### {name}")

    # Create QR
    qr = generate_qr(url)

    # --- PNG buffer ---
    png_buffer = io.BytesIO()
    qr.save(png_buffer, kind="png", scale=10, border=2)
    png_buffer.seek(0)

    # Base64 PNG for display
    png_base64 = base64.b64encode(png_buffer.getvalue()).decode()
    png_data_url = f"data:image/png;base64,{png_base64}"

    # Display QR image visually
    st.image(png_data_url, width=240)

    # --- SVG buffer ---
    svg_buffer = io.BytesIO()
    qr.save(svg_buffer, kind="svg", scale=4, border=2)
    svg_buffer.seek(0)
    svg_text = svg_buffer.getvalue()

    # Download buttons
    c1, c2 = st.columns(2)

    with c1:
        st.download_button(
            label="⬇ Download PNG",
            data=png_buffer.getvalue(),
            file_name=f"{name.replace(' ', '_').lower()}.png",
            mime="image/png"
        )

    with c2:
        st.download_button(
            label="⬇ Download SVG",
            data=svg_text,
            file_name=f"{name.replace(' ', '_').lower()}.svg",
            mime="image/svg+xml"
        )

    # Optional: view SVG text
    with st.expander("View SVG Code"):
        st.code(svg_text.decode(), language="xml")

    st.markdown("---")

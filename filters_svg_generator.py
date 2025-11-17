import streamlit as st

st.set_page_config(page_title="AquaShield Filters", layout="centered")

st.title("🌊 AquaShield — Low-Cost Water Filter Designs")
st.write("All diagrams below are self-contained SVGs and downloadable.")

# --------------------------
# FILTER A — Activated Charcoal Sock
# --------------------------
filter_a = r'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="800" height="240" viewBox="0 0 800 240">
  <style>
    .label { font: 18px sans-serif; }
    .small { font: 14px sans-serif; }
    .box { fill:none; stroke:#000; stroke-width:2; }
  </style>

  <text x="16" y="28" class="label">Activated Charcoal Sock Filter</text>

  <rect x="16" y="60" width="96" height="40" class="box"/>
  <text x="28" y="86" class="small">Tap</text>
  <line x1="112" y1="80" x2="200" y2="80" stroke="#000" stroke-width="2"/>

  <rect x="200" y="40" width="240" height="120" class="box"/>
  <text x="208" y="60" class="small">Cloth prefilter</text>
  <line x1="200" y1="80" x2="440" y2="80" stroke="#000" stroke-width="2"/>
  <text x="260" y="110" class="small">Packed Charcoal</text>

  <line x1="440" y1="100" x2="520" y2="100" stroke="#000" stroke-width="2"/>
  <rect x="520" y="80" width="120" height="60" class="box"/>
  <text x="540" y="115" class="small">Clean cup</text>
</svg>
'''

# --------------------------
# FILTER C — PVC Mini Pressure Charcoal
# --------------------------
filter_c = r'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="900" height="200" viewBox="0 0 900 200">
  <style>
    .label { font: 18px sans-serif; }
    .small { font: 14px sans-serif; }
    .box { fill:none; stroke:#000; stroke-width:2; }
  </style>

  <text x="16" y="26" class="label">PVC Mini Pressure Charcoal Filter</text>

  <rect x="16" y="70" width="50" height="50" class="box"/>
  <text x="22" y="100" class="small">Inlet</text>
  <line x1="66" y1="95" x2="150" y2="95" stroke="#000" stroke-width="2"/>

  <rect x="150" y="40" width="560" height="110" class="box"/>
  <text x="170" y="60" class="small">PVC tube</text>
  <text x="230" y="95" class="small">Cloth → Charcoal → Cloth</text>

  <line x1="710" y1="95" x2="795" y2="95" stroke="#000" stroke-width="2"/>

  <rect x="795" y="70" width="80" height="60" class="box"/>
  <text x="810" y="105" class="small">Cup</text>
</svg>
'''

# --------------------------
# FILTER D — Ceramic Disk Filter
# --------------------------
filter_d = r'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="700" height="260" viewBox="0 0 700 260">
  <style>
    .label { font: 18px sans-serif; }
    .small { font: 14px sans-serif; }
    .box { fill:none; stroke:#000; stroke-width:2; }
  </style>

  <text x="16" y="28" class="label">Silver-Coated Ceramic Disk Filter</text>

  <text x="180" y="70" class="small">Dirty Water →</text>

  <ellipse cx="350" cy="130" rx="160" ry="55"
           fill="none" stroke="#000" stroke-width="2"/>
  <text x="280" y="135" class="small">Porous Ceramic Disk</text>

  <line x1="350" y1="185" x2="350" y2="235" stroke="#000" stroke-width="2"/>
  <rect x="310" y="235" width="80" height="40" class="box"/>
  <text x="318" y="260" class="small">Clean cup</text>
</svg>
'''

# --------------------------
# FILTER E — Magnet Prefilter
# --------------------------
filter_e = r'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="820" height="240" viewBox="0 0 820 240">
  <style>
    .label { font: 18px sans-serif; }
    .small { font: 14px sans-serif; }
    .box { fill:none; stroke:#000; stroke-width:2; }
  </style>

  <text x="16" y="28" class="label">Zero-Rust Magnet Pre-Filter</text>

  <line x1="20" y1="130" x2="110" y2="130"
        stroke="#000" stroke-width="2"/>
  <text x="20" y="118" class="small">Tap</text>

  <rect x="110" y="80" width="520" height="100" class="box"/>
  <text x="130" y="75" class="small">Plastic Chamber (Slows water)</text>

  <circle cx="260" cy="130" r="18" fill="#000"/>
  <text x="285" y="135" class="small">Magnet traps rust</text>

  <line x1="630" y1="130" x2="720" y2="130"
        stroke="#000" stroke-width="2"/>
  <rect x="720" y="105" width="80" height="60" class="box"/>
  <text x="732" y="140" class="small">Cup</text>
</svg>
'''

### Display all filters
filters = [
    ("Filter A — Activated Charcoal Sock", filter_a),
    ("Filter C — PVC Mini Charcoal Filter", filter_c),
    ("Filter D — Ceramic Disk Filter", filter_d),
    ("Filter E — Magnet Pre-Filter", filter_e)
]

for name, svg_code in filters:
    st.subheader(name)
    st.image(svg_code.encode(), format="svg")
    st.download_button(
        label="⬇ Download SVG",
        data=svg_code,
        file_name=name.replace(" ", "_") + ".svg",
        mime="image/svg+xml"
    )
    st.divider()

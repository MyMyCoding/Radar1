import streamlit as st
import streamlit.components.v1 as components
import py3Dmol
import pandas as pd

st.set_page_config(layout="wide")
st.title("EGFR-Aptamer Interaction Dashboard")

# 3D Viewer Section
st.subheader("1. EGFR Protein Structure")
pdb_id = "1M17"  # You can change this later
def render_pdb(pdb_id="1M17"):
    view = py3Dmol.view(query=f"pdb:{pdb_id}")
    view.setStyle({'cartoon': {'color': 'spectrum'}})
    view.zoomTo()
    return view

st.subheader("1. EGFR Protein Structure Viewer")

# Get the view and render it as HTML
viewer = render_pdb()
components.html(viewer._make_html(), height=500)

# Aptamer Upload
st.subheader("2. Upload Aptamer Sequence (FASTA)")
aptamer_file = st.file_uploader("Upload Aptamer", type=["txt", "fasta"])
if aptamer_file:
    aptamer_seq = aptamer_file.read().decode("utf-8")
    st.text_area("Aptamer Sequence:", aptamer_seq)

# Simulate Docking & Interaction
st.subheader("3. Simulated Docking & Interaction")
if st.button("Run Docking (Simulated)"):
    st.success("Docking Complete. Showing mock interaction results.")
    df = pd.read_csv("mock_results/aptamer_interactions.csv")
    st.dataframe(df)

    best = df.sort_values("Num_Bonds", ascending=False).iloc[0]
    st.info(f"Top Aptamer: {best['Aptamer']} with {best['Num_Bonds']} bonds.")

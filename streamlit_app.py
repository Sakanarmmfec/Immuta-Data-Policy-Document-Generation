import streamlit as st

st.set_page_config(
    page_title="Immuta x MFEC Helper",
    page_icon="📋",
    layout="wide"
)

st.title("Immuta x MFEC Helper")
st.markdown("Welcome to the Immuta Rule Configuration Helper")

st.info("👈 Please select a page from the sidebar to get started")

with st.expander("📋 Available Tools"):
    st.markdown("""
    **Document Generation**: Upload YAML files to generate professional explanations
    """)

st.markdown("---")
st.markdown("Built with ❤️ by MFEC for Immuta | Immuta x MFEC Helper")
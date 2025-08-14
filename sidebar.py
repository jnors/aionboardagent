import json
import streamlit as st

def render_sidebar():
    st.sidebar.title("🗂 Embedded Files")
    try:
        with open("data/embedding_metadata.json", "r") as f:
            meta = json.load(f)
        st.sidebar.markdown(f"**Last embedded:** `{meta.get('timestamp','—')}`")
        st.sidebar.markdown(f"**Total chunks:** `{meta.get('count','0')}`")
        st.sidebar.markdown("**Files:**")
        for file in meta.get("files", []):
            st.sidebar.markdown(f"📄 {file}")
    except FileNotFoundError:
        st.sidebar.warning("No embedding metadata found. Run `load_docs.py` first.")


import streamlit as st

def inject_global_styles():
    st.markdown("""
<style>
  :root { --top-gap: 36px; }  /* tweak 24–36px if needed */

  /* Ensure the first heading isn't clipped by the page's top edge */
  .block-container { 
    padding-top: var(--top-gap) !important; 
    overflow: visible !important;          /* belt-and-suspenders */
  }

  /* Normalize heading spacing so ascenders don't get cropped */
  h1, .stMarkdown h1 {
    margin-top: 0 !important;
    padding-top: 2px;       /* tiny nudge to reveal the top pixels */
    line-height: 1.15;      /* prevent tight line-height clipping */
  }
</style>
""", unsafe_allow_html=True)
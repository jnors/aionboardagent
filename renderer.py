import json
import streamlit as st
from streamlit.components.v1 import html as st_html
TABLE_CSS = """
<style>
.chat-html table { border-collapse: collapse; width: 100%; }
.chat-html th, .chat-html td { border: 1px solid #444; padding: 8px; }
.chat-html th { background: #222; color: #fff; }
.chat-html tr:nth-child(even) { background: #111; }
</style>
"""

def _normalize_answer(obj):
    """
    Coerce agent output to a displayable form.
    Returns (mode, payload) where mode in {"markdown", "html", "json"}.
    """
    if isinstance(obj, str):
        return ("markdown", obj)

    if isinstance(obj, dict):
        # Prefer common text keys
        for key in ("content", "answer", "text", "markdown", "message"):
            val = obj.get(key)
            if isinstance(val, str) and val.strip():
                return ("markdown", val)
        html_val = obj.get("html")
        if isinstance(html_val, str) and html_val.strip():
            return ("html", html_val)
        return ("json", obj)

    if isinstance(obj, list):
        if all(isinstance(x, str) for x in obj):
            return ("markdown", "\n\n".join(obj))
        return ("json", obj)

    return ("markdown", str(obj))

def render_message(content):
    """
    Robust renderer for assistant/user messages.
    Handles str/dict/list; supports markdown, HTML tables, and JSON pretty-print.
    """
    mode, payload = _normalize_answer(content)

    if mode == "json":
        st.code(json.dumps(payload, indent=2), language="json")
        return

    if mode == "html":
        st_html(TABLE_CSS + f'<div class="chat-html">{payload}</div>', height=420, scrolling=True)
        return

    # mode == "markdown"
    c = (payload or "").strip()

    # If an HTML table sneaks inside markdown, render via HTML for fidelity
    lower_c = c.lower()
    if "<table" in lower_c and "</table>" in lower_c:
        st_html(TABLE_CSS + f'<div class="chat-html">{c}</div>', height=420, scrolling=True)
        return

    # Normalize HTML line breaks to Markdown breaks
    c = c.replace("<br />", "  \n").replace("<br/>", "  \n").replace("<br>", "  \n")

    # Help Streamlit parse markdown tables on first render
    if "|" in c and "---" in c:
        c = f"\n{c}\n"

    st.markdown(c, unsafe_allow_html=True)

import streamlit as st
from styles import inject_global_styles
from state import init_session_state, clear_chat
from sidebar import render_sidebar
from renderer import render_message
from chat_handler import handle_user_turn
from suggested_questions import render_suggested_questions_footer

st.set_page_config(page_title="AI Onboarding Agent", page_icon="🤖")
st.title("🤖 AI Onboarding Agent")

inject_global_styles()              # <- keep this ON (safe)
init_session_state()
render_sidebar()

if st.button("🧹 Clear Chat"):
    clear_chat()
    st.rerun()

# ---- Render history (ONCE) ----
for m in st.session_state.chat:
    with st.chat_message("user" if m["role"] == "user" else "assistant",
                         avatar="🧑" if m["role"] == "user" else "🤖"):
        render_message(m["content"])

# ---- Clear input BEFORE the widget is built ----
if st.session_state.get("clear_input"):
    st.session_state.chat_input = ""
    st.session_state.clear_input = False

# ---- Chat input ----
prompt = st.chat_input(placeholder="Ask a question...", key="chat_input")

# ---- Render footer NOW so button clicks happen in THIS run ----
render_suggested_questions_footer()

# ---- Submission logic (after footer may have set pending_prompt) ----
triggered = st.session_state.pending_prompt or prompt
st.session_state.pending_prompt = None

if triggered:
    handle_user_turn(triggered)
    st.session_state.clear_input = True
    st.rerun()


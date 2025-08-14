# app.py
import streamlit as st

from styles import inject_global_styles
from state import init_session_state, clear_chat
from sidebar import render_sidebar
from renderer import render_message
from chat_handler import handle_user_turn

# ---------------- Config ----------------
st.set_page_config(page_title="AI Onboarding Agent", page_icon="🤖")
st.title("🤖 AI Onboarding Agent")

inject_global_styles()
init_session_state()
render_sidebar()

# ---------------- Seed first message ----------------
# If there's no history yet, greet the user once.
if len(st.session_state.chat) == 0:
    st.session_state.chat.append({
        "role": "assistant",
        "content": "Hello! I am your AI Onboarding buddy! How can I help you today?"
    })

# ---------------- Clear Chat control ----------------
if st.button("🧹 Clear Chat"):
    clear_chat()
    st.rerun()

# ---------------- Suggested Questions ----------------
SUGGESTED_QUESTIONS = [
    "📅 What's the first week schedule?",
    "💻 How do I get my laptop set up?",
    "📡 What’s the company Wi-Fi info?",
    "📑 What are the company policies?",
    "🛠️ How do I get IT support?",
    "🎉 What benefits do I get?",
    "🏖️ How many vacation days do I have?",
]

def render_suggested_inline():
    """
    Inline panel shown ONCE, directly under the FIRST assistant message.
    Uses normal Streamlit widgets (no HTML hacks), so it won't jump around.
    Clicking a suggestion queues it via session_state.pending_prompt.
    """
    st.markdown("##### Suggested Questions")
    # Simple responsive grid (2 columns on wide, 1 on narrow).
    # Avoids any brittle CSS.
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"sq_{i}"):
                st.session_state.pending_prompt = q
                # Ask app to clear the text field BEFORE the widget is built next run
                st.session_state.clear_input = True

# ---------------- Chat History (render ONCE) ----------------
inserted_suggestions = False
for idx, m in enumerate(st.session_state.chat):
    with st.chat_message("user" if m["role"] == "user" else "assistant",
                         avatar="🧑" if m["role"] == "user" else "🤖"):
        render_message(m["content"])
    # Insert suggestions exactly once, right after the FIRST assistant turn
    if (not inserted_suggestions) and m["role"] == "assistant":
        render_suggested_inline()
        inserted_suggestions = True

# ---------------- Clear input BEFORE widget is instantiated ----------------
if st.session_state.get("clear_input"):
    st.session_state.chat_input = ""
    st.session_state.clear_input = False

# ---------------- Input AREA (bottom) ----------------
prompt = st.chat_input(placeholder="Ask a question...", key="chat_input")

# ---------------- Submission logic ----------------
# Read any click from the inline suggestions (set during this run),
# or the typed prompt from the chat input.
triggered = st.session_state.pending_prompt or prompt
st.session_state.pending_prompt = None  # consume queued suggestion

if triggered:
    handle_user_turn(triggered)
    # Defer clearing the input until BEFORE the next widget render
    st.session_state.clear_input = True
    st.rerun()

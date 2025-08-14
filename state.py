import streamlit as st

def init_session_state():
    defaults = {
        "chat": [],
        "chat_input": "",
        "pending_prompt": None,
        "clear_input": False
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def clear_chat():
    st.session_state.chat = []
    st.session_state.pending_prompt = None
    st.session_state.clear_input = True

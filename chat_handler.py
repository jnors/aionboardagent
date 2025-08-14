# chat_handler.py

import streamlit as st
from agents.guide_agent import ask_onboarding_agent
from renderer import render_message

def handle_user_turn(user_text: str):
    with st.chat_message("user", avatar="🧑"):
        render_message(user_text)
    st.session_state.chat.append({"role": "user", "content": user_text})

    # Assistant placeholder
    assistant_block = st.chat_message("assistant", avatar="🤖")
    placeholder = assistant_block.empty()
    with placeholder.container():
        render_message("🧠 *Thinking…*")

    # Call agent
    try:
        answer = ask_onboarding_agent(user_text)

    except Exception as e:
        # Updated, more general error handling
        err_str = str(e)
        if "429" in err_str:
            # This message will now only appear if BOTH services are rate-limited
            answer = {"error": "Both our primary and fallback AI services are currently busy. Please try again in a moment. 😴"}
        else:
            # A general message for other errors (e.g., API key invalid)
            st.error(f"An unexpected error occurred: {err_str}")
            answer = {"error": "Sorry, something went wrong while trying to get an answer. Please check the logs."}


    # Replace placeholder with final message
    placeholder.empty()
    with st.chat_message("assistant", avatar="🤖"):
        render_message(answer)
    st.session_state.chat.append({"role": "assistant", "content": answer})
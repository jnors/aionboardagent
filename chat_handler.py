import streamlit as st
from agents.guide_agent import ask_onboarding_agent  # returns a string or structured object
from renderer import render_message

# ---------- Message handling ----------

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
        if isinstance(answer, str) and "429" in answer:
            answer = "I'm tired for the day. You've used all your credits. See you tomorrow! 😴"
    except Exception as e:
        err = str(e)
        if "429" in err:
            answer = "I'm tired for the day. You've used all your credits. See you tomorrow! 😴"
        else:
            answer = {"error": err}

    # Replace placeholder with final message
    placeholder.empty()
    with st.chat_message("assistant", avatar="🤖"):
        render_message(answer)
    st.session_state.chat.append({"role": "assistant", "content": answer})


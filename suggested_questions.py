import streamlit as st

SUGGESTED_QUESTIONS = [
    "📅 What's the first week schedule?",
    "💻 How do I get my laptop set up?",
    "📡 What’s the company Wi‑Fi info?",
    "📑 What are the company policies?",
    "🛠️ How do I get IT support?",
    "🎉 What benefits do I get?",
    "🏖️ How many vacation days do I have?",
]

def render_suggested_questions_footer():
    """
    Pins the suggestions as a real footer BELOW the chat input.
    Uses a 'hook' element so CSS can promote the Streamlit container itself to fixed position.
    Also constrains and centers the chat input so it doesn't stretch full width.
    """
    st.markdown("""
    <style>
      :root {
        --sq-footer-h: 56px;
        --sq-maxw: 820px;
      }

      /* Give page body bottom padding so content isn't hidden behind fixed elements */
      .block-container { padding-bottom: calc(var(--sq-footer-h) + 130px); }

      /* Pin chat input above the footer and center it */
      /* Streamlit assigns data-testid="stChatInput" to the input wrapper */
      div[data-testid="stChatInput"] {
        position: fixed !important;
        left: 0; right: 0;
        bottom: calc(var(--sq-footer-h) + 10px);
        z-index: 1000;
        display: flex; justify-content: center;
        pointer-events: none; /* let inner input receive events only */
      }
      div[data-testid="stChatInput"] > div {
        width: 100%;
        max-width: var(--sq-maxw);
        pointer-events: auto;
      }

      /* Turn our container (the one that contains the hook) into a fixed footer */
      /* :has() is supported in modern Chrome/Edge */
      div:has(> #sq_footer_hook) {
        position: fixed;
        left: 0; right: 0; bottom: 0;
        z-index: 998; /* slightly under the chat input */
        background: rgba(21,23,26,0.95);
        backdrop-filter: blur(6px);
        border-top: 1px solid rgba(255,255,255,0.08);
        padding: 8px 12px;
      }

      /* Center content and limit width */
      div:has(> #sq_footer_hook) > div {
        max-width: calc(var(--sq-maxw) + 40px);
        margin: 0 auto;
        display: flex; flex-wrap: wrap; justify-content: center; gap: 6px;
      }

      /* Style the suggestion buttons living inside this container */
      div:has(> #sq_footer_hook) .stButton { display: inline-block; }
      div:has(> #sq_footer_hook) .stButton > button {
        background: #1d2126;
        border: 1px solid rgba(255,255,255,0.12);
        color: #e8e8e8;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.86rem;
        cursor: pointer;
        transition: all .2s ease;
        white-space: nowrap;
      }
      div:has(> #sq_footer_hook) .stButton > button:hover {
        background: #ffaf25; color: #000; border-color: #ffaf25;
      }

      @media (max-width: 640px) {
        div[data-testid="stChatInput"] > div { max-width: 94vw; }
        div:has(> #sq_footer_hook) .stButton > button {
          padding: 6px 10px; font-size: 0.82rem;
        }
      }
    </style>
    """, unsafe_allow_html=True)

    # This container becomes the fixed footer thanks to the :has() selector.
    footer = st.container()
    with footer:
        st.markdown('<div id="sq_footer_hook"></div>', unsafe_allow_html=True)

        # Actual suggestion buttons (now children of the same container)
        cols = st.columns(min(4, max(2, len(SUGGESTED_QUESTIONS)//3 or 2)))
        idx = 0
        for idx, q in enumerate(SUGGESTED_QUESTIONS):
            if st.button(q, key=f"sq_{idx}"):
                # DON'T set st.session_state.chat_input here
                st.session_state.pending_prompt = q
                # optional: also clear any existing text next run
                st.session_state.clear_input = True

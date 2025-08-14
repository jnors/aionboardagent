# suggested_questions_rail.py
import streamlit as st

SUGGESTED_QUESTIONS = [
    "📅 What's the first week schedule?",
    "💻 How do I get my laptop set up?",
    "📡 What’s the company Wi-Fi info?",
    "📑 What are the company policies?",
    "🛠️ How do I get IT support?",
    "🎉 What benefits do I get?",
    "🏖️ How many vacation days do I have?",
]

def render_suggested_questions_rail():
    """
    Right-side vertical 'second sidebar' aligned to the RIGHT EDGE of the chat area.
    - Aligns to chat content width (same max-width as your bubbles/input)
    - Fixed to the viewport; scrolls independently if long
    - Safe: only sets pending_prompt (no mutation of chat_input)
    - Hidden on narrow screens
    """
    st.markdown("""
    <style>
      :root {
        --chat-maxw: 820px;      /* chat area + chat_input width */
        --rail-w: 320px;         /* width of the suggestions sidebar */
        --rail-gutter: 16px;     /* gap between chat area and rail */
        --rail-top: 110px;       /* space under the title; tweak to taste */
      }

      /* Constrain & center the chat input to match the chat area width */
      div[data-testid="stChatInput"] > div {
        max-width: var(--chat-maxw);
        margin: 0 auto;
      }

      /* Reserve visual space so content doesn't hide under the rail */
      @media (min-width: 1200px) {
        .block-container { margin-right: calc(var(--rail-w) + var(--rail-gutter) + 12px) !important; }
      }

      /* Fixed right rail aligned to the right edge of the chat area:
         center of page + half chat width + gutter. */
      @media (min-width: 1200px) {
        div:has(#sq_rail_hook) {
          position: fixed;
          top: var(--rail-top);
          left: calc(50% + (var(--chat-maxw) / 2) + var(--rail-gutter));
          width: var(--rail-w);
          max-height: calc(100vh - var(--rail-top) - 24px);
          overflow: auto;

          background: rgba(21,23,26,0.95);
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 14px;
          box-shadow: 0 10px 30px rgba(0,0,0,.30);
          padding: 12px;
          z-index: 1000;
        }
      }

      /* Hide rail on smaller screens to avoid crowding */
      @media (max-width: 1199px) {
        div:has(#sq_rail_hook) { display: none; }
      }

      /* Inner layout + button styles */
      div:has(#sq_rail_hook) .sq-title {
        font-weight: 600; font-size: .95rem; opacity: .9; margin-bottom: 10px;
      }
      div:has(#sq_rail_hook) .stButton { display: block; margin-bottom: 8px; }
      div:has(#sq_rail_hook) .stButton > button {
        width: 100%;
        text-align: left;
        background: #1d2126;
        color: #e8e8e8;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 12px;
        padding: 10px 12px;
        white-space: normal;
        transition: background .2s, border-color .2s, transform .05s;
      }
      div:has(#sq_rail_hook) .stButton > button:hover {
        background: #ffaf25; color: #000; border-color: #ffaf25;
      }
      div:has(#sq_rail_hook) .stButton > button:active { transform: translateY(1px); }
    </style>
    """, unsafe_allow_html=True)

    # This container becomes the fixed rail (via :has(#sq_rail_hook))
    rail = st.container()
    with rail:
        st.markdown('<div id="sq_rail_hook"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sq-title">💡 Suggested</div>', unsafe_allow_html=True)

        for i, q in enumerate(SUGGESTED_QUESTIONS):
            if st.button(q, key=f"sq_r_{i}"):
                st.session_state.pending_prompt = q
                st.session_state.clear_input = True

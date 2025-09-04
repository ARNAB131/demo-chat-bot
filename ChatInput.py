# ChatInput.py
# Python translation of chatInput.jsx (names unchanged)
# Props preserved: onSend(message: str), placeholder: str = "Type your message...", disabled: bool = False

from typing import Callable, Optional
import streamlit as st

def ChatInput(onSend: Callable[[str], None], placeholder: str = "Type your message...", disabled: bool = False):
    """
    Renders a chat composer with a text input, mic icon (placeholder), and send button.
    Calls onSend(message) when user submits a non-empty message.
    """
    # Styles to resemble the original
    st.markdown("""
    <style>
      .ci-wrap{display:flex;gap:8px;padding:16px;background:#fff;border-top:1px solid #e5e7eb;}
      .ci-input{position:relative;flex:1;}
      .ci-mic{
        position:absolute;right:8px;top:50%;transform:translateY(-50%);
        height:32px;width:32px;border-radius:8px;border:0;background:transparent;color:#9ca3af;cursor:pointer;
      }
      .ci-mic:hover{color:#4b5563}
      .ci-send{
        padding:8px 16px;border-radius:8px;border:0;background:#3b82f6;color:#fff;cursor:pointer;
      }
      .ci-send:disabled{opacity:.5;cursor:not-allowed}
      .ci-input input{
        width:100%;padding:10px 40px 10px 12px;border-radius:8px;border:1px solid #e5e7eb;background:#f9fafb;
        outline:none;
      }
      .ci-input input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.2)}
    </style>
    """, unsafe_allow_html=True)

    # Use a form to get Enter-to-send behavior without rerender issues
    with st.form(key="chat_input_form", clear_on_submit=True):
        # We keep an internal key so multiple ChatInput calls don't collide
        msg: str = st.text_input("", value="", placeholder=placeholder, disabled=disabled, key="chat_input_text")
        cols = st.columns([1, 0.12, 0.22])

        with cols[1]:
            mic_clicked = st.form_submit_button("🎙", disabled=disabled, help="Voice input feature coming soon!")
        with cols[2]:
            send_clicked = st.form_submit_button("Send ➤", disabled=disabled or (not msg.strip()))

        # Mic click placeholder behavior (match the alert from JS)
        if mic_clicked and not disabled:
            st.toast("Voice input feature coming soon!", icon="🎙")

        if send_clicked and not disabled:
            message = msg.strip()
            if message:
                try:
                    onSend(message)
                except Exception as e:
                    # Fail-safe: surface any callback error to the UI
                    st.error(f"onSend error: {e}")

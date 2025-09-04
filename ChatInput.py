# ChatInput.py
from typing import Callable
import streamlit as st

def ChatInput(onSend: Callable[[str], None], placeholder: str = "Type your message...", disabled: bool = False, formKey: str = "chat"):
    """
    Renders a chat composer with a text input, mic icon (placeholder), and send button.
    Calls onSend(message) when user submits a non-empty message.
    """
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

    text_key = f"chat_input_text_{formKey}"
    # initialize once
    if text_key not in st.session_state:
        st.session_state[text_key] = ""

    with st.form(key=f"chat_input_form_{formKey}", clear_on_submit=False):
        cols = st.columns([1, 0.12, 0.22])
        with cols[0]:
            msg = st.text_input(
                label="",
                value=st.session_state[text_key],
                key=text_key,
                placeholder=placeholder,
                disabled=disabled,
                label_visibility="collapsed",
            )
        with cols[1]:
            mic_clicked = st.form_submit_button("🎙", disabled=disabled, help="Voice input feature coming soon!")
        with cols[2]:
            send_clicked = st.form_submit_button("Send ➤", disabled=disabled or (not (msg or "").strip()))

    if mic_clicked and not disabled:
        st.toast("Voice input feature coming soon!", icon="🎙")

    if send_clicked and not disabled:
        message = (st.session_state[text_key] or "").strip()
        if message:
            try:
                onSend(message)
            finally:
                # clear AFTER we’ve used the value
                st.session_state[text_key] = ""
                # force UI to reflect new state immediately
                st.experimental_rerun()

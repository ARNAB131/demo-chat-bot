# ChatMessage.py
# Python translation of ChatMessage.jsx (names unchanged)
# Renders a chat bubble with optional typing indicator and timestamp.

from typing import Optional
import streamlit as st

def ChatMessage(message: str, isBot: bool, timestamp: Optional[str], isTyping: bool = False):
    # Minimal CSS to mimic the original look & feel
    st.markdown("""
    <style>
      .cm-wrap{display:flex;gap:12px;margin-bottom:16px;align-items:flex-end;}
      .cm-wrap.left{justify-content:flex-start;}
      .cm-wrap.right{justify-content:flex-end;}
      .cm-avatar{
        width:40px;height:40px;border-radius:9999px;display:flex;align-items:center;justify-content:center;
        background:linear-gradient(90deg,#3b82f6,#2563eb); /* blue gradient */
        color:#fff;font-weight:700;font-size:14px;flex-shrink:0;
      }
      .cm-avatar.user{background:linear-gradient(90deg,#22c55e,#16a34a);} /* green gradient */
      .cm-box{max-width:min(36rem,80vw);}
      .cm-bubble{
        border-radius:18px;padding:10px 14px;font-size:14px;line-height:1.5;box-shadow:0 1px 2px rgba(0,0,0,.05);
      }
      .cm-bubble.bot{background:#fff;border:1px solid #e5e7eb;color:#111827;}
      .cm-bubble.user{background:linear-gradient(90deg,#3b82f6,#2563eb);color:#fff;}
      .cm-time{display:flex;gap:6px;margin-top:4px;font-size:12px;color:#9ca3af;}
      /* typing dots */
      .dots{display:inline-flex;gap:4px;vertical-align:middle;margin-right:6px}
      .dot{width:6px;height:6px;border-radius:9999px;background:#60a5fa;display:inline-block;animation:bounce 1s infinite;}
      .dot:nth-child(2){animation-delay:.1s}
      .dot:nth-child(3){animation-delay:.2s}
      @keyframes bounce {
        0%,80%,100%{transform:translateY(0);opacity:.7}
        40%{transform:translateY(-4px);opacity:1}
      }
    </style>
    """, unsafe_allow_html=True)

    side_cls = "left" if isBot else "right"
    bubble_cls = "bot" if isBot else "user"
    avatar_text = "🤖" if isBot else "🙂"

    st.markdown(f"""
    <div class="cm-wrap {side_cls}">
      {"<div class='cm-avatar'>" + avatar_text + "</div>" if isBot else ""}
      <div class="cm-box">
        <div class="cm-bubble {bubble_cls}">
          {(
            "<span class='dots'><span class='dot'></span><span class='dot'></span><span class='dot'></span></span>"
            "<span style='font-size:12px;color:#6b7280;'>Doc is typing...</span>"
          ) if isTyping else message}
        </div>
        {(f"<div class='cm-time'><span>🕒</span><span>{timestamp}</span></div>") if timestamp else ""}
      </div>
      {"" if isBot else "<div class='cm-avatar user'>🙂</div>"}
    </div>
    """, unsafe_allow_html=True)

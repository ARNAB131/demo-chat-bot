# BedSelector.py
# Python translation of BedSelector.jsx (names preserved)
# Function signature: BedSelector(onSelect)

from typing import Callable, Dict, Any, List
import streamlit as st

# Bed options preserved exactly
bedOptions: List[Dict[str, Any]] = [
    {
        "type": "General Bed",
        "price": 100,
        "features": ["1 bed", "1 chair", "bed table"],
        "icon": "🛏️",
    },
    {
        "type": "General Cabin",
        "price": 1000,
        "features": ["2 beds", "attached washroom", "bed table", "chair", "food x3 times"],
        "icon": "👥",
    },
    {
        "type": "VIP Cabin",
        "price": 4000,
        "features": [
            "premium bed x2", "sofa", "Air Conditioning", "attached washroom",
            "TV", "fridge", "bed table x2", "coffee table", "2 chairs"
        ],
        "icon": "🌟",
    },
]

def BedSelector(onSelect: Callable[[Dict[str, Any] | None], None], key: str = "bed_selector"):
    """
    Render a list of bed options as cards with Select buttons, and a "No thanks" button.
    """
    st.markdown("""
    <style>
      .bed-card{border:1px solid #e5e7eb;border-radius:12px;background:#fff;overflow:hidden;}
      .bed-head{padding:12px 16px;display:flex;justify-content:space-between;align-items:center;}
      .bed-title{font-weight:600;font-size:16px;color:#111827;}
      .bed-price{font-size:18px;font-weight:700;color:#111827;}
      .bed-price span{font-size:12px;font-weight:400;color:#6b7280;}
      .bed-body{padding:12px 16px;}
      .bed-feat{display:flex;align-items:center;gap:6px;font-size:13px;color:#374151;margin-bottom:4px;}
      .bed-icon{font-style:normal}
      .bed-btn{width:100%;padding:10px;border-radius:10px;background:#2563eb;color:#fff;border:0;cursor:pointer;}
      .bed-btn:hover{background:#1e40af;}
      .bed-btn-outline{width:100%;padding:10px;margin-top:12px;border-radius:10px;background:#fff;border:1px solid #d1d5db;color:#111827;cursor:pointer;}
      .bed-btn-outline:hover{background:#f9fafb;}
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(bedOptions))
    for i, option in enumerate(bedOptions):
        with cols[i]:
            st.markdown('<div class="bed-card">', unsafe_allow_html=True)
            st.markdown('<div class="bed-head">', unsafe_allow_html=True)
            st.markdown(f'<div class="bed-title">{option["type"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bed-icon">{option["icon"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="bed-price">₹{option["price"]} <span>/ night</span></div>', unsafe_allow_html=True)
            st.markdown('<div class="bed-body">', unsafe_allow_html=True)
            for feature in option["features"]:
                st.markdown(f'<div class="bed-feat"><span class="bed-icon">✔️</span>{feature}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Select", key=f"{key}_{i}"):
                try:
                    onSelect(option)
                except Exception as e:
                    st.error(f"onSelect error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("No, thanks", key=f"{key}_none"):
        try:
            onSelect(None)
        except Exception as e:
            st.error(f"onSelect error: {e}")

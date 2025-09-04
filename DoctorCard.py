# DoctorCard.py
# Python translation of DoctorCard.jsx (names unchanged)
# Props preserved: DoctorCard(doctor, availableSlots, estimatedTime, distance, onBook)

from typing import Callable, List, Optional, Dict, Any
import streamlit as st

def DoctorCard(
    doctor: Dict[str, Any],
    availableSlots: Optional[List[str]],
    estimatedTime: Optional[float],
    distance: Optional[float],
    onBook: Callable[[Dict[str, Any]], None],
    key: Optional[str] = None,
):
    """
    Renders a doctor card with name, specialization, chamber, experience,
    optional distance/ETA row, a few available slots badges, and a Book button.
    """
    # Styles to emulate the React card + badges
    st.markdown("""
    <style>
      .dc-card{border:1px solid #e5e7eb;border-radius:12px;background:#fff;transition:box-shadow .2s;}
      .dc-card:hover{box-shadow:0 4px 12px rgba(0,0,0,.06);}
      .dc-body{padding:16px;}
      .dc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;}
      .dc-name{font-weight:600;font-size:16px;color:#111827;}
      .dc-spec{color:#2563eb;font-size:14px;}
      .dc-exp{display:flex;align-items:center;gap:6px;color:#4b5563;font-size:13px;}
      .dc-row{display:flex;align-items:center;gap:8px;color:#4b5563;font-size:13px;margin:6px 0;}
      .dc-badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
      .dc-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 8px;border-radius:999px;border:1px solid #e5e7eb;background:#fff;font-size:12px;color:#111827;}
      .dc-btn{width:100%;margin-top:12px;padding:10px 14px;border-radius:10px;border:0;background:#22c55e;color:#fff;cursor:pointer;}
      .dc-btn:disabled{opacity:.6;cursor:not-allowed;}
      .muted{color:#6b7280;}
      .icon{font-style:normal}
    </style>
    """, unsafe_allow_html=True)

    name = doctor.get("name", "")
    specialization = doctor.get("specialization", "")
    chamber = doctor.get("chamber", "")
    experience = doctor.get("experience", "")

    # Guard against None for slots
    slots = list(availableSlots or [])
    top_slots = slots[:3]
    more_count = max(0, len(slots) - 3)

    # Determine disabled state
    disabled = (len(slots) == 0)

    # Unique keys for multiple instances
    k = key or f"DoctorCard_{name}_{specialization}"

    st.markdown('<div class="dc-card">', unsafe_allow_html=True)
    st.markdown('<div class="dc-body">', unsafe_allow_html=True)

    # Top header
    st.markdown('<div class="dc-top">', unsafe_allow_html=True)
    left_col, right_col = st.columns([0.78, 0.22])

    with left_col:
        st.markdown(f'<div class="dc-name">Dr. {name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="dc-spec">{specialization}</div>', unsafe_allow_html=True)
    with right_col:
        if experience:
            st.markdown(f'<div class="dc-exp"><span class="icon">🏅</span><span class="muted">{experience} Exp.</span></div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # dc-top

    # Chamber row
    if chamber:
        st.markdown(f'<div class="dc-row"><span class="icon">📍</span><span>{chamber}</span></div>', unsafe_allow_html=True)

    # Distance/ETA row
    if distance is not None:
        try:
            d_txt = f"{float(distance):.1f}km away"
        except Exception:
            d_txt = f"{distance}km away"
        eta_txt = f" • ~{int(estimatedTime)} min travel" if (estimatedTime is not None) else ""
        st.markdown(f'<div class="dc-row"><span class="icon">⏱️</span><span>{d_txt}{eta_txt}</span></div>', unsafe_allow_html=True)

    # Available slots badges
    if len(slots) > 0:
        st.markdown('<div class="muted" style="margin-top:8px;">Available today:</div>', unsafe_allow_html=True)
        st.markdown('<div class="dc-badges">', unsafe_allow_html=True)
        for s in top_slots:
            st.markdown(f'<div class="dc-badge"><span class="icon">📅</span>{s}</div>', unsafe_allow_html=True)
        if more_count > 0:
            st.markdown(f'<div class="dc-badge">+{more_count} more</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Book button -> calls onBook(doctor)
    col_btn = st.columns(1)[0]
    with col_btn:
        clicked = st.button("Book Appointment", key=f"{k}_book", disabled=disabled)
        if clicked:
            try:
                onBook(doctor)
            except Exception as e:
                st.error(f"onBook error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)  # dc-body
    st.markdown('</div>', unsafe_allow_html=True)  # dc-card

# SymptomSelector.py
# Python translation of SymptomSelector.jsx (names unchanged)
# Props preserved: onSubmit(selectedSymptoms: list[str]), onSkip()

from typing import Callable, List
import streamlit as st

# Keep the same constant name as in JS
commonSymptoms: List[str] = [
    'Fever', 'Headache', 'Cough', 'Sore throat', 'Body ache',
    'Nausea', 'Vomiting', 'Diarrhea', 'Chest pain', 'Shortness of breath',
    'Dizziness', 'Fatigue', 'Loss of appetite', 'Stomach pain', 'Joint pain'
]

def SymptomSelector(onSubmit: Callable[[List[str]], None], onSkip: Callable[[], None]):
    """
    Renders symptom chips (toggle), custom symptom add, selected list with remove,
    and action buttons: Continue with Symptoms (n) / Skip / No Symptoms.
    """
    # Local state keys (stable, unique to this component)
    sel_key = "SymptomSelector_selectedSymptoms"
    custom_key = "SymptomSelector_customSymptom"

    if sel_key not in st.session_state:
        st.session_state[sel_key] = []
    if custom_key not in st.session_state:
        st.session_state[custom_key] = ""

    selectedSymptoms: List[str] = st.session_state[sel_key]
    customSymptom: str = st.session_state[custom_key]

    # Styles to emulate badge look/feel
    st.markdown("""
    <style>
      .ss-wrap{background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;padding:16px;}
      .ss-title{font-weight:600;color:#111827;margin-bottom:12px;}
      .chips{display:flex;flex-wrap:wrap;gap:8px;}
      .chip{
        display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:999px;font-size:13px;cursor:pointer;
        border:1px solid #cbd5e1;background:#fff;color:#0f172a;
      }
      .chip:hover{background:#eff6ff;border-color:#93c5fd;color:#1d4ed8}
      .chip.active{background:#3b82f6;color:#fff;border-color:#2563eb;}
      .selected{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
      .sel{
        display:inline-flex;align-items:center;gap:6px;padding:4px 8px;border-radius:999px;font-size:12px;background:#f1f5f9;color:#0f172a;border:1px solid #e5e7eb;
      }
      .sel button{
        background:transparent;border:0;color:#ef4444;cursor:pointer;font-weight:700;
      }
      .row{display:flex;gap:8px;margin-top:10px;}
      .row input{
        flex:1;padding:8px 10px;border-radius:8px;border:1px solid #e5e7eb;
      }
      .btn{
        padding:8px 12px;border-radius:8px;border:1px solid #e5e7eb;background:#3b82f6;color:#fff;cursor:pointer;
      }
      .btn:disabled{opacity:.6;cursor:not-allowed}
      .btn-outline{background:#fff;color:#111827}
      .actions{display:flex;gap:8px;margin-top:12px;}
      .note{color:#64748b;font-size:12px;margin-top:8px;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ss-wrap">', unsafe_allow_html=True)

    # Title
    st.markdown('<div class="ss-title">Select your symptoms:</div>', unsafe_allow_html=True)

    # Chips (common symptoms)
    # Use buttons to toggle; unique keys per chip
    st.markdown('<div class="chips">', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, symptom in enumerate(commonSymptoms):
        active = symptom in selectedSymptoms
        with cols[i % 3]:
            clicked = st.button(
                symptom,
                key=f"symptom_chip_{symptom}",
                help="Click to toggle",
                type="secondary"
            )
            if clicked:
                if active:
                    st.session_state[sel_key] = [s for s in selectedSymptoms if s != symptom]
                else:
                    st.session_state[sel_key] = selectedSymptoms + [symptom]
                st.experimental_rerun()
        # Style the last rendered button as a chip (target via key is not direct; apply global style)
        st.markdown(f"""
        <script>
          const el = window.parent.document.querySelector('button[kind="secondary"][aria-label="{symptom}"]')
                   || window.parent.document.querySelector('button[title="{symptom}"]')
                   || null;
          if(el) {{
            el.classList.add('chip');
            {"el.classList.add('active');" if active else "el.classList.remove('active');"}
          }}
        </script>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Custom symptom add (use form to allow Enter key)
    with st.form(key="symptom_add_form", clear_on_submit=False):
        c1, c2 = st.columns([1, 0.18])
        with c1:
            val = st.text_input(
                "Add custom symptom...",
                value=customSymptom,
                key=custom_key,
                label_visibility="collapsed",
                placeholder="Add custom symptom..."
            )
        with c2:
            add = st.form_submit_button("Add")
        if add:
            s = (val or "").strip()
            if s and s not in selectedSymptoms:
                st.session_state[sel_key] = selectedSymptoms + [s]
                st.session_state[custom_key] = ""
                st.experimental_rerun()

    # Selected list with remove (X)
    if selectedSymptoms:
        st.markdown('<div class="selected">', unsafe_allow_html=True)
        for s in selectedSymptoms:
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                st.markdown(f'<div class="sel">{s}</div>', unsafe_allow_html=True)
            with c2:
                if st.button("✕", key=f"remove_{s}", help=f"Remove {s}"):
                    st.session_state[sel_key] = [x for x in selectedSymptoms if x != s]
                    st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Actions
    st.markdown('<div class="actions">', unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        cont = st.button(
            f"Continue with Symptoms ({len(selectedSymptoms)})",
            disabled=(len(selectedSymptoms) == 0),
            key="symptoms_continue"
        )
    with colB:
        skip = st.button("Skip / No Symptoms", key="symptoms_skip")
    st.markdown('</div>', unsafe_allow_html=True)

    if cont:
        try:
            onSubmit(st.session_state[sel_key])
        except Exception as e:
            st.error(f"onSubmit error: {e}")
    if skip:
        try:
            onSkip()
        except Exception as e:
            st.error(f"onSkip error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

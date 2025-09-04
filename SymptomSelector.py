# SymptomSelector.py
# Python translation of SymptomSelector.jsx (names unchanged)
# Props preserved: onSubmit(selectedSymptoms: list[str]), onSkip()

from typing import Callable, List
import streamlit as st

# Same commonSymptoms list as in JS
commonSymptoms: List[str] = [
    'Fever', 'Headache', 'Cough', 'Sore throat', 'Body ache',
    'Nausea', 'Vomiting', 'Diarrhea', 'Chest pain', 'Shortness of breath',
    'Dizziness', 'Fatigue', 'Loss of appetite', 'Stomach pain', 'Joint pain'
]

def SymptomSelector(onSubmit: Callable[[List[str]], None], onSkip: Callable[[], None]):
    """
    Renders selectable symptom chips, an input to add custom symptoms,
    and actions: Continue with Symptoms (N) / Skip / No Symptoms.
    Calls onSubmit(selectedSymptoms) or onSkip().
    """
    # Local session state to keep selections stable across reruns
    if "SymptomSelector_selectedSymptoms" not in st.session_state:
        st.session_state.SymptomSelector_selectedSymptoms = []
    if "SymptomSelector_customSymptom" not in st.session_state:
        st.session_state.SymptomSelector_customSymptom = ""

    selectedSymptoms = st.session_state.SymptomSelector_selectedSymptoms
    customSymptom = st.session_state.SymptomSelector_customSymptom

    # Styles to mimic the look/feel
    st.markdown("""
    <style>
      .ss-wrap{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:16px;}
      .ss-title{font-weight:600;color:#111827;margin-bottom:12px;}
      .ss-chips{display:flex;flex-wrap:wrap;gap:8px;}
      .chip{
        display:inline-flex;align-items:center;gap:6px;cursor:pointer;padding:6px 10px;border-radius:9999px;font-size:13px;
        border:1px solid #e5e7eb;color:#1f2937;background:#fff;
      }
      .chip:hover{background:#eff6ff;color:#2563eb;border-color:#bfdbfe}
      .chip.active{background:#3b82f6;color:#fff;border-color:#2563eb}
      .ss-row{display:flex;gap:8px;margin-top:12px}
      .ss-row input{
        flex:1;padding:8px 10px;border-radius:8px;border:1px solid #e5e7eb;outline:none;
      }
      .ss-row input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.2)}
      .btn{padding:8px 12px;border-radius:8px;border:0;cursor:pointer;}
      .btn-primary{background:#3b82f6;color:#fff}
      .btn-primary:disabled{opacity:.5;cursor:not-allowed}
      .btn-outline{background:#fff;border:1px solid #e5e7eb;color:#111827}
      .sel-wrap{margin-top:10px}
      .sel-chip{display:inline-flex;align-items:center;gap:6px;border-radius:9999px;padding:4px 10px;font-size:12px;background:#f3f4f6;margin:4px}
      .sel-chip button{background:transparent;border:0;color:#ef4444;cursor:pointer}
      .actions{display:flex;gap:8px;padding-top:8px}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ss-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="ss-title">Select your symptoms:</div>', unsafe_allow_html=True)

    # Chips for common symptoms
    st.markdown('<div class="ss-chips">', unsafe_allow_html=True)
    cols = st.columns(5) if len(commonSymptoms) >= 5 else st.columns(len(commonSymptoms))
    for i, symptom in enumerate(commonSymptoms):
        col = cols[i % len(cols)]
        with col:
            active = symptom in selectedSymptoms
            if st.button(symptom + (" ✓" if active else ""), key=f"chip_{symptom}", use_container_width=True):
                if active:
                    selectedSymptoms.remove(symptom)
                else:
                    selectedSymptoms.append(symptom)
                st.session_state.SymptomSelector_selectedSymptoms = selectedSymptoms.copy()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Custom symptom row
    with st.container():
        st.markdown('<div class="ss-row">', unsafe_allow_html=True)
        c1, c2 = st.columns([0.78, 0.22])
        with c1:
            customSymptom = st.text_input(
                "Add custom symptom...",
                value=customSymptom,
                label_visibility="collapsed",
                key="SymptomSelector_customSymptom_input",
                placeholder="Add custom symptom..."
            )
            st.session_state.SymptomSelector_customSymptom = customSymptom
        with c2:
            add_clicked = st.button("Add", key="SymptomSelector_add_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Add custom on Enter (simulate)
        # Streamlit doesn't capture Enter into a callback without a form; keep "Add" button.

        if add_clicked:
            cs = (customSymptom or "").strip()
            if cs and cs not in selectedSymptoms:
                selectedSymptoms.append(cs)
                st.session_state.SymptomSelector_selectedSymptoms = selectedSymptoms.copy()
                st.session_state.SymptomSelector_customSymptom = ""
                st.rerun()

    # Selected list
    if selectedSymptoms:
        st.markdown('<div class="sel-wrap"><div class="small text-gray-600">Selected symptoms:</div>', unsafe_allow_html=True)
        # Render chips with remove buttons
        for s in selectedSymptoms:
            cols = st.columns([0.88, 0.12])
            with cols[0]:
                st.markdown(f'<div class="sel-chip">{s}</div>', unsafe_allow_html=True)
            with cols[1]:
                if st.button("✕", key=f"rm_{s}", help=f"Remove {s}"):
                    selectedSymptoms.remove(s)
                    st.session_state.SymptomSelector_selectedSymptoms = selectedSymptoms.copy()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Actions
    st.markdown('<div class="actions">', unsafe_allow_html=True)
    cA, cB = st.columns(2)
    with cA:
        cont = st.button(
            f"Continue with Symptoms ({len(selectedSymptoms)})",
            key="SymptomSelector_continue",
            disabled=(len(selectedSymptoms) == 0),
            use_container_width=True
        )
    with cB:
        skip = st.button("Skip / No Symptoms", key="SymptomSelector_skip", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if cont:
        try:
            onSubmit(selectedSymptoms.copy())
        except Exception as e:
            st.error(f"onSubmit error: {e}")

    if skip:
        try:
            onSkip()
        except Exception as e:
            st.error(f"onSkip error: {e}")

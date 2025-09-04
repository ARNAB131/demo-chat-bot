import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import math
import json
import random
import base64

# -------------------------------------------------------------------
# Streamlit compatibility shims
# -------------------------------------------------------------------
if not hasattr(st, "experimental_rerun") and hasattr(st, "rerun"):
    st.experimental_rerun = st.rerun

def _rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_force_refresh"] = st.session_state.get("_force_refresh", 0) + 1

# -------------------------------------------------------------------
# Imported UI components you already have as .py files in root
# (They render chat bubbles, symptom picker, doctor cards, bed picker)
# -------------------------------------------------------------------
from ChatMessage import ChatMessage
from SymptomSelector import SymptomSelector
from DoctorCard import DoctorCard
from BedSelector import BedSelector
from AppointmentCard import AppointmentCard  # not used for print; kept for continuity

# Optional schemas (won’t block if pydantic missing on Cloud)
try:
    from models import Appointment, Doctor, Hospital  # noqa: F401
except Exception:
    Appointment = Doctor = Hospital = object  # placeholders


# -------------------------------------------------------------------
# Data you provided (Doctors + Hospitals)
# -------------------------------------------------------------------
DOCTORS_MASTER = [
    {
        "name": "Dr. Amit Kumar Kalwar",
        "specialization": "General Medicine",
        "chamber": "Jeevan Jyoti Institute Of Medical Science, Meherpur",
        "visiting_hours": "11.00am-1.30pm",
        "available_slots": ["11:00am-11:30am", "12:00pm-12:30pm", "1:00pm-1:30pm"],
        "experience": "15 years",
    },
    {
        "name": "Dr. Suvajoyti Chakraborty",
        "specialization": "General and Laparoscopic Surgeon",
        "chamber": "Silchar Medical & Collage, Medical Point",
        "visiting_hours": "11.00am-1.30pm",
        "available_slots": ["11:00am-11:30am", "12:00pm-12:30pm", "1:00pm-1:30pm"],
        "experience": "34 years",
    },
    {
        "name": "Dr. Abhinandan Bhattacharjee",
        "specialization": "ENT Surgeon",
        "chamber": "Munni Medical Hall, Sonai",
        "visiting_hours": "11.00am-4.00pm",
        "available_slots": ["11:00am-11:30am", "1:00pm-1:30pm", "3:00pm-3:30pm"],
        "experience": "10 years",
    },
    {
        "name": "Dr. R.P Banik",
        "specialization": "ENT Surgeon",
        "chamber": "Jeevan Jyoti Institute Of Medical Science, Meherpur",
        "visiting_hours": "12.30pm-2.30pm",
        "available_slots": ["12:30pm-1:00pm", "1:00pm-1:30pm", "2:00pm-2:30pm"],
        "experience": "18 years",
    },
    {
        "name": "Dr. Tirthankar Roy",
        "specialization": "Cardiologist",
        "chamber": "Silchar Medical & Collage, Medical Point",
        "visiting_hours": "1.30pm-2.30pm",
        "available_slots": ["1:30pm-2:00pm", "2:00pm-2:30pm"],
        "experience": "5 years",
    },
    {
        "name": "Dr. P.P Dutta",
        "specialization": "Urologist",
        "chamber": "Munni Medical Hall, Sonai",
        "visiting_hours": "12.00pm-12.30pm",
        "available_slots": ["12:00pm-12:30pm"],
        "experience": "10 years",
    },
    {
        "name": "Dr. Raj Kumar Bhattacharjee",
        "specialization": "Cardiologist",
        "chamber": "Jeevan Jyoti Institute Of Medical Science, Meherpur",
        "visiting_hours": "8.00pm-8.30pm",
        "available_slots": ["8:00pm-8:30pm"],
        "experience": "6 years",
    },
    {
        "name": "Dr. Prithwiraj Bhattacharjee",
        "specialization": "Medicine (Consultant Physician)",
        "chamber": "Silchar Medical & Collage , Medical Point",
        "visiting_hours": "6.00pm-8.00pm",
        "available_slots": ["6:00pm-6:30pm", "7:00pm-7:30pm"],
        "experience": "10 years",
    },
    {
        "name": "Dr. P.K Das",
        "specialization": "Dentist",
        "chamber": "Munni Medical Hall, Sonai",
        "visiting_hours": "5.30pm-6.00pm",
        "available_slots": ["5:30pm-6:00pm"],
        "experience": "20 years",
    },
    {
        "name": "Dr. Kinnor Das",
        "specialization": "Dermatology",
        "chamber": "Jeevan Jyoti Institute Of Medical Science, Meherpur",
        "visiting_hours": "1.00pm-2.00pm",
        "available_slots": ["1:00pm-1:30pm", "1:30pm-2:00pm"],
        "experience": "3 years",
    },
]

HOSPITALS_MASTER = [
    {
        "name": "MUNNI MEDICAL HALL",
        "address": "MOTOR STAND, Tulargram Pt I, Sonai, Assam 788119",
        "latitude": 24.734, "longitude": 92.8913
    },
    {
        "name": "Jeevan Jyoti Institute of Medical Sciences",
        "address": "Meherpur, Birbal Bazar, Silchar, Assam 788015",
        "latitude": 24.788, "longitude": 92.7934
    },
    {
        "name": "Silchar Medical College and Hospital",
        "address": "Ghungoor, Masimpur, Silchar, Assam 788014",
        "latitude": 24.7758, "longitude": 92.7949
    },
]

# Bed inventory (today-level simple model)
BED_STOCK = {
    "General Bed": {"total": 50, "booked": 10, "prefix": "G"},
    "General Cabin": {"total": 20, "booked": 4, "prefix": "C"},
    "VIP Cabin": {"total": 10, "booked": 3, "prefix": "V"},
}

# -------------------------------------------------------------------
# Conversation Steps
# -------------------------------------------------------------------
conversationSteps = {
    "INITIAL": "initial",
    "ASK_NAME": "ask_name",
    "ASK_SYMPTOMS": "ask_symptoms",
    "CHOOSE_PATH": "choose_path",            # new step
    "LIST_DOCTORS": "list_doctors",
    "LIST_HOSPITALS": "list_hospitals",
    "ASK_BED": "ask_bed",
    "ASK_VITALS": "ask_vitals",
    "COLLECT_DETAILS": "collect_details",
    "FINAL_CARD": "final_card",
}

patientDetailSteps = [
    {"key": "patient_phone", "label": "phone number"},
    {"key": "patient_gender", "label": "gender (male/female/other)"},
    {"key": "patient_age", "label": "age"},
    {"key": "patient_email", "label": "email address"},
    {"key": "patient_address", "label": "address"},
]

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def calculateDistance(lat1, lng1, lat2, lng2):
    if None in [lat1, lng1, lat2, lng2]:
        return None
    R = 6371
    dLat = (lat2 - lat1) * math.pi / 180
    dLng = (lng2 - lng1) * math.pi / 180
    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(lat1 * math.pi / 180)
        * math.cos(lat2 * math.pi / 180)
        * math.sin(dLng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def calculateETA(distance_km: Optional[float]) -> Optional[int]:
    if distance_km is None:
        return None
    return round(distance_km * 2)  # ~30km/h average

def _synth_vitals() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "systolic_bp": round(random.uniform(110, 130), 1),
        "diastolic_bp": round(random.uniform(70, 85), 1),
        "body_temperature": round(random.uniform(36.4, 37.2), 1),
    }

def get_recent_vitals() -> Dict[str, Any]:
    try:
        from vitals_bridge import get_latest_vitals  # type: ignore
        v = get_latest_vitals()
        if v:
            return v
    except Exception:
        pass
    df = st.session_state.get("forecast_data", None)
    if df is not None and getattr(df, "empty", True) is False:
        try:
            row = df.iloc[-1]
            return {
                "timestamp": str(row.get("timestamp", datetime.now().isoformat(timespec="seconds"))),
                "systolic_bp": float(row.get("systolic_bp", 120.0)),
                "diastolic_bp": float(row.get("diastolic_bp", 80.0)),
                "body_temperature": float(row.get("body_temperature", 36.8)),
            }
        except Exception:
            pass
    return _synth_vitals()

def _assign_bed_serial(bed_type: str) -> Optional[str]:
    stock = BED_STOCK.get(bed_type)
    if not stock:
        return None
    booked = st.session_state.get("booked_map", {}).get(bed_type, set())
    for i in range(1, stock["total"] + 1):
        sid = f"{stock['prefix']}-{i}"
        if sid not in booked:
            # Respect already booked initial numbers
            # Mark first N as prebooked
            if i <= stock["booked"]:
                continue
            booked.add(sid)
            st.session_state.setdefault("booked_map", {})[bed_type] = booked
            return sid
    return None

def _bed_counts_text() -> str:
    out = []
    for t, s in BED_STOCK.items():
        used = s["booked"] + len(st.session_state.get("booked_map", {}).get(t, set()))
        out.append(f"{t}: {s['total']-used} available (of {s['total']})")
    return " • ".join(out)

# -------------------------------------------------------------------
# HTML receipt (styled like your sample)
# -------------------------------------------------------------------
def build_receipt_html(appt: Dict[str, Any]) -> str:
    # Format pieces
    patient = {
        "name": appt.get("patient_name", ""),
        "age": appt.get("patient_age", ""),
        "gender": appt.get("patient_gender", ""),
        "phone": appt.get("patient_phone", ""),
        "email": appt.get("patient_email", ""),
        "address": appt.get("patient_address", ""),
    }
    booking_type = appt.get("booking_type", "normal").capitalize()
    doc = appt.get("doctor_name", "")
    hosp = appt.get("hospital_name", "")
    dt_str = datetime.fromisoformat(appt.get("appointment_date")).strftime("%d/%m/%Y")
    time_slot = appt.get("appointment_time", "")
    issued = datetime.now().strftime("%d/%m/%Y, %I:%M %p")

    bed_block = ""
    if appt.get("needs_bed") and appt.get("bed_type"):
        bed_type = appt.get("bed_type")
        bed_price = (appt.get("bed_details") or {}).get("price", "")
        bed_ser = (appt.get("bed_details") or {}).get("serial", "")
        feats = (appt.get("bed_details") or {}).get("features", [])
        feats_html = "".join([f"<li>{f}</li>" for f in feats]) if feats else "<li>—</li>"
        bed_block = f"""
        <section>
          <h2 class="h2">Bed/Cabin Details</h2>
          <p><strong>Type:</strong> {bed_type}</p>
          <p><strong>Serial #:</strong> {bed_ser or "Assigned at admit desk"}</p>
          <p><strong>Price per night:</strong> ₹{bed_price}</p>
          <div class="mt">
            <strong>Features:</strong>
            <ul class="ul">{feats_html}</ul>
          </div>
        </section>
        """

    sym_block = ""
    syms = appt.get("symptoms") or []
    if syms:
        sym_block = f"""
        <div class="mt">
          <strong>Symptoms:</strong> {", ".join(syms)}
        </div>
        """

    vitals_block = ""
    rv = appt.get("recent_vitals")
    if rv:
        vitals_block = f"""
        <section>
          <h2 class="h2">Attached Recent Vitals</h2>
          <div class="grid">
            <div><strong>Systolic BP:</strong> {rv.get("systolic_bp","")} mmHg</div>
            <div><strong>Diastolic BP:</strong> {rv.get("diastolic_bp","")} mmHg</div>
            <div><strong>Body Temperature:</strong> {rv.get("body_temperature","")} °C</div>
            <div><strong>Recorded:</strong> {rv.get("timestamp","")}</div>
          </div>
        </section>
        """

    # CSS tuned to your uploaded sample
    css = """
    body { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji";
           color:#1f2937; }
    .wrap { padding:24px; max-width:800px; margin:0 auto; }
    .title { font-size:28px; font-weight:800; color:#2563eb; text-align:center; margin-bottom:6px; }
    .sub { font-size:16px; color:#6b7280; text-align:center; margin-bottom:20px; }
    .h2 { font-size:18px; font-weight:700; border-bottom:2px solid #e5e7eb; padding-bottom:8px; margin:18px 0 12px; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .foot { color:#6b7280; text-align:center; margin-top:28px; font-size:14px; }
    .ul { margin:6px 0 0 18px; }
    .mt { margin-top:8px; }
    .badge { display:inline-block; padding:3px 8px; border-radius:999px; background:#eef2ff; color:#1d4ed8; font-size:12px; margin-top:6px;}
    @media print { .no-print { display:none; } }
    """
    # HTML template (based on your file)
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Doctigo Booking Summary</title>
  <style>{css}</style>
</head>
<body>
  <div class="wrap" id="print-receipt">
    <header>
      <h1 class="title">Doctigo Booking Summary</h1>
      <p class="sub">{hosp}</p>
    </header>

    <section>
      <h2 class="h2">Patient Details</h2>
      <div class="grid">
        <div><strong>Patient Name:</strong> {patient["name"]}</div>
        <div><strong>Age:</strong> {patient["age"]}</div>
        <div><strong>Gender:</strong> {patient["gender"]}</div>
        <div><strong>Phone:</strong> {patient["phone"]}</div>
        <div style="grid-column:1/-1;"><strong>Email:</strong> {patient["email"]}</div>
        <div style="grid-column:1/-1;"><strong>Address:</strong> {patient["address"]}</div>
      </div>
    </section>

    <section>
      <h2 class="h2">Appointment Details</h2>
      <div class="grid">
        <div><strong>Doctor:</strong> {doc}</div>
        <div><strong>Booking Type:</strong> <span class="badge">{booking_type}</span></div>
        <div><strong>Date:</strong> {dt_str}</div>
        <div><strong>Time:</strong> {time_slot}</div>
      </div>
      {sym_block}
    </section>

    {bed_block}
    {vitals_block}

    <footer class="foot">
      <p>This receipt was auto-generated by Doctigo AI.</p>
      <p>Issued on: {issued}</p>
    </footer>

    <div class="no-print" style="margin-top:16px; text-align:center;">
      <button onclick="window.print()" style="padding:10px 16px;border-radius:8px;background:#2563eb;color:#fff;border:0;cursor:pointer;">
        Print
      </button>
    </div>
  </div>
</body>
</html>"""
    return html

def _html_download_button(html_str: str, filename: str, label: str = "⬇️ Download HTML (print to PDF)"):
    b = html_str.encode("utf-8")
    b64 = base64.b64encode(b).decode()
    href = f"data:text/html;base64,{b64}"
    st.download_button(label=label, data=b, file_name=filename, mime="text/html")

# -------------------------------------------------------------------
# Solid Chat Input (Enter + Button)
# -------------------------------------------------------------------
def SafeChatInput(onSend, placeholder="Type your message...", disabled=False, formKey="chat"):
    text_key = f"chat_input_text_{formKey}"
    btn_key = f"chat_input_btn_{formKey}"
    st.session_state.setdefault(text_key, "")

    def _send_cb():
        msg = (st.session_state.get(text_key) or "").strip()
        if not msg or disabled:
            return
        try:
            onSend(msg)
        finally:
            st.session_state[text_key] = ""
            _rerun()

    st.markdown("""
    <style>
      .ci-row{display:flex;gap:8px;padding:12px;background:#111214;border-top:1px solid #2a2b2f;}
      .ci-row input{
        width:100%;padding:12px 14px;border-radius:10px;border:1px solid #2a2b2f;background:#0d1117;color:#e6edf3;outline:none;
      }
      .ci-row input:focus{border-color:#1f6feb;box-shadow:0 0 0 3px rgba(31,111,235,.25)}
      .ci-row button{padding:10px 16px;border-radius:10px;border:1px solid #2a2b2f;background:#1f6feb;color:#fff;cursor:pointer;}
      .ci-row button:disabled{opacity:.5;cursor:not-allowed;}
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 0.18], gap="small")
    with c1:
        st.text_input(
            label="",
            key=text_key,
            placeholder=placeholder,
            disabled=disabled,
            label_visibility="collapsed",
            on_change=_send_cb,
        )
    with c2:
        st.button("Send ➤", key=btn_key, on_click=_send_cb, disabled=disabled)

# -------------------------------------------------------------------
# Main App
# -------------------------------------------------------------------
def BookingPage():
    st.set_page_config(page_title="Doctigo AI", page_icon="🩺", layout="centered")

    # Session init
    for k, v in {
        "messages": [],
        "currentStep": conversationSteps["INITIAL"],
        "patientName": "",
        "bookingType": "",
        "symptoms": [],
        "selectedDoctor": None,
        "selectedHospital": None,
        "bedSelection": None,
        "patientDetails": {},
        "currentDetailStep": 0,
        "finalAppointment": None,
        "recentVitals": None,
        "booked_map": {},  # bed type -> set(serials)
    }.items():
        st.session_state.setdefault(k, v)

    st.title("🩺 Doctigo AI")
    st.caption("Your AI-powered medical booking assistant")

    step = st.session_state.currentStep

    # ---------- INITIAL ----------
    if step == conversationSteps["INITIAL"]:
        st.subheader("Choose booking type")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Normal Booking"):
                st.session_state.bookingType = "normal"
                st.session_state.messages.append({"text": "I want normal booking", "isBot": False})
                st.session_state.currentStep = conversationSteps["ASK_NAME"]; _rerun()
        with c2:
            if st.button("🚨 Emergency Booking"):
                st.session_state.bookingType = "emergency"
                st.session_state.messages.append({"text": "I want emergency booking", "isBot": False})
                st.session_state.currentStep = conversationSteps["ASK_NAME"]; _rerun()

    # ---------- CHAT ----------
    else:
        st.markdown("### Chat")
        for msg in st.session_state.messages:
            ChatMessage(message=msg["text"], isBot=msg["isBot"], timestamp=None)

        # ASK_NAME
        if step == conversationSteps["ASK_NAME"]:
            ChatMessage("Hello! I am Doc, your friendly neighborhood **Spider Doc** 🕷️🩺. What's your name?", True, None)
            SafeChatInput(onSend=handleName, formKey="ask_name")

        # ASK_SYMPTOMS
        elif step == conversationSteps["ASK_SYMPTOMS"]:
            if st.session_state.bookingType == "emergency":
                ChatMessage("Woooo it's an **EMERGENCY**! Enter your symptoms or type **next**.", True, None)
            else:
                ChatMessage("Enter your symptoms or type **next**.", True, None)
            SymptomSelector(onSubmit=handleSymptoms, onSkip=lambda: handleSymptoms([]))

        # CHOOSE_PATH (doctors vs hospitals)
        elif step == conversationSteps["CHOOSE_PATH"]:
            ChatMessage("What would you like to choose next?", True, None)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("👨‍⚕️ See Doctors"):
                    st.session_state.currentStep = conversationSteps["LIST_DOCTORS"]; _rerun()
            with c2:
                if st.button("🏥 See Hospitals"):
                    st.session_state.currentStep = conversationSteps["LIST_HOSPITALS"]; _rerun()

        # LIST_DOCTORS
        elif step == conversationSteps["LIST_DOCTORS"]:
            ChatMessage("Here are the available doctors:", True, None)
            # If symptoms present, filter by specialization keywords
            filtered = DOCTORS_MASTER
            if st.session_state.symptoms:
                sy_lower = " ".join([s.lower() for s in st.session_state.symptoms])
                # simple rule map
                spec_map = [
                    ("fever cough sore throat", "General Medicine"),
                    ("chest pain shortness breath", "Cardiologist"),
                    ("ear nose throat", "ENT Surgeon"),
                    ("skin rash acne", "Dermatology"),
                    ("tooth gum", "Dentist"),
                    ("urine kidney", "Urologist"),
                    ("surgery", "Laparoscopic"),
                ]
                wanted_specs = set()
                for keys, spec in spec_map:
                    for k in keys.split():
                        if k in sy_lower:
                            wanted_specs.add(spec)
                if wanted_specs:
                    filtered = [d for d in DOCTORS_MASTER if any(ws in d["specialization"] for ws in wanted_specs)]
                    if not filtered:
                        filtered = DOCTORS_MASTER  # fallback
            for doc in filtered:
                # hospital distance/ETA optional – omitted to keep it simple
                DoctorCard(
                    doctor=doc,
                    availableSlots=doc["available_slots"],
                    estimatedTime=None,
                    distance=None,
                    onBook=handleDoctorSelect,
                )

        # LIST_HOSPITALS
        elif step == conversationSteps["LIST_HOSPITALS"]:
            ChatMessage("Here are the hospitals. Select one to browse beds/cabins:", True, None)
            for h in HOSPITALS_MASTER:
                with st.container(border=True):
                    st.markdown(f"**{h['name']}**  \n_{h['address']}_")
                    if st.button(f"Select **{h['name']}**", key=f"h_{h['name']}"):
                        st.session_state.selectedHospital = h
                        st.session_state.messages.append({"text": f"Selected hospital: {h['name']}", "isBot": False})
                        st.session_state.currentStep = conversationSteps["ASK_BED"]; _rerun()
            st.caption("Inventory right now: " + _bed_counts_text())

        # ASK_BED
        elif step == conversationSteps["ASK_BED"]:
            ChatMessage("Do you need to book a **Bed/Cabin**? (Inventory: " + _bed_counts_text() + ")", True, None)
            BedSelector(onSelect=handleBedSelect)

        # ASK_VITALS
        elif step == conversationSteps["ASK_VITALS"]:
            ChatMessage("Hey buddy, why don't you hook up your **recent vitals**? Type **Yes** or **No**.", True, None)
            SafeChatInput(onSend=handleVitalsChoice, formKey="ask_vitals", placeholder="Type Yes or No...")

        # COLLECT_DETAILS
        elif step == conversationSteps["COLLECT_DETAILS"]:
            idx = st.session_state.currentDetailStep
            detail = patientDetailSteps[idx]
            ChatMessage(f"Please enter patient's {detail['label']}:", True, None)
            SafeChatInput(onSend=handleDetail, formKey=f"detail_{detail['key']}")

        # FINAL_CARD (HTML receipt preview + downloads)
        elif step == conversationSteps["FINAL_CARD"]:
            ChatMessage("🎉 Appointment confirmed! Here's your booking summary (use **Print** to save as PDF):", True, None)
            appt = st.session_state.finalAppointment or {}
            html = build_receipt_html(appt)

            # Embedded preview (iframe)
            st.components.v1.html(html, height=820, scrolling=True)

            # Download as HTML (user can open and Print to PDF)
            _html_download_button(html, "doctigo_receipt.html")

            # Optional: also show your existing AppointmentCard box UI
            with st.expander("Card view (UI box)"):
                AppointmentCard(appt)

# -------------------------------------------------------------------
# Handlers
# -------------------------------------------------------------------
def handleName(name: str):
    st.session_state.patientName = name
    st.session_state.messages.append({"text": name, "isBot": False})
    st.session_state.messages.append({"text": f"Hello {name}! Let's continue.", "isBot": True})
    st.session_state.currentStep = conversationSteps["ASK_SYMPTOMS"]; _rerun()

def handleSymptoms(symptoms: List[str]):
    st.session_state.symptoms = symptoms
    if symptoms:
        st.session_state.messages.append({"text": f"Symptoms: {', '.join(symptoms)}", "isBot": False})
    else:
        st.session_state.messages.append({"text": "No symptoms", "isBot": False})
    # For both cases, user chooses path (doctors or hospitals)
    st.session_state.currentStep = conversationSteps["CHOOSE_PATH"]; _rerun()

def handleDoctorSelect(doctor: Dict[str, Any]):
    st.session_state.selectedDoctor = doctor
    st.session_state.selectedHospital = None
    st.session_state.messages.append({"text": f"Selected {doctor['name']}", "isBot": False})
    st.session_state.currentStep = conversationSteps["ASK_BED"]; _rerun()

def handleBedSelect(selection: Optional[Dict[str, Any]]):
    if selection:
        # Assign a serial if possible
        serial = _assign_bed_serial(selection["type"])
        sel = dict(selection)
        sel["serial"] = serial  # may be None if stock exhausted
        st.session_state.bedSelection = sel
        st.session_state.messages.append(
            {"text": f"Selected {selection['type']}" + (f' (Serial {serial})' if serial else ''), "isBot": False}
        )
    else:
        st.session_state.bedSelection = None
        st.session_state.messages.append({"text": "No bed needed.", "isBot": False})
    st.session_state.currentStep = conversationSteps["ASK_VITALS"]; _rerun()

def handleVitalsChoice(answer: str):
    ans = (answer or "").strip().lower()
    st.session_state.messages.append({"text": answer, "isBot": False})
    if ans in ("yes", "y"):
        vitals = get_recent_vitals()
        st.session_state.recentVitals = vitals
        pretty = json.dumps(vitals, indent=2)
        st.session_state.messages.append({"text": f"✅ Attached recent vitals:\n```\n{pretty}\n```", "isBot": True})
    else:
        st.session_state.recentVitals = None
        st.session_state.messages.append({"text": "👍 Proceeding without recent vitals.", "isBot": True})
    st.session_state.currentStep = conversationSteps["COLLECT_DETAILS"]; _rerun()

def handleDetail(detail_value: str):
    idx = st.session_state.currentDetailStep
    currentDetail = patientDetailSteps[idx]
    st.session_state.patientDetails[currentDetail["key"]] = detail_value
    st.session_state.messages.append({"text": detail_value, "isBot": False})

    if idx < len(patientDetailSteps) - 1:
        st.session_state.currentDetailStep += 1; _rerun(); return

    # Build appointment object (doctor-first or hospital-first)
    selected_doc = st.session_state.selectedDoctor
    selected_hosp = st.session_state.selectedHospital
    if selected_doc:
        hospital_name = selected_doc["chamber"]
        appointment_time = selected_doc["available_slots"][0]
        doctor_name = selected_doc["name"]
    else:
        hospital_name = (selected_hosp or {}).get("name", "")
        appointment_time = "11:00am-11:30am"  # default slot if hospital-only flow
        doctor_name = "(Hospital admission)"

    appt = {
        "patient_name": st.session_state.patientName,
        "booking_type": st.session_state.bookingType,
        "symptoms": st.session_state.symptoms,
        "doctor_name": doctor_name,
        "hospital_name": hospital_name,
        "appointment_date": datetime.now().isoformat(),
        "appointment_time": appointment_time,
        **st.session_state.patientDetails,
        "needs_bed": bool(st.session_state.bedSelection),
        "bed_type": st.session_state.bedSelection["type"] if st.session_state.bedSelection else None,
        "bed_details": st.session_state.bedSelection if st.session_state.bedSelection else None,
        "recent_vitals": st.session_state.recentVitals,
        "status": "confirmed",
    }

    st.session_state.finalAppointment = appt
    st.session_state.currentStep = conversationSteps["FINAL_CARD"]; _rerun()

# -------------------------------------------------------------------
if __name__ == "__main__":
    BookingPage()

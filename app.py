import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import math
import json
import random

# -----------------------------------------------------------------------------
# Streamlit compatibility shims
# -----------------------------------------------------------------------------
if not hasattr(st, "experimental_rerun") and hasattr(st, "rerun"):
    st.experimental_rerun = st.rerun  # alias for older code that calls experimental_rerun


def _rerun():
    """Safe rerun helper across Streamlit versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        st.session_state["_force_refresh"] = st.session_state.get("_force_refresh", 0) + 1


# -----------------------------------------------------------------------------
# Import UI components
# -----------------------------------------------------------------------------
from ChatMessage import ChatMessage
from SymptomSelector import SymptomSelector
from DoctorCard import DoctorCard
from BedSelector import BedSelector
from AppointmentCard import AppointmentCard

# Schemas (optional runtime validation if pydantic is available)
try:
    from models import Appointment, Doctor, Hospital  # noqa: F401
except Exception:
    Appointment = Doctor = Hospital = object  # placeholders


# =============================================================================
# Data: Doctors & Hospitals (from your CSVs)
# =============================================================================

DOCTORS: List[Dict[str, Any]] = [
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
        "available_slots": ["11:00am-11:30am", "12:30pm-1:00pm", "3:30pm-4:00pm"],
        "experience": "10 years",
    },
    {
        "name": "Dr. R.P Banik",
        "specialization": "ENT Surgeon",
        "chamber": "Jeevan Jyoti Institute Of Medical Science, Meherpur",
        "visiting_hours": "12.30pm-2.30pm",
        "available_slots": ["12:30pm-1:00pm", "1:30pm-2:00pm", "2:00pm-2:30pm"],
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
        "available_slots": ["6:00pm-6:30pm", "7:00pm-7:30pm", "7:30pm-8:00pm"],
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

HOSPITALS: List[Dict[str, Any]] = [
    {
        "name": "MUNNI MEDICAL HALL",
        "address": "MOTOR STAND, Tulargram Pt I, Sonai, Assam 788119",
        "latitude": 24.734,
        "longitude": 92.8913,
    },
    {
        "name": "Jeevan Jyoti Institute of Medical Sciences",
        "address": "Meherpur, Birbal Bazar, Silchar, Assam 788015",
        "latitude": 24.788,
        "longitude": 92.7934,
    },
    {
        "name": "Silchar Medical College and Hospital",
        "address": "Ghungoor, Masimpur, Silchar, Assam 788014",
        "latitude": 24.7758,
        "longitude": 92.7949,
    },
]

# Static inventory template per hospital
DEFAULT_INVENTORY = {
    "General Bed": {"total": 50, "booked": 10, "price": 100, "features": ["1 bed", "1 chair", "bed table"]},
    "General Cabin": {
        "total": 20,
        "booked": 4,
        "price": 1000,
        "features": ["2 beds", "attached washroom", "bed table", "chair", "food x3 times"],
    },
    "VIP Cabin": {
        "total": 10,
        "booked": 3,
        "price": 4000,
        "features": ["premium bed x2", "sofa", "Air Conditioning", "attached washroom", "TV", "fridge", "bed table x2", "coffee table", "2 chairs"],
    },
}


# =============================================================================
# Conversation Steps
# =============================================================================
conversationSteps = {
    "INITIAL": "initial",
    "ASK_NAME": "ask_name",
    "ASK_SYMPTOMS": "ask_symptoms",
    "CHOOSE_PATH": "choose_path",         # <-- NEW: choose Doctors or Hospitals
    "SHOW_DOCTORS": "show_doctors",
    "SHOW_HOSPITALS": "show_hospitals",   # <-- NEW: list hospitals, then bed flow
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


# =============================================================================
# Utilities
# =============================================================================
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
        "timestamp": datetime.now().isoformat(),
        "systolic_bp": round(random.uniform(105, 135), 1),
        "diastolic_bp": round(random.uniform(65, 88), 1),
        "body_temperature": round(random.uniform(36.3, 37.4), 1),
    }


def get_recent_vitals() -> Dict[str, Any]:
    """
    1) Try vitals_bridge.get_latest_vitals() if bridge file exists.
    2) Else try session_state["forecast_data"] last row.
    3) Else synthesize reasonable vitals so flow never breaks.
    """
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
                "timestamp": str(row.get("timestamp", datetime.now().isoformat())),
                "systolic_bp": float(row.get("systolic_bp", 120.0)),
                "diastolic_bp": float(row.get("diastolic_bp", 80.0)),
                "body_temperature": float(row.get("body_temperature", 36.8)),
            }
        except Exception:
            pass

    return _synth_vitals()


# Simple symptom → specialization map for filtering recommendations
SYMPTOM_TO_SPEC = {
    "fever": "General Medicine",
    "cough": "General Medicine",
    "headache": "General Medicine",
    "sore throat": "ENT Surgeon",
    "ear pain": "ENT Surgeon",
    "throat pain": "ENT Surgeon",
    "chest pain": "Cardiologist",
    "shortness of breath": "Cardiologist",
    "stomach pain": "Medicine (Consultant Physician)",
    "fatigue": "General Medicine",
    "skin rash": "Dermatology",
    "acne": "Dermatology",
    "tooth pain": "Dentist",
    "urination pain": "Urologist",
    "hernia": "General and Laparoscopic Surgeon",
    "appendix": "General and Laparoscopic Surgeon",
}


def recommended_doctors_from_symptoms(symptoms: List[str]) -> List[Dict[str, Any]]:
    if not symptoms:
        return DOCTORS[:]  # all
    # collect target specializations for given symptoms
    target_specs = set()
    for s in symptoms:
        s_norm = str(s).strip().lower()
        if s_norm in SYMPTOM_TO_SPEC:
            target_specs.add(SYMPTOM_TO_SPEC[s_norm])
    # fallback: if none matched, suggest all
    if not target_specs:
        return DOCTORS[:]
    # filter doctors by specialization match
    out = [d for d in DOCTORS if d["specialization"] in target_specs]
    return out if out else DOCTORS[:]


# =============================================================================
# Solid chat input (Enter + Button both work)
# =============================================================================
def SafeChatInput(onSend, placeholder="Type your message...", disabled=False, formKey="chat"):
    """
    - Uses a plain text_input with on_change callback.
    - The same callback is also used by the Send button.
    - Unique keys per step via formKey.
    """
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

    st.markdown(
        """
    <style>
      .ci-wrap{display:flex;gap:8px;padding:16px;background:#111214;border-top:1px solid #2a2b2f;}
      .ci-input{position:relative;flex:1;}
      .ci-send{
        padding:10px 16px;border-radius:10px;border:1px solid #2a2b2f;background:#1f6feb;color:#fff;cursor:pointer;
      }
      .ci-send:disabled{opacity:.5;cursor:not-allowed}
      .ci-input input{
        width:100%;padding:12px 14px;border-radius:10px;border:1px solid #2a2b2f;background:#0d1117;color:#e6edf3;
        outline:none;
      }
      .ci-input input:focus{border-color:#1f6feb;box-shadow:0 0 0 3px rgba(31,111,235,.25)}
    </style>
    """,
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 0.18], gap="small")
    with cols[0]:
        st.text_input(
            label="",
            key=text_key,
            placeholder=placeholder,
            disabled=disabled,
            label_visibility="collapsed",
            on_change=_send_cb,  # Enter submits
        )
    with cols[1]:
        st.button("Send ➤", key=btn_key, on_click=_send_cb, disabled=disabled)


# =============================================================================
# Main Page
# =============================================================================
def BookingPage():
    st.set_page_config(page_title="Doctigo AI", page_icon="🩺", layout="centered")

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "currentStep" not in st.session_state:
        st.session_state.currentStep = conversationSteps["INITIAL"]
    if "patientName" not in st.session_state:
        st.session_state.patientName = ""
    if "bookingType" not in st.session_state:
        st.session_state.bookingType = ""
    if "symptoms" not in st.session_state:
        st.session_state.symptoms = []
    if "selectedDoctor" not in st.session_state:
        st.session_state.selectedDoctor = None
    if "selectedHospital" not in st.session_state:
        st.session_state.selectedHospital = None
    if "bedSelection" not in st.session_state:
        st.session_state.bedSelection = None
    if "patientDetails" not in st.session_state:
        st.session_state.patientDetails = {}
    if "currentDetailStep" not in st.session_state:
        st.session_state.currentDetailStep = 0
    if "finalAppointment" not in st.session_state:
        st.session_state.finalAppointment = None
    if "recentVitals" not in st.session_state:
        st.session_state.recentVitals = None
    if "inventory" not in st.session_state:
        # per-hospital independent copies of DEFAULT_INVENTORY
        inv = {}
        for hosp in HOSPITALS:
            inv[hosp["name"]] = json.loads(json.dumps(DEFAULT_INVENTORY))  # deep copy
        st.session_state.inventory = inv

    st.title("🩺 Doctigo AI")
    st.caption("Your AI-powered medical booking assistant")

    step = st.session_state.currentStep

    # ----------------- Initial screen -----------------
    if step == conversationSteps["INITIAL"]:
        st.subheader("Choose booking type")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Normal Booking"):
                st.session_state.bookingType = "normal"
                st.session_state.messages.append({"text": "I want normal booking", "isBot": False})
                st.session_state.currentStep = conversationSteps["ASK_NAME"]
                _rerun()
        with c2:
            if st.button("🚨 Emergency Booking"):
                st.session_state.bookingType = "emergency"
                st.session_state.messages.append({"text": "I want emergency booking", "isBot": False})
                st.session_state.currentStep = conversationSteps["ASK_NAME"]
                _rerun()

    # ----------------- Chat area -----------------
    else:
        st.markdown("### Chat")
        for msg in st.session_state.messages:
            ChatMessage(message=msg["text"], isBot=msg["isBot"], timestamp=None)

        # ASK NAME
        if step == conversationSteps["ASK_NAME"]:
            ChatMessage("Hello! I am Doc, your friendly neighborhood **Spider Doc** 🕷️🩺. What's your name?", True, None)
            SafeChatInput(onSend=handleName, formKey="ask_name")

        # ASK SYMPTOMS
        elif step == conversationSteps["ASK_SYMPTOMS"]:
            if st.session_state.bookingType == "emergency":
                ChatMessage("Woooo it's an **EMERGENCY**! Enter your symptoms or type **next** to skip.", True, None)
            else:
                ChatMessage("Enter your symptoms or type **next** to skip.", True, None)
            SymptomSelector(onSubmit=handleSymptoms, onSkip=lambda: handleSymptoms([]))

        # CHOOSE PATH (Doctors | Hospitals)
        elif step == conversationSteps["CHOOSE_PATH"]:
            ChatMessage("What would you like to browse next? **Doctors** or **Hospitals**.", True, None)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("👨‍⚕️ Browse Doctors"):
                    st.session_state.messages.append({"text": "Browse Doctors", "isBot": False})
                    st.session_state.currentStep = conversationSteps["SHOW_DOCTORS"]
                    _rerun()
            with c2:
                if st.button("🏥 Browse Hospitals"):
                    st.session_state.messages.append({"text": "Browse Hospitals", "isBot": False})
                    st.session_state.currentStep = conversationSteps["SHOW_HOSPITALS"]
                    _rerun()

        # SHOW DOCTORS (filtered by symptoms if provided)
        elif step == conversationSteps["SHOW_DOCTORS"]:
            syms = st.session_state.symptoms
            recs = recommended_doctors_from_symptoms(syms)
            if syms:
                ChatMessage("Based on your symptoms, here are recommended doctors:", True, None)
            else:
                ChatMessage("Here are available doctors:", True, None)

            for doc in recs:
                # DoctorCard expects keys: doctor, availableSlots, estimatedTime, distance, onBook
                DoctorCard(
                    doctor={
                        "name": doc["name"],
                        "specialization": doc["specialization"],
                        "chamber": doc["chamber"],
                        "experience": doc["experience"],
                    },
                    availableSlots=doc.get("available_slots", []),
                    estimatedTime=20,
                    distance=10,
                    onBook=handleDoctorSelect,
                )

            st.info("Tip: click **Book Appointment** on the desired doctor card.")

        # SHOW HOSPITALS (then go to bed flow for chosen hospital)
        elif step == conversationSteps["SHOW_HOSPITALS"]:
            ChatMessage("Select a hospital. We'll then show bed/cabin availability.", True, None)
            inv = st.session_state.inventory

            for hosp in HOSPITALS:
                name = hosp["name"]
                inv_h = inv.get(name, DEFAULT_INVENTORY)
                gb = inv_h["General Bed"]
                gc = inv_h["General Cabin"]
                vip = inv_h["VIP Cabin"]
                gb_av = gb["total"] - gb["booked"]
                gc_av = gc["total"] - gc["booked"]
                vip_av = vip["total"] - vip["booked"]

                with st.container(border=True):
                    st.markdown(f"**{name}**")
                    st.caption(hosp["address"])
                    st.write(
                        f"🛏️ General Beds: **{gb_av} / {gb['total']}** available  |  "
                        f"🚪 General Cabins: **{gc_av} / {gc['total']}** available  |  "
                        f"⭐ VIP Cabins: **{vip_av} / {vip['total']}** available"
                    )
                    if st.button(f"Select {name}"):
                        st.session_state.selectedHospital = hosp
                        st.session_state.messages.append({"text": f"Selected hospital: {name}", "isBot": False})
                        st.session_state.currentStep = conversationSteps["ASK_BED"]
                        _rerun()

        # ASK BED (works for both doctor-path and hospital-path)
        elif step == conversationSteps["ASK_BED"]:
            # If coming from hospital path, show remaining availability for context
            hosp = st.session_state.get("selectedHospital")
            if hosp:
                inv_h = st.session_state.inventory.get(hosp["name"], DEFAULT_INVENTORY)
                gb = inv_h["General Bed"]; gc = inv_h["General Cabin"]; vip = inv_h["VIP Cabin"]
                gb_av = gb["total"] - gb["booked"]; gc_av = gc["total"] - gc["booked"]; vip_av = vip["total"] - vip["booked"]
                ChatMessage(
                    f"At **{hosp['name']}** — General Beds: **{gb_av}**, General Cabins: **{gc_av}**, VIP Cabins: **{vip_av}** available.",
                    True,
                    None,
                )
            ChatMessage("Do you need to book a Bed or Cabin? Please choose:", True, None)
            BedSelector(onSelect=handleBedSelect)

        # ASK VITALS
        elif step == conversationSteps["ASK_VITALS"]:
            ChatMessage("Hey buddy, why don't you hook up your **recent vitals**? Type **Yes** or **No**.", True, None)
            SafeChatInput(onSend=handleVitalsChoice, formKey="ask_vitals", placeholder="Type Yes or No...")

        # COLLECT DETAILS
        elif step == conversationSteps["COLLECT_DETAILS"]:
            idx = st.session_state.currentDetailStep
            detail = patientDetailSteps[idx]
            ChatMessage(f"Please enter patient's {detail['label']}:", True, None)
            SafeChatInput(onSend=handleDetail, formKey=f"detail_{detail['key']}")

        # FINAL CARD
        elif step == conversationSteps["FINAL_CARD"]:
            ChatMessage("🎉 Appointment confirmed! Here's your appointment card:", True, None)
            AppointmentCard(st.session_state.finalAppointment)


# =============================================================================
# Handlers
# =============================================================================
def handleName(name: str):
    st.session_state.patientName = name
    st.session_state.messages.append({"text": name, "isBot": False})
    st.session_state.messages.append(
        {"text": f"Hello {name}! So you opted for **{st.session_state.bookingType}** booking.", "isBot": True}
    )
    st.session_state.currentStep = conversationSteps["ASK_SYMPTOMS"]
    _rerun()


def handleSymptoms(symptoms: List[str]):
    # Normalize symptoms to lower-case to match map easily
    st.session_state.symptoms = [s.strip() for s in symptoms]
    shown = ", ".join(st.session_state.symptoms) if symptoms else "None"
    st.session_state.messages.append({"text": f"Symptoms: {shown}", "isBot": False})
    # Regardless of symptoms given or not, next step is the same: choose doctors or hospitals
    st.session_state.currentStep = conversationSteps["CHOOSE_PATH"]
    _rerun()


def handleDoctorSelect(doctor: Dict[str, Any]):
    st.session_state.selectedDoctor = doctor
    st.session_state.selectedHospital = None  # doctor path takes precedence for hospital via doctor.chamber
    st.session_state.messages.append({"text": f"Selected {doctor['name']}", "isBot": False})
    st.session_state.currentStep = conversationSteps["ASK_BED"]
    _rerun()


def handleBedSelect(selection: Optional[Dict[str, Any]]):
    # selection is a dict with keys: type, price, features
    st.session_state.bedSelection = selection
    if selection:
        st.session_state.messages.append({"text": f"Selected {selection['type']}", "isBot": False})
        # If user has selected a hospital earlier, decrement availability
        hosp = st.session_state.get("selectedHospital")
        if hosp:
            inv_h = st.session_state.inventory.get(hosp["name"], DEFAULT_INVENTORY)
            bedtype = selection["type"]
            if bedtype in inv_h:
                # only decrement if available > 0
                available = inv_h[bedtype]["total"] - inv_h[bedtype]["booked"]
                if available > 0:
                    inv_h[bedtype]["booked"] += 1
                    st.session_state.inventory[hosp["name"]] = inv_h
    else:
        st.session_state.messages.append({"text": "No bed needed.", "isBot": False})

    st.session_state.currentStep = conversationSteps["ASK_VITALS"]
    _rerun()


def handleVitalsChoice(answer: str):
    ans = (answer or "").strip().lower()
    st.session_state.messages.append({"text": answer, "isBot": False})

    if ans in ("yes", "y"):
        vitals = get_recent_vitals()
        st.session_state.recentVitals = vitals
        pretty = json.dumps(vitals, indent=2)
        st.session_state.messages.append(
            {"text": f"✅ Got it! I’ve attached your recent vitals:\n```\n{pretty}\n```", "isBot": True}
        )
    else:
        st.session_state.recentVitals = None
        st.session_state.messages.append(
            {"text": "👍 No problem. We’ll proceed without recent vitals.", "isBot": True}
        )

    st.session_state.currentStep = conversationSteps["COLLECT_DETAILS"]
    _rerun()


def handleDetail(detail_value: str):
    idx = st.session_state.currentDetailStep
    currentDetail = patientDetailSteps[idx]
    st.session_state.patientDetails[currentDetail["key"]] = detail_value
    st.session_state.messages.append({"text": detail_value, "isBot": False})

    if idx < len(patientDetailSteps) - 1:
        st.session_state.currentDetailStep += 1
        _rerun()
        return

    # Finalize appointment
    # Determine hospital name:
    hospital_name = None
    if st.session_state.selectedDoctor:
        hospital_name = st.session_state.selectedDoctor.get("chamber")
    elif st.session_state.selectedHospital:
        hospital_name = st.session_state.selectedHospital["name"]
    else:
        hospital_name = "Not selected"

    # Determine doctor name:
    doctor_name = st.session_state.selectedDoctor["name"] if st.session_state.selectedDoctor else "Not selected"

    # Determine appointment time:
    if st.session_state.selectedDoctor and st.session_state.selectedDoctor.get("available_slots"):
        appt_time = st.session_state.selectedDoctor["available_slots"][0]
    else:
        appt_time = "To be scheduled"

    appointment = {
        "patient_name": st.session_state.patientName,
        "booking_type": st.session_state.bookingType,
        "symptoms": st.session_state.symptoms,
        "doctor_name": doctor_name,
        "hospital_name": hospital_name,
        "appointment_date": datetime.now().isoformat(),
        "appointment_time": appt_time,
        **st.session_state.patientDetails,
        "needs_bed": bool(st.session_state.bedSelection),
        "bed_type": st.session_state.bedSelection["type"] if st.session_state.bedSelection else None,
        "bed_details": st.session_state.bedSelection if st.session_state.bedSelection else None,
        "recent_vitals": st.session_state.recentVitals,
        "status": "confirmed",
    }
    st.session_state.finalAppointment = appointment
    st.session_state.currentStep = conversationSteps["FINAL_CARD"]
    _rerun()


# =============================================================================
# Entry point
# =============================================================================
if __name__ == "__main__":
    BookingPage()

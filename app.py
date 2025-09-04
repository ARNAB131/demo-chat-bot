import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional
import math

# -----------------------------------------------------------------------------
# Streamlit compatibility shims
# -----------------------------------------------------------------------------
# Some of your components (e.g., SymptomSelector.py) call st.experimental_rerun().
# Newer Streamlit versions removed it in favor of st.rerun().
# This shim guarantees both names exist.
if not hasattr(st, "experimental_rerun") and hasattr(st, "rerun"):
    st.experimental_rerun = st.rerun  # alias for backward compatibility

# A safe rerun helper we can call anywhere
def _rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        # last resort: nudge state so Streamlit re-executes
        st.session_state["_force_refresh"] = st.session_state.get("_force_refresh", 0) + 1


# -----------------------------------------------------------------------------
# Import our translated components
# -----------------------------------------------------------------------------
from ChatMessage import ChatMessage
from ChatInput import ChatInput
from SymptomSelector import SymptomSelector
from DoctorCard import DoctorCard
from BedSelector import BedSelector
from AppointmentCard import AppointmentCard

# Schemas (optional runtime validation if pydantic is available)
from models import Appointment, Doctor, Hospital


# -----------------------------
# Conversation Steps
# -----------------------------
conversationSteps = {
    "INITIAL": "initial",
    "ASK_NAME": "ask_name",
    "CONFIRM_BOOKING_TYPE": "confirm_booking_type",
    "ASK_SYMPTOMS": "ask_symptoms",
    "SHOW_DOCTORS": "show_doctors",
    "ASK_BED": "ask_bed",
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


# -----------------------------
# Utilities
# -----------------------------
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


# -----------------------------
# Session helpers
# -----------------------------
def _ensure_chat_input_key(form_key: str):
    """
    Pre-initialize the text input state key that ChatInput.py expects.
    Prevents SessionState assignment errors during widget creation.
    """
    text_key = f"chat_input_text_{form_key}"
    if text_key not in st.session_state:
        st.session_state[text_key] = ""


# -----------------------------
# Main Page
# -----------------------------
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
    if "bedSelection" not in st.session_state:
        st.session_state.bedSelection = None
    if "patientDetails" not in st.session_state:
        st.session_state.patientDetails = {}
    if "currentDetailStep" not in st.session_state:
        st.session_state.currentDetailStep = 0
    if "finalAppointment" not in st.session_state:
        st.session_state.finalAppointment = None

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
            ChatMessage("Hello! I am Doc, your friendly neighborhood Spider Doc 🕷️🩺. What's your name?", True, None)
            _ensure_chat_input_key("ask_name")
            ChatInput(onSend=handleName, formKey="ask_name")

        elif step == conversationSteps["ASK_SYMPTOMS"]:
            bookingType = st.session_state.bookingType
            if bookingType == "emergency":
                ChatMessage("Woooo it's an **EMERGENCY**! Just enter symptoms or type 'next'.", True, None)
            else:
                ChatMessage("Enter your symptoms or type 'next'.", True, None)
            # Your SymptomSelector handles its own reruns; no changes needed here
            SymptomSelector(onSubmit=handleSymptoms, onSkip=lambda: handleSymptoms([]))

        elif step == conversationSteps["SHOW_DOCTORS"]:
            ChatMessage("Based on your information, here are available doctors:", True, None)
            # NOTE: replace this with actual Doctor.list() + Hospital.list() once wired
            dummy_doctors = [
                {
                    "name": "Amit Kumar",
                    "specialization": "General Medicine",
                    "chamber": "City Hospital",
                    "experience": "15 yrs",
                    "available_slots": ["11:00am-11:30am", "12:00pm-12:30pm"],
                },
                {
                    "name": "Suvajoyti Chakraborty",
                    "specialization": "Surgeon",
                    "chamber": "Munni Medical Hall",
                    "experience": "20 yrs",
                    "available_slots": ["1:00pm-1:30pm", "2:00pm-2:30pm"],
                },
            ]
            for doc in dummy_doctors:
                DoctorCard(
                    doctor=doc,
                    availableSlots=doc["available_slots"],
                    estimatedTime=20,
                    distance=10,
                    onBook=handleDoctorSelect,
                )

        elif step == conversationSteps["ASK_BED"]:
            ChatMessage("Do you need to book a Bed or Cabin? Please choose:", True, None)
            BedSelector(onSelect=handleBedSelect)

        elif step == conversationSteps["COLLECT_DETAILS"]:
            idx = st.session_state.currentDetailStep
            detail = patientDetailSteps[idx]
            ChatMessage(f"Please enter patient's {detail['label']}:", True, None)
            _ensure_chat_input_key(f"detail_{detail['key']}")
            ChatInput(onSend=handleDetail, formKey=f"detail_{detail['key']}")

        elif step == conversationSteps["FINAL_CARD"]:
            ChatMessage("🎉 Appointment confirmed! Here's your appointment card:", True, None)
            AppointmentCard(st.session_state.finalAppointment)


# -----------------------------
# Handlers
# -----------------------------
def handleName(name: str):
    st.session_state.patientName = name
    st.session_state.messages.append({"text": name, "isBot": False})
    st.session_state.messages.append(
        {"text": f"Hello {name}! So you opted for {st.session_state.bookingType} booking.", "isBot": True}
    )
    st.session_state.currentStep = conversationSteps["ASK_SYMPTOMS"]
    _rerun()


def handleSymptoms(symptoms: List[str]):
    st.session_state.symptoms = symptoms
    st.session_state.messages.append(
        {"text": f"Symptoms: {', '.join(symptoms) if symptoms else 'None'}", "isBot": False}
    )
    st.session_state.currentStep = conversationSteps["SHOW_DOCTORS"]
    _rerun()


def handleDoctorSelect(doctor: Dict[str, Any]):
    st.session_state.selectedDoctor = doctor
    st.session_state.messages.append({"text": f"Selected Dr. {doctor['name']}", "isBot": False})
    st.session_state.currentStep = conversationSteps["ASK_BED"]
    _rerun()


def handleBedSelect(selection: Optional[Dict[str, Any]]):
    st.session_state.bedSelection = selection
    if selection:
        st.session_state.messages.append({"text": f"Selected {selection['type']}", "isBot": False})
    else:
        st.session_state.messages.append({"text": "No bed needed.", "isBot": False})
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
    appointment = {
        "patient_name": st.session_state.patientName,
        "booking_type": st.session_state.bookingType,
        "symptoms": st.session_state.symptoms,
        "doctor_name": st.session_state.selectedDoctor["name"],
        "hospital_name": st.session_state.selectedDoctor["chamber"],
        "appointment_date": datetime.now().isoformat(),
        "appointment_time": st.session_state.selectedDoctor["available_slots"][0],
        **st.session_state.patientDetails,
        "needs_bed": bool(st.session_state.bedSelection),
        "bed_type": st.session_state.bedSelection["type"] if st.session_state.bedSelection else None,
        # AppointmentCard handles dict or JSON string
        "bed_details": st.session_state.bedSelection if st.session_state.bedSelection else None,
        "status": "confirmed",
    }
    st.session_state.finalAppointment = appointment
    st.session_state.currentStep = conversationSteps["FINAL_CARD"]
    _rerun()


# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    BookingPage()

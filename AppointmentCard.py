# AppointmentCard.py
from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


def _pdfsafe(s) -> str:
    """Make text safe for FPDF core fonts (latin-1)."""
    if s is None:
        return ""
    s = str(s)
    return (
        s.replace("₹", "Rs ")
        .replace("–", "-")
        .replace("—", "-")
        .replace("•", "*")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("‘", "'")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _fmt_list(lst: Optional[List[str]]) -> str:
    if not lst:
        return ""
    return ", ".join([str(x) for x in lst])


def _generate_pdf(appointment: Dict[str, Any]) -> Optional[io.BytesIO]:
    """Return a BytesIO PDF receipt if fpdf is available; otherwise None."""
    try:
        from fpdf import FPDF
    except Exception:
        return None

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, _pdfsafe("Doctigo Appointment Receipt"), ln=True, align="C")

    hosp = appointment.get("hospital_name") or "—"
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, _pdfsafe(f"Hospital: {hosp}"), ln=True)
    pdf.ln(2)

    # Patient Details
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, _pdfsafe("Patient Details"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, _pdfsafe(f"Name: {appointment.get('patient_name','')}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Phone: {appointment.get('patient_phone','')}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Gender: {appointment.get('patient_gender','')}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Age: {appointment.get('patient_age','')}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Email: {appointment.get('patient_email','')}"), ln=True)
    pdf.multi_cell(0, 7, _pdfsafe(f"Address: {appointment.get('patient_address','')}"))
    pdf.ln(2)

    # Appointment Details
    appt_dt = appointment.get("appointment_date")
    try:
        appt_date_str = datetime.fromisoformat(appt_dt).strftime("%d %B %Y, %I:%M %p") if appt_dt else "—"
    except Exception:
        appt_date_str = appt_dt or "—"

    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, _pdfsafe("Appointment Details"), ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 7, _pdfsafe(f"Doctor: {appointment.get('doctor_name','')}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Booking Type: {appointment.get('booking_type','').title() if appointment.get('booking_type') else '—'}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Date/Booked: {appt_date_str}"), ln=True)
    pdf.cell(0, 7, _pdfsafe(f"Time Slot: {appointment.get('appointment_time','—')}"), ln=True)

    syms = appointment.get("symptoms") or []
    if syms:
        pdf.multi_cell(0, 7, _pdfsafe(f"Symptoms: {', '.join([str(s) for s in syms])}"))
    pdf.ln(2)

    # Travel (optional)
    dist = appointment.get("distance_km", None)
    eta = appointment.get("estimated_travel_time", None)
    if dist is not None or eta is not None:
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, _pdfsafe("Travel (Estimated)"), ln=True)
        pdf.set_font("Arial", "", 12)
        tline = []
        if dist is not None:
            try:
                tline.append(f"Distance: {float(dist):.1f} km")
            except Exception:
                tline.append(f"Distance: {dist}")
        if eta is not None:
            tline.append(f"ETA: ~{eta} min")
        pdf.cell(0, 7, _pdfsafe(" | ".join(tline) if tline else "—"), ln=True)
        pdf.ln(2)

    # Bed/Cabin
    if appointment.get("needs_bed"):
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, _pdfsafe("Bed/Cabin"), ln=True)
        pdf.set_font("Arial", "", 12)

        bed_type = appointment.get("bed_type") or "—"
        bed_unit = appointment.get("bed_unit_id") or "—"
        bed_serial = appointment.get("bed_serial")
        bd = appointment.get("bed_details") or {}

        price = bd.get("price", "—")
        features = _fmt_list(bd.get("features"))

        pdf.cell(0, 7, _pdfsafe(f"Type: {bed_type}"), ln=True)
        pdf.cell(0, 7, _pdfsafe(f"Assigned Unit: {bed_unit}"), ln=True)
        pdf.cell(0, 7, _pdfsafe(f"Serial #: {bed_serial if bed_serial is not None else '—'}"), ln=True)
        pdf.cell(0, 7, _pdfsafe(f"Price per night: Rs {price}"), ln=True)
        if features:
            pdf.multi_cell(0, 7, _pdfsafe(f"Features: {features}"))
        pdf.ln(2)

    # Recent Vitals (optional)
    rv = appointment.get("recent_vitals")
    if rv:
        pdf.set_font("Arial", "B", 13)
        pdf.cell(0, 8, _pdfsafe("Recent Vitals (User-provided)"), ln=True)
        pdf.set_font("Arial", "", 12)
        try:
            pdf.cell(0, 7, _pdfsafe(f"Timestamp: {rv.get('timestamp','')}"), ln=True)
            pdf.cell(0, 7, _pdfsafe(f"Systolic BP: {rv.get('systolic_bp','')}"), ln=True)
            pdf.cell(0, 7, _pdfsafe(f"Diastolic BP: {rv.get('diastolic_bp','')}"), ln=True)
            pdf.cell(0, 7, _pdfsafe(f"Body Temperature: {rv.get('body_temperature','')} °C"), ln=True)
        except Exception:
            pdf.multi_cell(0, 7, _pdfsafe(str(rv)))
        pdf.ln(2)

    # Footer
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(120)
    pdf.cell(0, 8, _pdfsafe("This receipt is auto-generated by Doctigo AI."), ln=True, align="C")
    pdf.set_text_color(0)

    try:
        bytes_out = pdf.output(dest="S").encode("latin-1")
        return io.BytesIO(bytes_out)
    except Exception:
        return None


def AppointmentCard(appointment: Dict[str, Any]):
    """
    Streamlit card that shows a confirmed appointment and exposes a PDF download.

    The appointment dict is expected to include (at least):
      - patient_* fields
      - doctor_name, hospital_name
      - appointment_date (iso), appointment_time
      - needs_bed (bool), bed_type (str|None)
      - bed_unit_id (str|None), bed_serial (int|None)
      - bed_details (dict) with keys: type, price, features, unit_id, serial
      - recent_vitals (optional dict)
    """
    if not isinstance(appointment, dict) or not appointment:
        st.info("No appointment to show yet.")
        return

    # Derived / formats
    try:
        appt_dt = appointment.get("appointment_date")
        appt_date = datetime.fromisoformat(appt_dt) if appt_dt else None
    except Exception:
        appt_date = None

    date_display = appt_date.strftime("%d %b %Y, %I:%M %p") if appt_date else "—"
    time_slot = appointment.get("appointment_time") or "—"
    booking_type = (appointment.get("booking_type") or "").title() or "—"

    # Card UI
    with st.container(border=True):
        st.markdown("### ✅ Appointment Confirmed")
        st.caption(f"**Type:** {booking_type}")

        # Top grid
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"**Patient:** {appointment.get('patient_name','—')}")
            st.markdown(f"**Phone:** {appointment.get('patient_phone','—')}")
            st.markdown(f"**Gender/Age:** {appointment.get('patient_gender','—')} / {appointment.get('patient_age','—')}")
            st.markdown(f"**Email:** {appointment.get('patient_email','—')}")
            st.markdown(f"**Address:** {appointment.get('patient_address','—')}")
        with c2:
            st.markdown(f"**Doctor:** {appointment.get('doctor_name','—')}")
            st.markdown(f"**Hospital:** {appointment.get('hospital_name','—')}")
            st.markdown(f"**Booked On:** {date_display}")
            st.markdown(f"**Time Slot:** {time_slot}")

            # Travel (optional)
            dist = appointment.get("distance_km", None)
            eta = appointment.get("estimated_travel_time", None)
            if dist is not None or eta is not None:
                line = []
                if dist is not None:
                    try:
                        line.append(f"{float(dist):.1f} km")
                    except Exception:
                        line.append(str(dist))
                if eta is not None:
                    line.append(f"~{eta} min travel")
                st.caption(" | ".join(line))

        # Symptoms
        syms = appointment.get("symptoms") or []
        if syms:
            st.markdown("**Symptoms:** " + ", ".join([str(s) for s in syms]))

        st.markdown("---")

        # Bed/Cabin section (shows Unit ID + Serial prominently)
        if appointment.get("needs_bed"):
            bd = appointment.get("bed_details") or {}
            btype = appointment.get("bed_type") or bd.get("type") or "—"
            unit_id = appointment.get("bed_unit_id") or bd.get("unit_id") or "—"
            serial = appointment.get("bed_serial") or bd.get("serial")
            price = bd.get("price", "—")
            features = bd.get("features") or []

            st.markdown("#### 🛏️ Bed/Cabin")
            st.markdown(
                f"- **Type:** {btype}\n"
                f"- **Assigned Unit:** `{unit_id}`\n"
                f"- **Serial #:** `{serial if serial is not None else '—'}`\n"
                f"- **Price/Night:** Rs {price}\n"
                + (f"- **Features:** {', '.join([str(f) for f in features])}" if features else "")
            )
        else:
            st.caption("No bed/cabin reserved.")

        # Recent Vitals (optional)
        rv = appointment.get("recent_vitals")
        if rv:
            st.markdown("#### ❤️ Recent Vitals (provided)")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Systolic", f"{rv.get('systolic_bp','—')}")
            with c2:
                st.metric("Diastolic", f"{rv.get('diastolic_bp','—')}")
            with c3:
                st.metric("Temp (°C)", f"{rv.get('body_temperature','—')}")
            with c4:
                ts = rv.get("timestamp", "—")
                st.caption(f"Updated: {ts}")

        st.markdown("---")

        # Download actions
        pdf_buf = _generate_pdf(appointment)
        colA, colB = st.columns(2)
        with colA:
            if pdf_buf:
                st.download_button(
                    "⬇️ Download PDF Receipt",
                    data=pdf_buf,
                    file_name="doctigo_appointment_receipt.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.info("PDF module not available; offering JSON download instead.")
        with colB:
            st.download_button(
                "⬇️ Download Appointment (JSON)",
                data=st.session_state.get("finalAppointment", appointment).__repr__().encode("utf-8"),
                file_name="doctigo_appointment.json",
                mime="application/json",
                use_container_width=True,
            )

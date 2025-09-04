# AppointmentCard.py
# Python translation of AppointmentCard.jsx (names unchanged)
# Components preserved: PrintReceipt, AppointmentCard
# Notes:
# - window.print() isn't available in Streamlit. We generate a print-friendly HTML
#   and expose it via st.download_button to mimic "Download PDF Receipt" behavior.

from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime
import json
import streamlit as st


def _format_date_iso_to_display(dt_str: Optional[str]) -> str:
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return dt_str


def _format_date_iso_long(dt_str: Optional[str]) -> str:
    if not dt_str:
        return ""
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%-d %B %Y")
    except Exception:
        return _format_date_iso_to_display(dt_str)


def _safe_float(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def PrintReceipt(appointment: Dict[str, Any], bedDetails: Optional[Dict[str, Any]]):
    """Print-only section (mirrors JSX PrintReceipt). In Streamlit we render it
    and also produce a downloadable HTML below from AppointmentCard()."""
    # Style for print block
    st.markdown("""
    <style>
      .pr-wrap{font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans","Liberation Sans",Arial,"Apple Color Emoji","Segoe UI Emoji";color:#1f2937;padding:24px;background:#fff;}
      .pr-title{font-size:28px;font-weight:800;color:#2563eb;text-align:center;margin-bottom:6px;}
      .pr-sub{font-size:16px;color:#6b7280;text-align:center;margin-bottom:20px;}
      .pr-h2{font-size:18px;font-weight:700;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin:18px 0 12px;}
      .pr-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
      .pr-li{margin-left:18px;list-style:disc;}
      .pr-foot{color:#6b7280;text-align:center;margin-top:28px;font-size:14px;}
      /* Keep visible in Streamlit; printing is done via downloaded HTML */
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="pr-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="pr-title">Doctigo Booking Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="pr-sub">{appointment.get("hospital_name","")}</div>', unsafe_allow_html=True)

    # Patient Details
    st.markdown('<div class="pr-h2">Patient Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="pr-grid">', unsafe_allow_html=True)
    st.markdown(f"<div><b>Patient Name:</b> {appointment.get('patient_name','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Age:</b> {appointment.get('patient_age','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Gender:</b> {appointment.get('patient_gender','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Phone:</b> {appointment.get('patient_phone','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='col-span-2'><b>Email:</b> {appointment.get('patient_email','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='col-span-2'><b>Address:</b> {appointment.get('patient_address','')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Appointment Details
    st.markdown('<div class="pr-h2">Appointment Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="pr-grid">', unsafe_allow_html=True)
    st.markdown(f"<div><b>Doctor:</b> Dr. {appointment.get('doctor_name','')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Booking Type:</b> {str(appointment.get('booking_type','')).capitalize()}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Date:</b> {_format_date_iso_to_display(appointment.get('appointment_date'))}</div>", unsafe_allow_html=True)
    st.markdown(f"<div><b>Time:</b> {appointment.get('appointment_time','')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Symptoms
    symptoms = appointment.get("symptoms") or []
    if isinstance(symptoms, list) and len(symptoms) > 0:
        st.markdown("<div><b>Symptoms:</b> " + ", ".join(symptoms) + "</div>", unsafe_allow_html=True)

    # Bed/Cabin
    if appointment.get("needs_bed") and bedDetails:
        st.markdown('<div class="pr-h2">Bed/Cabin Details</div>', unsafe_allow_html=True)
        st.markdown(f"<div><b>Type:</b> {appointment.get('bed_type','')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div><b>Price per night:</b> ₹{bedDetails.get('price','')}</div>", unsafe_allow_html=True)
        feats = bedDetails.get("features") or []
        if feats:
            st.markdown("<div><b>Features:</b></div>", unsafe_allow_html=True)
            for f in feats:
                st.markdown(f"<div class='pr-li'>{f}</div>", unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="pr-foot">This receipt was auto-generated by Doctigo AI.<br/>Issued on: ' +
                datetime.now().strftime("%d/%m/%Y, %I:%M %p") + '</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def _build_print_html(appointment: Dict[str, Any], bedDetails: Optional[Dict[str, Any]]) -> str:
    """Generate a standalone HTML for printing/downloading (mirrors PrintReceipt)."""
    def esc(x: Any) -> str:
        return "" if x is None else str(x)

    def date_short(x: Optional[str]) -> str:
        return _format_date_iso_to_display(x)

    issued = datetime.now().strftime("%d/%m/%Y, %I:%M %p")

    feats_ul = ""
    if appointment.get("needs_bed") and bedDetails and bedDetails.get("features"):
        lis = "\n".join(f"<li>{esc(f)}</li>" for f in bedDetails["features"])
        feats_ul = f"""
        <div style="font-weight:600;margin-top:8px;">Features:</div>
        <ul style="margin:4px 0 0 18px; color:#374151;">{lis}</ul>
        """

    symptoms = appointment.get("symptoms") or []
    symptoms_html = ""
    if isinstance(symptoms, list) and symptoms:
        symptoms_html = f"<div><strong>Symptoms:</strong> {', '.join(map(esc, symptoms))}</div>"

    bed_html = ""
    if appointment.get("needs_bed") and bedDetails:
        bed_html = f"""
        <section style="margin-top:16px;">
          <h2 style="font-size:18px;font-weight:700;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin:18px 0 12px;">Bed/Cabin Details</h2>
          <div><strong>Type:</strong> {esc(appointment.get('bed_type',''))}</div>
          <div><strong>Price per night:</strong> ₹{esc(bedDetails.get('price',''))}</div>
          {feats_ul}
        </section>
        """

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Doctigo Booking Summary</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue",
            "Noto Sans", "Liberation Sans", Arial, "Apple Color Emoji", "Segoe UI Emoji"; color:#1f2937; }}
    .wrap {{ padding:24px; max-width:800px; margin:0 auto; }}
    .title {{ font-size:28px; font-weight:800; color:#2563eb; text-align:center; margin-bottom:6px; }}
    .sub {{ font-size:16px; color:#6b7280; text-align:center; margin-bottom:20px; }}
    .h2 {{ font-size:18px; font-weight:700; border-bottom:2px solid #e5e7eb; padding-bottom:8px; margin:18px 0 12px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
    .foot {{ color:#6b7280; text-align:center; margin-top:28px; font-size:14px; }}
    @media print {{
      .no-print {{ display:none; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1 class="title">Doctigo Booking Summary</h1>
      <p class="sub">{esc(appointment.get('hospital_name',''))}</p>
    </header>

    <section>
      <h2 class="h2">Patient Details</h2>
      <div class="grid">
        <div><strong>Patient Name:</strong> {esc(appointment.get('patient_name',''))}</div>
        <div><strong>Age:</strong> {esc(appointment.get('patient_age',''))}</div>
        <div><strong>Gender:</strong> {esc(appointment.get('patient_gender',''))}</div>
        <div><strong>Phone:</strong> {esc(appointment.get('patient_phone',''))}</div>
        <div style="grid-column:1/-1;"><strong>Email:</strong> {esc(appointment.get('patient_email',''))}</div>
        <div style="grid-column:1/-1;"><strong>Address:</strong> {esc(appointment.get('patient_address',''))}</div>
      </div>
    </section>

    <section>
      <h2 class="h2">Appointment Details</h2>
      <div class="grid">
        <div><strong>Doctor:</strong> Dr. {esc(appointment.get('doctor_name',''))}</div>
        <div><strong>Booking Type:</strong> {esc(str(appointment.get('booking_type','')).capitalize())}</div>
        <div><strong>Date:</strong> {date_short(appointment.get('appointment_date'))}</div>
        <div><strong>Time:</strong> {esc(appointment.get('appointment_time',''))}</div>
      </div>
      {symptoms_html}
    </section>

    {bed_html}

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
</html>
"""
    return html


def AppointmentCard(appointment: Dict[str, Any]):
    """Main confirmation card with download button, mirroring the JSX layout."""
    # Parse bed_details JSON (if present)
    bedDetails: Optional[Dict[str, Any]] = None
    raw_bed = appointment.get("bed_details")
    if isinstance(raw_bed, str) and raw_bed.strip():
        try:
            bedDetails = json.loads(raw_bed)
        except Exception:
            bedDetails = None

    # --- Header / gradient card styling (approximation of the original) ---
    st.markdown("""
    <style>
      .ac-card{border:2px solid #bbf7d0;border-radius:14px;background:linear-gradient(135deg,#f0fdf4,#eff6ff);box-shadow:0 6px 18px rgba(0,0,0,.06);max-width:480px;margin:0 auto;}
      .ac-head{padding:16px 12px;border-top-left-radius:12px;border-top-right-radius:12px;background:linear-gradient(90deg,#22c55e,#3b82f6);color:#fff;text-align:center;}
      .ac-title{font-weight:700;font-size:18px;display:flex;align-items:center;justify-content:center;gap:8px;}
      .ac-badge{display:inline-block;margin-top:8px;background:#ffffff;color:#16a34a;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:600;}
      .ac-body{padding:18px;display:flex;flex-direction:column;gap:12px;}
      .ac-row{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:10px;}
      .ac-name{font-weight:700;color:#111827;text-align:center;border-bottom:1px solid #e5e7eb;padding-bottom:10px;}
      .muted{color:#6b7280;font-size:12px;}
      .ac-download{margin-top:8px;width:100%;padding:10px;border-radius:10px;border:1px solid #e5e7eb;background:#fff;cursor:pointer;}
      .ac-download:hover{background:#f9fafb;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ac-card">', unsafe_allow_html=True)
    # Header
    booking_type = appointment.get("booking_type", "normal")
    st.markdown("""
    <div class="ac-head">
      <div class="ac-title">📅 Appointment Confirmed</div>
    """, unsafe_allow_html=True)
    bt_badge = "🚨 Emergency" if booking_type == "emergency" else "📋 Normal"
    st.markdown(f'<div class="ac-badge">{bt_badge} Booking</div></div>', unsafe_allow_html=True)

    # Body
    st.markdown('<div class="ac-body">', unsafe_allow_html=True)

    # Patient name
    st.markdown(f'<div class="ac-name">{appointment.get("patient_name","")}<div class="muted">Patient</div></div>', unsafe_allow_html=True)

    # Doctor row
    st.markdown(f"""
    <div class="ac-row">
      <div>👨‍⚕️</div>
      <div>
        <div style="font-weight:600;">Dr. {appointment.get("doctor_name","")}</div>
        <div class="muted">Attending Physician</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Date/time row
    st.markdown(f"""
    <div class="ac-row">
      <div>📆</div>
      <div>
        <div style="font-weight:600;">{_format_date_iso_long(appointment.get("appointment_date"))}</div>
        <div class="muted">{appointment.get("appointment_time","")}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Hospital / distance
    distance_km = _safe_float(appointment.get("distance_km"))
    eta = _safe_float(appointment.get("estimated_travel_time"))
    dist_eta = ""
    if distance_km is not None:
        dist_eta = f"{distance_km:.1f}km"
        if eta is not None:
            dist_eta += f" • ~{int(round(eta))} min travel"
    st.markdown(f"""
    <div class="ac-row">
      <div>📍</div>
      <div>
        <div style="font-weight:600;">{appointment.get("hospital_name","")}</div>
        <div class="muted">{dist_eta}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Bed block
    if appointment.get("needs_bed") and bedDetails:
        st.markdown(f"""
        <div class="ac-row" style="border-color:#fed7aa;">
          <div>🛏️</div>
          <div>
            <div style="font-weight:600;">{appointment.get("bed_type","")} Reserved</div>
            <div class="muted">₹{bedDetails.get("price","")}/night</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Render the print section (visible preview)
    st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
    PrintReceipt(appointment, bedDetails)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download button: generate print-friendly HTML
    html_content = _build_print_html(appointment, bedDetails)
    st.download_button(
        label="Download PDF Receipt",
        data=html_content.encode("utf-8"),
        file_name="doctigo_receipt.html",
        mime="text/html",
        help="Downloads a print-ready HTML. Open it and press Ctrl/Cmd+P to save as PDF."
    )

    st.markdown('</div>', unsafe_allow_html=True)  # ac-body
    st.markdown('</div>', unsafe_allow_html=True)  # ac-card

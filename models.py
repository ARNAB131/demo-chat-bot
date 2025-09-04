# models.py
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime


class Appointment(BaseModel):
    patient_name: str
    booking_type: Literal["normal", "emergency"]

    symptoms: Optional[List[str]] = None
    doctor_name: Optional[str] = None
    hospital_name: Optional[str] = None
    appointment_date: Optional[datetime] = None  # format: date-time
    appointment_time: Optional[str] = None

    patient_phone: Optional[str] = None
    patient_gender: Optional[Literal["male", "female", "other"]] = None
    patient_age: Optional[float] = None
    patient_email: Optional[EmailStr] = None
    patient_address: Optional[str] = None

    needs_bed: Optional[bool] = None
    bed_type: Optional[Literal["General Bed", "General Cabin", "VIP Cabin"]] = None
    bed_details: Optional[str] = None  # JSON string of bed features and price

    estimated_travel_time: Optional[float] = None  # minutes
    distance_km: Optional[float] = None  # km

    status: Literal["confirmed", "pending", "cancelled"] = "confirmed"

    # carried over as-is (not enforced by pydantic; include for reference/DB layer)
    rls: dict = {
        "read": {
            "$or": [
                {"created_by": "{{user.email}}"},
                {"user_condition": {"role": "admin"}},
            ]
        },
        "write": {
            "$or": [
                {"created_by": "{{user.email}}"},
                {"user_condition": {"role": "admin"}},
            ]
        },
    }


class Doctor(BaseModel):
    name: str
    specialization: str
    hospital: Optional[str] = None
    chamber: Optional[str] = None
    visiting_hours: Optional[str] = None
    available_slots: Optional[List[str]] = None
    experience: Optional[str] = None

    rls: dict = {
        "read": {},
        "write": {
            "$or": [
                {"created_by": "{{user.email}}"},
                {"user_condition": {"role": "admin"}},
            ]
        },
    }


class Hospital(BaseModel):
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None

    rls: dict = {
        "read": {},
        "write": {
            "$or": [
                {"created_by": "{{user.email}}"},
                {"user_condition": {"role": "admin"}},
            ]
        },
    }

# vitals_bridge.py
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import streamlit as st

PERSIST_PATH = Path("latest_vitals.json")

def get_latest_vitals() -> Optional[Dict[str, Any]]:
    """Return a dict with the most recent vitals or None if not available."""
    # First: from session (preferred)
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

    # Second: from file (optional persistence)
    if PERSIST_PATH.exists():
        try:
            return json.loads(PERSIST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return None

    return None


def set_latest_vitals(vitals: Dict[str, Any]) -> None:
    """Persist vitals to session and (optionally) to a json file."""
    # You can store a one-row DataFrame to forecast_data if you want,
    # but keeping it as JSON is fine for the chat app.
    st.session_state["latest_vitals_dict"] = vitals
    try:
        PERSIST_PATH.write_text(json.dumps(vitals, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

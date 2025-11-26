# utils.py — use Flask API instead of direct SQL
import os
import sys
import requests
import streamlit as st

# ---------- CONFIG ----------
# We’ll read API base URL from Streamlit secrets if possible,
# otherwise fall back to an environment variable / hard-coded value.
def _get_api_base() -> str:
    # 1) Streamlit Cloud secrets
    try:
        api_url = st.secrets.get("api_url", "").strip()
        if api_url:
            return api_url.rstrip("/")
    except Exception:
        pass

    # 2) Environment variable (optional)
    api_url = os.getenv("API_URL", "").strip()
    if api_url:
        return api_url.rstrip("/")

    # 3) LAST RESORT: hard-code while testing (CHANGE THIS!)
    return "https://unsubordinative-intermalleolar-ria.ngrok-free.dev".rstrip("/")


API_BASE = _get_api_base()


def _post(endpoint: str, payload: dict) -> dict:
    """Helper to call the Flask API."""
    url = f"{API_BASE}{endpoint}"
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        print(f"[API] Error calling {url}: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}


# ---------- USERS API (wrapping your Flask endpoints) ----------
def get_user(username: str, password: str):
    payload = {
        "username": (username or "").strip(),
        "password": password or ""
    }

    data = _post("/get_user", payload)

    if data.get("success") and data.get("user"):
        return data["user"]

    return None



def add_user(username: str, password: str, role: str, rights: dict | None = None) -> bool:
    rights = rights or {}
    payload = {
        "username": username,
        "password": password,
        "role": role,
        "rights": {
            "internal_store_transfer": bool(rights.get("internal_store_transfer")),
            "assortment": bool(rights.get("assortment")),
            "ip": bool(rights.get("ip")),
        },
    }
    data = _post("/add_user", payload)
    return bool(data.get("success"))


def delete_user(username: str) -> bool:
    payload = {"username": (username or "").strip()}
    data = _post("/delete_user", payload)
    return bool(data.get("success"))


def update_user_rights(username: str, rights: dict) -> bool:
    payload = {
        "username": (username or "").strip(),
        "rights": {
            "internal_store_transfer": bool(rights.get("internal_store_transfer")),
            "assortment": bool(rights.get("assortment")),
            "ip": bool(rights.get("ip")),
        },
    }
    data = _post("/update_user_rights", payload)
    return bool(data.get("success"))


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    For now we keep it simple: compare plain text.
    Your existing users 'admin123', 'orient123' are stored as plain text.

    If later you change API to return hashed passwords, we can extend this.
    """
    if stored_password is None:
        return False
    return plain_password == stored_password



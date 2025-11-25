# utils.py — SQL Server over pymssql
import streamlit as st
import os
import json
import sys
import pymssql  # correct SQL Server driver

# Optional password hashing
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False


# ---------- CONFIG ----------
CONFIG_PATH = os.getenv("DB_CONFIG_JSON", os.path.join(os.getcwd(), "secrets.json"))

def _load_cfg() -> dict:
    """Load database config from Streamlit secrets (cloud) or secrets.json (local)"""
    # Cloud first
    try:
        if "mssql" in st.secrets:
            cfg = dict(st.secrets["mssql"])
            print("[DB] Loaded st.secrets['mssql']:", cfg, file=sys.stderr)
            return cfg
    except Exception as e:
        print(f"[DB] No st.secrets['mssql']: {e}", file=sys.stderr)

    # Local fallback
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f).get("mssql", {})
            print("[DB] Loaded local secrets.json:", cfg, file=sys.stderr)
            return cfg
    except Exception as e:
        print(f"[DB] Could not load {CONFIG_PATH}: {e}", file=sys.stderr)
        return {}

CFG = _load_cfg()


# ---------- DB CONNECTION ----------
def connect_to_database():
    """Connect to SQL Server using pymssql"""
    try:
        conn = pymssql.connect(
            server=CFG.get("server"),
            user=CFG.get("username"),
            password=CFG.get("password"),
            database=CFG.get("database"),
            port=int(CFG.get("port", 1433))
        )
        print("[DB] Connected via pymssql!", file=sys.stderr)
        return conn
    except Exception as e:
        print("[DB] pymssql Connection error:", e, file=sys.stderr)
        return None


# ---------- HELPERS ----------
def _to_bit(v) -> int:
    return 1 if bool(v) else 0


# ---------- USERS ----------
def get_user(username: str):
    try:
        conn = connect_to_database()
        if not conn:
            print("[LOGIN] DB connection failed!", file=sys.stderr)
            return None

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, password, role,
                   can_access_internal_store_transfer,
                   can_access_assortment,
                   can_access_ip
            FROM dbo.users
            WHERE username = %s
            """,
            (username.strip(),)
        )
        row = cursor.fetchone()
        conn.close()

        print("[LOGIN] Query returned:", row, file=sys.stderr)

        if row:
            return {
                "id": row[0],
                "username": row[1],
                "password": row[2],
                "role": row[3],
                "can_access_internal_store_transfer": bool(row[4]),
                "can_access_assortment": bool(row[5]),
                "can_access_ip": bool(row[6]),
            }
        return None

    except Exception as e:
        print("[LOGIN] ERROR:", e, file=sys.stderr)
        return None


def verify_password(plain: str, stored: str) -> bool:
    if not stored:
        return False
    if HAS_BCRYPT and stored.startswith("$2"):
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), stored.encode("utf-8"))
        except:
            return False
    return plain == stored

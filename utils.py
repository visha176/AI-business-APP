# utils.py — SQL Server connection using pymssql (no pyodbc)
import streamlit as st
import os
import json
import sys
import pymssql  # pip install pymssql

# Optional password hashing (works even if bcrypt isn't installed)
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False


# ---------- CONFIG ----------
# Reads ./secrets.json by default; or Streamlit Cloud secrets if available
CONFIG_PATH = os.getenv("DB_CONFIG_JSON", os.path.join(os.getcwd(), "secrets.json"))


def _load_cfg() -> dict:
    """Load DB config.

    Priority:
    1) st.secrets["mssql"] (Streamlit Cloud)
    2) secrets.json (local file)
    """
    try:
        if "mssql" in st.secrets:
            cfg = dict(st.secrets["mssql"])
            print("[DB] Using st.secrets config:", cfg, file=sys.stderr)
            return cfg
    except Exception as e:
        print("[DB] st.secrets not found:", e, file=sys.stderr)

    # Fallback for local dev
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            cfg = data.get("mssql", {})
            print("[DB] Using local secrets.json config:", cfg, file=sys.stderr)
            return cfg
    except Exception as e:
        print("[DB] Local secrets.json missing:", e, file=sys.stderr)
        return {}


CFG = _load_cfg()


# ---------- CONNECTION ----------
def connect_to_database():
    """Connect to SQL Server using pymssql driver."""
    try:
        print("[DB] Attempting pymssql connection...", file=sys.stderr)
        conn = pymssql.connect(
            server=str(CFG.get("server")),
            user=str(CFG.get("username")),
            password=str(CFG.get("password")),
            database=str(CFG.get("database")),
            port=int(CFG.get("port", 1433)),
            login_timeout=10,
            timeout=15
        )
        print("[DB] Connection SUCCESS", file=sys.stderr)
        return conn
    except Exception as e:
        print("[DB] Connection FAILED:", e, file=sys.stderr)
        return None


# ---------- HELPERS ----------
def _to_bit(v) -> int:
    return 1 if bool(v) else 0


# ---------- USERS API ----------
def get_user(username):
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

        print("[LOGIN] Query result:", row, file=sys.stderr)

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


def add_user(username: str, password: str, role: str, rights: dict | None = None) -> bool:
    rights = rights or {}
    pw_to_store = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode() if HAS_BCRYPT else password

    sql = """
        INSERT INTO dbo.users
        (username, password, role,
         can_access_internal_store_transfer, can_access_assortment, can_access_ip)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    params = (
        username,
        pw_to_store,
        role,
        _to_bit(rights.get("internal_store_transfer", False)),
        _to_bit(rights.get("assortment", False)),
        _to_bit(rights.get("ip", False)),
    )

    conn = connect_to_database()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        print("[DB] add_user ERROR:", e, file=sys.stderr)
        return False


def delete_user(username: str) -> bool:
    sql = "DELETE FROM dbo.users WHERE username = %s"
    conn = connect_to_database()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(sql, (username,))
        conn.commit()
        return True
    except Exception as e:
        print("[DB] delete_user ERROR:", e, file=sys.stderr)
        return False


def update_user_rights(username: str, rights: dict) -> bool:
    sql = """
        UPDATE dbo.users
           SET can_access_internal_store_transfer = %s,
               can_access_assortment = %s,
               can_access_ip = %s
         WHERE username = %s
    """

    params = (
        _to_bit(rights.get("internal_store_transfer", False)),
        _to_bit(rights.get("assortment", False)),
        _to_bit(rights.get("ip", False)),
        username,
    )

    conn = connect_to_database()
    if not conn:
        return False

    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print("[DB] update_user_rights ERROR:", e, file=sys.stderr)
        return False


def verify_password(plain_password: str, stored_password: str) -> bool:
    if HAS_BCRYPT and stored_password.startswith("$2"):
        return bcrypt.checkpw(plain_password.encode("utf-8"), stored_password.encode("utf-8"))
    return plain_password == stored_password

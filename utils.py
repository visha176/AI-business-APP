# utils.py — SQL Server only (pyodbc)
import os
import json
import sys
import pyodbc  # pip install pyodbc

# Optional password hashing (works even if bcrypt isn't installed)
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False


# ---------- CONFIG ----------
# Reads ./secrets.json by default; override with env var DB_CONFIG_JSON
CONFIG_PATH = os.getenv("DB_CONFIG_JSON", os.path.join(os.getcwd(), "secrets.json"))


def _load_cfg() -> dict:
    """Load the JSON config (once)."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("mssql", {})
    except Exception as e:
        print(f"[DB] Could not load {CONFIG_PATH}: {e}", file=sys.stderr)
        return {}


CFG = _load_cfg()


# ---------- CONNECTION ----------
def _build_conn_str(cfg: dict) -> str:
    """
    Build a robust ODBC connection string.
    - Accepts either "server": "HOST,PORT" or "server": "HOST" + "port": 1433
    - Adds Encrypt/TrustServerCertificate for ODBC Driver 18
    """
    driver = cfg.get("driver", "ODBC Driver 18 for SQL Server")
    server = str(cfg.get("server", "")).strip()
    port = cfg.get("port")

    # If port provided separately, append it to server as HOST,PORT
    if port and ("," not in server):
        server = f"{server},{port}"

    database = cfg.get("database", "").strip()
    uid = cfg.get("username", "").strip()
    pwd = cfg.get("password", "")
    encrypt = "yes" if cfg.get("encrypt", True) else "no"
    trust = "yes" if cfg.get("trust_server_certificate", True) else "no"
    timeout = int(cfg.get("timeout", 15))  # seconds

    missing = [k for k in ("server", "database", "username", "password") if not cfg.get(k)]
    if missing:
        raise ValueError(f"Missing mssql config keys in {CONFIG_PATH}: {missing}")

    # NB: database name with spaces is fine in ODBC
    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
        f"Connection Timeout={timeout};"
    )


def connect_to_database():
    """Open a SQL Server connection using pyodbc and secrets.json."""
    try:
        conn_str = _build_conn_str(CFG)
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"[DB] Connection error: {e}", file=sys.stderr)
        return None


# ---------- HELPERS ----------
def _to_bit(v) -> int:
    return 1 if bool(v) else 0


# ---------- USERS API ----------
def get_user(username):
    import pyodbc
    import json

    with open("secrets.json", "r") as f:
        creds = json.load(f)["mssql"]

    conn_str = (
        f"DRIVER={{{creds['driver']}}};"
        f"SERVER={creds['server']};"
        f"DATABASE={creds['database']};"
        f"UID={creds['username']};"
        f"PWD={creds['password']};"
        f"Encrypt={'yes' if creds['encrypt'] else 'no'};"
        f"TrustServerCertificate={'yes' if creds['trust_server_certificate'] else 'no'};"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role, can_access_internal_store_transfer, can_access_assortment, can_access_ip FROM dbo.users WHERE username = ?", username)
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row.id,
            "username": row.username,
            "password": row.password,
            "role": row.role,
            "can_access_internal_store_transfer": bool(row.can_access_internal_store_transfer),
            "can_access_assortment": bool(row.can_access_assortment),
            "can_access_ip": bool(row.can_access_ip),
        }
    else:
        return None



def add_user(username: str, password: str, role: str, rights: dict | None = None) -> bool:
    rights = rights or {}
    pw_to_store = (
        bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        if HAS_BCRYPT else password
    )

    sql = """
        INSERT INTO dbo.users
        (username, password, role,
         can_access_internal_store_transfer, can_access_assortment, can_access_ip)
        VALUES (?, ?, ?, ?, ?, ?)
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
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] add_user error: {e}", file=sys.stderr)
        return False
    finally:
        try:
            if cur:
                cur.close()
            conn.close()
        except Exception:
            pass


def delete_user(username: str) -> bool:
    sql = "DELETE FROM dbo.users WHERE username = ?"
    conn = connect_to_database()
    if not conn:
        return False
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql, (username,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] delete_user error: {e}", file=sys.stderr)
        return False
    finally:
        try:
            if cur:
                cur.close()
            conn.close()
        except Exception:
            pass


def update_user_rights(username: str, rights: dict) -> bool:
    sql = """
        UPDATE dbo.users
           SET can_access_internal_store_transfer = ?,
               can_access_assortment             = ?,
               can_access_ip                     = ?
         WHERE username = ?
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
    cur = None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        print(f"[DB] update_user_rights error: {e}", file=sys.stderr)
        return False
    finally:
        try:
            if cur:
                cur.close()
            conn.close()
        except Exception:
            pass


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    True if plain_password matches stored_password.
    Uses bcrypt when stored value looks like a bcrypt hash ($2...),
    otherwise falls back to plain-text compare (dev only).
    """
    if not stored_password:
        return False
    if HAS_BCRYPT and stored_password.startswith("$2"):
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                stored_password.encode("utf-8")
            )
        except Exception:
            return False
    return plain_password == stored_password

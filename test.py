import pyodbc, json, os

with open(os.path.join(os.getcwd(), "secrets.json"), "r") as f:
    cfg = json.load(f)["mssql"]

conn_str = (
    f"DRIVER={{{cfg['driver']}}};"
    f"SERVER={cfg['server']};"
    f"DATABASE={cfg['database']};"
    f"UID={cfg['username']};"
    f"PWD={cfg['password']};"
    f"Encrypt=yes;TrustServerCertificate=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✅ Connected successfully!")
    cur = conn.cursor()
    cur.execute("SELECT TOP 3 * FROM dbo.Product_Data")
    for row in cur.fetchall():
        print(row)
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)

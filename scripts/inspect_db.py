#!/usr/bin/env python3
"""Admin inspection of the SQL Server using sa creds passed via env vars.
Does NOT write anything. Reports security-relevant facts so we can deploy
the app with a least-privilege (read-only) login instead of sa.
"""
import os
import pyodbc

server = os.environ["INS_SERVER"]
user = os.environ["INS_USER"]
pwd = os.environ["INS_PASS"]
driver = os.environ.get("INS_DRIVER", "ODBC Driver 18 for SQL Server")
target_db = os.environ.get("INS_DB", "eJarAnalytics")
ro_login = os.environ.get("INS_RO_LOGIN", "renty_readonly")

cs = (
    f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;"
    f"UID={user};PWD={pwd};Encrypt=yes;TrustServerCertificate=yes;"
    "Connection Timeout=10;"
)
cn = pyodbc.connect(cs)
cur = cn.cursor()


def q(sql):
    cur.execute(sql)
    return cur.fetchall()


print("=== version ===")
print(q("SELECT @@VERSION")[0][0].splitlines()[0])

print("\n=== logged in as ===")
print("login:", q("SELECT SUSER_SNAME()")[0][0],
      "| sysadmin:", q("SELECT IS_SRVROLEMEMBER('sysadmin')")[0][0])

print("\n=== target database present? ===")
rows = q(f"SELECT name, state_desc FROM sys.databases WHERE name = '{target_db}'")
print(rows if rows else f"DB '{target_db}' NOT found")
print("all user DBs:", [r[0] for r in q("SELECT name FROM sys.databases WHERE database_id > 4 ORDER BY name")])

print("\n=== read-only login present? ===")
rows = q(f"SELECT name, type_desc, is_disabled FROM sys.server_principals WHERE name = '{ro_login}'")
print(rows if rows else f"login '{ro_login}' NOT found")

print("\n=== security posture ===")
for label, sql in [
    ("xp_cmdshell enabled (1=BAD)", "SELECT value_in_use FROM sys.configurations WHERE name='xp_cmdshell'"),
    ("Ole Automation enabled", "SELECT value_in_use FROM sys.configurations WHERE name='Ole Automation Procedures'"),
    ("remote admin connections", "SELECT value_in_use FROM sys.configurations WHERE name='remote admin connections'"),
]:
    try:
        print(f"{label}: {q(sql)[0][0]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label}: <error {e}>")

cn.close()
print("\nDONE")

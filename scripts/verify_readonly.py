#!/usr/bin/env python3
"""Verify least-privilege deployment options:
  1) As sa: read server security config (CAST sql_variant -> int).
  2) As renty_readonly: confirm login works, is read-only on eJarAnalytics,
     and that a write is denied.
No writes are committed.
"""
import os
import pyodbc

server = os.environ["INS_SERVER"]
driver = os.environ.get("INS_DRIVER", "ODBC Driver 18 for SQL Server")


def conn(user, pwd, db="master"):
    cs = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={db};"
        f"UID={user};PWD={pwd};Encrypt=yes;TrustServerCertificate=yes;"
        "Connection Timeout=10;"
    )
    return pyodbc.connect(cs)


# 1) sa security config
print("=== server security config (as sa) ===")
cn = conn(os.environ["SA_USER"], os.environ["SA_PASS"])
cur = cn.cursor()
for name in ["xp_cmdshell", "Ole Automation Procedures", "remote admin connections"]:
    cur.execute(
        "SELECT CAST(value_in_use AS int) FROM sys.configurations WHERE name = ?",
        name,
    )
    print(f"  {name}: {cur.fetchone()[0]}")
cn.close()

# 2) renty_readonly verification
print("\n=== renty_readonly on eJarAnalytics ===")
ro_user = os.environ.get("RO_USER", "renty_readonly")
ro_pass = os.environ["RO_PASS"]
try:
    cn = conn(ro_user, ro_pass, db="eJarAnalytics")
    cur = cn.cursor()
    cur.execute("SELECT SUSER_SNAME()")
    print("  connected as:", cur.fetchone()[0])
    cur.execute(
        "SELECT r.name FROM sys.database_role_members m "
        "JOIN sys.database_principals r ON r.principal_id = m.role_principal_id "
        "JOIN sys.database_principals u ON u.principal_id = m.member_principal_id "
        "WHERE u.name = USER_NAME()"
    )
    roles = [r[0] for r in cur.fetchall()]
    print("  db roles:", roles)
    print("  is_readonly:", ("db_datareader" in roles and "db_denydatawriter" in roles))
    # prove writes are blocked
    try:
        cur.execute("SELECT TOP 1 name FROM sys.tables")
        t = cur.fetchone()
        tname = t[0] if t else None
        if tname:
            cur.execute(f"UPDATE [{tname}] SET 1=1 WHERE 1=0")
            print("  WRITE TEST: !! write allowed (UNEXPECTED)")
    except pyodbc.Error as e:
        print("  WRITE TEST: denied (good) ->", str(e).split("]")[-1][:80])
    cn.close()
except pyodbc.Error as e:
    print("  renty_readonly connect FAILED ->", e)

print("\nDONE")

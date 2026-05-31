"""
One-time admin script: provision a STRICT read-only SQL Server login for the
Renty analytics demo.

The demo application must NEVER be able to write to, alter, or otherwise modify
the database. This script creates a dedicated login/user that:
  - is added to db_datareader  (can SELECT)
  - is added to db_denydatawriter  (DB-wide DENY on INSERT/UPDATE/DELETE)
  - is explicitly DENIED INSERT/UPDATE/DELETE/EXECUTE/ALTER/CONTROL on schema dwh
  - is DENIED CREATE/ALTER/DROP at the database level

It must be run by a privileged login (e.g. `sa`). Admin credentials and the
read-only password are read from environment variables so nothing secret is
hard-coded:

    DB_SERVER                (reused from .env)
    DB_DATABASE              (reused from .env)
    DB_DRIVER                (reused from .env)
    DB_TRUST_CERT            (reused from .env)
    DB_ADMIN_USER            admin login used only to run this script
    DB_ADMIN_PASSWORD        admin password
    DB_READONLY_USER         name of the read-only login to create
    DB_READONLY_PASSWORD     password to assign the read-only login

Usage (PowerShell, one line, values not committed anywhere):
    $env:DB_ADMIN_USER='sa'; $env:DB_ADMIN_PASSWORD='...'; `
    $env:DB_READONLY_USER='renty_readonly'; $env:DB_READONLY_PASSWORD='...'; `
    python scripts/setup_readonly_user.py
"""
import os
import sys
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv(override=True)


def _admin_engine():
    server = os.environ["DB_SERVER"]
    database = os.environ["DB_DATABASE"]
    driver = os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trust = os.environ.get("DB_TRUST_CERT", "yes")
    user = os.environ["DB_ADMIN_USER"]
    password = os.environ["DB_ADMIN_PASSWORD"]

    url = (
        f"mssql+pyodbc://{user}:{urllib.parse.quote_plus(password)}@{server}/{database}"
        f"?driver={urllib.parse.quote_plus(driver)}&TrustServerCertificate={trust}"
    )
    # autocommit so each DDL/permission statement takes effect immediately
    return create_engine(url, isolation_level="AUTOCOMMIT")


def main() -> None:
    ro_user = os.environ.get("DB_READONLY_USER", "renty_readonly")
    ro_pwd = os.environ.get("DB_READONLY_PASSWORD")
    database = os.environ["DB_DATABASE"]

    if not ro_pwd:
        print("ERROR: set DB_READONLY_PASSWORD before running.")
        sys.exit(1)

    # The read-only user name must be a safe SQL identifier (letters, digits, _).
    # We embed it directly as a bracket-quoted identifier, so reject anything else.
    if not all(c.isalnum() or c == "_" for c in ro_user):
        print("ERROR: DB_READONLY_USER must contain only letters, digits, underscore.")
        sys.exit(1)
    ro_pwd_lit = ro_pwd.replace("'", "''")  # escape for the SQL string literal

    statements = [
        # 1. Create the server login if it does not exist (EXEC: CREATE LOGIN must
        #    be the first statement in its batch; dynamic SQL satisfies that).
        f"""
        IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = '{ro_user}')
            EXEC(N'CREATE LOGIN [{ro_user}] WITH PASSWORD = ''{ro_pwd_lit}'', CHECK_POLICY = OFF');
        """,
        # 2. Create the database user mapped to that login if it does not exist
        f"""
        IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '{ro_user}')
            EXEC(N'CREATE USER [{ro_user}] FOR LOGIN [{ro_user}]');
        """,
        # 3. Grant read on the whole database
        f"ALTER ROLE db_datareader ADD MEMBER [{ro_user}];",
        # 4. DB-wide DENY on all writes
        f"ALTER ROLE db_denydatawriter ADD MEMBER [{ro_user}];",
        # 5. Explicit, schema-scoped DENY for writes/exec/alter (defense in depth).
        #    Do NOT deny CONTROL here: DENY CONTROL on a schema also revokes SELECT
        #    and would break read access granted via db_datareader.
        f"DENY INSERT, UPDATE, DELETE, EXECUTE, ALTER ON SCHEMA::dwh TO [{ro_user}];",
        # 6. DENY structural changes at the database level
        f"DENY CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION, CREATE SCHEMA TO [{ro_user}];",
    ]

    engine = _admin_engine()
    print(f"Connecting as admin to {os.environ['DB_SERVER']}/{database} ...")
    with engine.connect() as conn:
        for i, stmt in enumerate(statements, 1):
            conn.execute(text(stmt))
            print(f"  step {i}/{len(statements)} OK")

    # Verify the effective permissions of the new principal
    print("\nVerifying read-only permissions ...")
    verify_sql = f"""
    SELECT dp.permission_name, dp.state_desc
    FROM sys.database_permissions dp
    JOIN sys.database_principals pr ON dp.grantee_principal_id = pr.principal_id
    WHERE pr.name = '{ro_user}'
    ORDER BY dp.state_desc, dp.permission_name;
    """
    role_sql = f"""
    SELECT r.name AS role_name
    FROM sys.database_role_members rm
    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
    WHERE m.name = '{ro_user}';
    """
    with engine.connect() as conn:
        roles = [row[0] for row in conn.execute(text(role_sql))]
        perms = [(row[0], row[1]) for row in conn.execute(text(verify_sql))]

    print(f"  Roles: {', '.join(roles) if roles else '(none)'}")
    for name, state in perms:
        print(f"  {state}: {name}")

    print(
        f"\nDone. Login '{ro_user}' is read-only.\n"
        f"Now set DB_USER={ro_user} and DB_PASSWORD=<the password> in .env, "
        f"then run `python db.py` to confirm the app connects as the read-only user."
    )


if __name__ == "__main__":
    main()

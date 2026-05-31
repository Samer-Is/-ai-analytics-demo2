"""
Data access layer for the Renty analytics demo.

Two interchangeable back ends are provided, selected by the ``DATA_SOURCE``
environment variable:

* ``live``    (default) - a singleton SQLAlchemy engine that runs read-only
  queries against the eJarAnalytics warehouse (``dwh`` schema on SQL Server).
* ``offline`` - an in-process DuckDB instance that serves the same ``dwh.*``
  tables from local Parquet snapshot files (see ``scripts/extract_snapshot.py``).

The public contract (``run_query``, ``validate_sql``, ``get_connection_security``,
``smoke_test``) is identical for both back ends, so the rest of the application
and the generated analysis code do not need to know which one is active. ALL of
the live SQL Server code is preserved unchanged and simply bypassed when
``DATA_SOURCE=offline``.
"""
import glob
import os
import re
import urllib.parse
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


# Single engine for the whole app. Created lazily on first use.
_engine: Optional[Engine] = None

# Single DuckDB connection for offline mode. Created lazily on first use.
_duck = None


def _data_source() -> str:
    """Return the active data source ('live' or 'offline'), read at call time."""
    return os.environ.get("DATA_SOURCE", "live").strip().lower()


def _snapshot_dir() -> str:
    """Directory that holds the Parquet snapshot files for offline mode.

    Defaults to ``<app dir>/data/renty`` so the path resolves regardless of the
    current working directory (the code executor runs generated scripts from a
    temp dir). Override with the ``DATA_DIR`` environment variable.
    """
    override = os.environ.get("DATA_DIR")
    if override:
        return override
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "renty")


def get_duckdb():
    """Create or return the DuckDB connection used for offline mode.

    Every ``*.parquet`` file in the snapshot directory is exposed as a view
    ``dwh.<filename>`` so existing ``dwh.<table>`` SQL keeps working verbatim.
    """
    global _duck
    if _duck is not None:
        return _duck

    import duckdb  # local import: live mode does not require duckdb installed

    data_dir = _snapshot_dir()
    files = sorted(glob.glob(os.path.join(data_dir, "*.parquet")))
    if not files:
        raise FileNotFoundError(
            f"No Parquet snapshot files found in '{data_dir}'. "
            "Run scripts/extract_snapshot.py against the live database first, "
            "or set DATA_DIR to the snapshot location."
        )

    con = duckdb.connect(database=":memory:")
    con.execute("CREATE SCHEMA IF NOT EXISTS dwh")
    for path in files:
        table = os.path.splitext(os.path.basename(path))[0]
        # Table names come from filenames we control in the extraction script.
        # DuckDB does not allow bind parameters inside CREATE VIEW, so the path
        # is inlined with single quotes escaped.
        safe_path = path.replace("'", "''")
        con.execute(
            f'CREATE OR REPLACE VIEW dwh."{table}" AS '
            f"SELECT * FROM read_parquet('{safe_path}')"
        )
    _duck = con
    return _duck


def get_engine() -> Engine:
    """Create or return the SQLAlchemy engine for the analytics DB."""
    global _engine
    if _engine is not None:
        return _engine

    server = os.environ["DB_SERVER"]
    database = os.environ["DB_DATABASE"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    driver = os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trust_cert = os.environ.get("DB_TRUST_CERT", "yes")

    driver_encoded = urllib.parse.quote_plus(driver)
    password_encoded = urllib.parse.quote_plus(password)

    odbc_str = (
        f"mssql+pyodbc://{user}:{password_encoded}@{server}/{database}"
        f"?driver={driver_encoded}&TrustServerCertificate={trust_cert}"
    )

    _engine = create_engine(
        odbc_str,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        connect_args={"timeout": int(os.environ.get("DB_QUERY_TIMEOUT", "30"))},
    )
    return _engine


# Whitelist: query must start with SELECT or WITH (for CTEs).
_SAFE_STATEMENT_PATTERN = re.compile(r"^\s*(WITH|SELECT)\b", re.IGNORECASE)

# Forbidden keywords. Even inside a SELECT these should not appear.
_FORBIDDEN_KEYWORDS = [
    r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b",
    r"\bALTER\b", r"\bTRUNCATE\b", r"\bMERGE\b", r"\bEXEC\b",
    r"\bEXECUTE\b", r"\bCREATE\b", r"\bGRANT\b", r"\bREVOKE\b",
    r"\bSP_\w+", r"\bXP_\w+",
]
_FORBIDDEN_PATTERN = re.compile("|".join(_FORBIDDEN_KEYWORDS), re.IGNORECASE)

# Maximum rows returned by a single query. The LLM is told to aggregate,
# but this is defense-in-depth against runaway SELECTs.
MAX_ROWS = int(os.environ.get("DB_MAX_ROWS", "10000"))


class UnsafeSQLError(ValueError):
    """Raised when generated SQL contains a forbidden statement or keyword."""


def _strip_string_literals(sql: str) -> str:
    """Remove single-quoted string literals so we can search for keywords safely."""
    return re.sub(r"'(?:[^']|'')*'", "''", sql)


def validate_sql(sql: str) -> None:
    """
    Reject any SQL that is not a pure SELECT (or WITH-prefixed CTE).
    Raises UnsafeSQLError if the SQL is not safe to execute.
    """
    if not sql or not sql.strip():
        raise UnsafeSQLError("Empty SQL")

    if not _SAFE_STATEMENT_PATTERN.match(sql):
        raise UnsafeSQLError(
            f"SQL must start with SELECT or WITH. Got: {sql[:80]}..."
        )

    sanitized = _strip_string_literals(sql)

    forbidden = _FORBIDDEN_PATTERN.search(sanitized)
    if forbidden:
        raise UnsafeSQLError(
            f"SQL contains forbidden keyword: {forbidden.group(0)}"
        )

    stripped = sanitized.rstrip().rstrip(";").strip()
    if ";" in stripped:
        raise UnsafeSQLError("Multi-statement SQL is not allowed")


def _cap_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Defense-in-depth cap on the number of rows returned by a single query."""
    if len(df) > MAX_ROWS:
        df = df.head(MAX_ROWS)
        df.attrs["truncated"] = True
        df.attrs["truncated_at"] = MAX_ROWS
    return df


def _run_query_offline(sql: str) -> pd.DataFrame:
    """Execute an already-validated read-only query against the DuckDB snapshot."""
    con = get_duckdb()
    df = con.execute(sql).fetch_df()
    return _cap_rows(df)


def run_query(sql: str, timeout_seconds: Optional[int] = None) -> pd.DataFrame:
    """
    Validate, execute, and return SQL query results as a DataFrame.
    Read-only. Throws UnsafeSQLError or SQLAlchemyError on failure.

    Routes to the local DuckDB snapshot when ``DATA_SOURCE=offline``; otherwise
    runs against the live SQL Server warehouse.
    """
    validate_sql(sql)

    if _data_source() == "offline":
        return _run_query_offline(sql)

    timeout = timeout_seconds or int(os.environ.get("DB_QUERY_TIMEOUT", "30"))
    engine = get_engine()

    with engine.connect() as conn:
        # Set per-statement timeout for SQL Server (milliseconds).
        conn.execute(text(f"SET LOCK_TIMEOUT {timeout * 1000}"))
        df = pd.read_sql_query(text(sql), conn)

    return _cap_rows(df)


def get_connection_security() -> dict:
    """
    Inspect the database principal the app is connected as and confirm it is
    read-only. Returns the user name, granted database roles, and any
    explicit DENY permissions.
    """
    info: dict = {
        "user": os.environ.get("DB_USER", "(unknown)"),
        "roles": [],
        "denied_permissions": [],
        "is_readonly": False,
        "error": None,
    }

    # Offline mode: data is served from immutable local Parquet files. There is
    # no live principal to inspect; report a synthetic read-only status.
    if _data_source() == "offline":
        info.update(
            {
                "user": "offline-snapshot",
                "roles": ["read-only Parquet snapshot"],
                "denied_permissions": [],
                "is_readonly": True,
                "mode": "offline",
                "snapshot_dir": _snapshot_dir(),
            }
        )
        return info

    try:
        engine = get_engine()
        with engine.connect() as conn:
            info["user"] = conn.execute(text("SELECT CURRENT_USER")).scalar() or info["user"]

            roles = conn.execute(text(
                """
                SELECT r.name
                FROM sys.database_role_members m
                JOIN sys.database_principals r ON r.principal_id = m.role_principal_id
                JOIN sys.database_principals u ON u.principal_id = m.member_principal_id
                WHERE u.name = CURRENT_USER
                ORDER BY r.name
                """
            )).fetchall()
            info["roles"] = [row[0] for row in roles]

            denied = conn.execute(text(
                """
                SELECT DISTINCT permission_name
                FROM sys.database_permissions
                WHERE state_desc = 'DENY'
                  AND grantee_principal_id = DATABASE_PRINCIPAL_ID(CURRENT_USER)
                ORDER BY permission_name
                """
            )).fetchall()
            info["denied_permissions"] = [row[0] for row in denied]

        write_roles = {"db_owner", "db_datawriter", "db_ddladmin"}
        has_write_role = any(r in write_roles for r in info["roles"])
        has_deny_writer = "db_denydatawriter" in info["roles"]
        info["is_readonly"] = (not has_write_role) and (
            has_deny_writer or "db_datareader" in info["roles"]
        )
    except Exception as e:
        info["error"] = str(e)
    return info


def smoke_test() -> dict:
    """Verify connection and return row counts for key tables."""
    queries = {
        "dim_branches": "SELECT COUNT(*) AS n FROM dwh.dim_branches",
        "dim_categories": "SELECT COUNT(*) AS n FROM dwh.dim_categories",
        "fact_daily_features": "SELECT COUNT(*) AS n FROM dwh.fact_daily_features",
        "fact_contracts_clean": "SELECT COUNT(*) AS n FROM dwh.fact_contracts_clean",
        "fact_bookings_clean": "SELECT COUNT(*) AS n FROM dwh.fact_bookings_clean",
    }
    counts = {}
    for name, sql in queries.items():
        df = run_query(sql)
        counts[name] = int(df.iloc[0]["n"])
    return counts


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)

    if _data_source() == "offline":
        print(f"\nReading offline snapshot from {_snapshot_dir()} ...")
    else:
        print(f"\nConnecting to {os.environ['DB_SERVER']}/{os.environ['DB_DATABASE']} ...")
    try:
        counts = smoke_test()
        print("Data source OK. Row counts:")
        for name, n in counts.items():
            print(f"  {name}: {n:,}")
    except Exception as e:
        print(f"Smoke test failed: {e}")
        raise

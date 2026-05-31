"""
Extract the Renty ``dwh`` warehouse tables to local Parquet snapshot files.

This is the ONE-TIME (or periodic) export that feeds the offline DuckDB data
source (see db.py, DATA_SOURCE=offline). Run it from inside the internal network
with the read-only login configured in the environment / .env:

    DB_SERVER, DB_DATABASE, DB_USER, DB_PASSWORD, DB_DRIVER

Usage:
    python scripts/extract_snapshot.py
    python scripts/extract_snapshot.py --out ../data/renty --years 3

Design decisions (documented in docs/activity.md):
* The large fact tables (contracts, bookings, daily demand) are filtered to the
  last N years (default 3) to keep the snapshot small and fast. All other tables
  (dimensions, scope lists, and the pre-aggregated feature/price/utilization
  facts) are exported in full. Pass ``--years 0`` to disable the date filter and
  export the full history of every table (matches the canonical schema counts).
* Files are written as ``<table>.parquet`` (without the ``dwh.`` prefix); the
  DuckDB loader re-exposes each one as ``dwh.<table>`` so existing SQL keeps
  working verbatim.
* The export connects with the least-privilege read-only login -- never ``sa``.
"""
import argparse
import os
import sys
from datetime import date

import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import text

# Allow importing db.py from the parent directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db  # noqa: E402

from dotenv import load_dotenv  # noqa: E402


# table -> date column to filter on (None = export in full).
TABLES = {
    "dwh.dim_branches": None,
    "dwh.dim_categories": None,
    "dwh.dim_carmodels": None,
    "dwh.fact_contracts_clean": "contract_start_date",
    "dwh.fact_bookings_clean": "booking_start_date",
    "dwh.fact_rental_rates": None,
    "dwh.fact_daily_demand": "demand_date",
    "dwh.fact_daily_base_price": None,
    "dwh.fact_daily_features": None,
    "dwh.fact_utilization_snapshot": None,
    "dwh.scope_top_branches": None,
    "dwh.scope_top_categories": None,
    "dwh.competitor_rates_aggregated": None,
}

CHUNK_SIZE = 100_000


def _cutoff_date(years: int) -> str:
    today = date.today()
    try:
        cutoff = today.replace(year=today.year - years)
    except ValueError:
        # Handles Feb 29 -> Feb 28.
        cutoff = today.replace(year=today.year - years, day=28)
    return cutoff.isoformat()


def _export_table(engine, qualified: str, date_col, out_dir: str, cutoff: str) -> int:
    file_name = qualified.split(".")[-1] + ".parquet"
    out_path = os.path.join(out_dir, file_name)

    sql = f"SELECT * FROM {qualified}"
    if date_col:
        sql += f" WHERE {date_col} >= '{cutoff}'"

    print(f"  - {qualified} -> {file_name}", end="", flush=True)
    if date_col:
        print(f"  (filtered {date_col} >= {cutoff})", end="", flush=True)

    writer = None
    total = 0
    try:
        with engine.connect().execution_options(stream_results=True) as conn:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            while True:
                rows = result.fetchmany(CHUNK_SIZE)
                if not rows:
                    break
                table = pa.Table.from_pylist(
                    [dict(zip(columns, row)) for row in rows]
                )
                if writer is None:
                    writer = pq.ParquetWriter(out_path, table.schema)
                else:
                    table = table.cast(writer.schema)
                writer.write_table(table)
                total += table.num_rows
                print(".", end="", flush=True)

        if writer is None:
            # Empty result: still write a valid (0-row) Parquet file with schema.
            with engine.connect() as conn:
                probe = conn.execute(text(f"SELECT TOP 0 * FROM {qualified}"))
                empty = pa.table({c: pa.array([], type=pa.string()) for c in probe.keys()})
            pq.write_table(empty, out_path)
    finally:
        if writer is not None:
            writer.close()

    print(f"  [{total:,} rows]")
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Export dwh tables to Parquet.")
    parser.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "renty"),
        help="Output directory for the Parquet files.",
    )
    parser.add_argument(
        "--years",
        type=int,
        default=int(os.environ.get("SNAPSHOT_YEARS", "3")),
        help="Number of years of history to keep for the large fact tables. "
             "Use 0 to disable the filter and export full history.",
    )
    args = parser.parse_args()

    load_dotenv(override=True)
    os.makedirs(args.out, exist_ok=True)

    full_export = args.years <= 0
    cutoff = None if full_export else _cutoff_date(args.years)
    engine = db.get_engine()  # live SQL Server engine (read-only login)

    print(f"Extracting Renty snapshot to: {args.out}")
    if full_export:
        print("Full history export (no date filter)\n")
    else:
        print(f"Large fact tables filtered to >= {cutoff} ({args.years} years)\n")

    grand_total = 0
    skipped = []
    for qualified, date_col in TABLES.items():
        effective_date_col = None if full_export else date_col
        try:
            grand_total += _export_table(engine, qualified, effective_date_col, args.out, cutoff)
        except Exception as e:
            msg = str(e)
            # A missing table (e.g. an optional table absent on this instance) is
            # a warning, not a fatal error -- keep exporting the rest.
            if "Invalid object name" in msg or "42S02" in msg or "208" in msg:
                print(f"  SKIPPED (table not found on this server): {qualified}")
                skipped.append(qualified)
                continue
            print(f"  FAILED: {qualified}: {e}")
            return 1

    exported = len(TABLES) - len(skipped)
    print(f"\nDone. {exported}/{len(TABLES)} tables, {grand_total:,} total rows written to {args.out}")
    if skipped:
        print(f"Skipped {len(skipped)} missing table(s): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

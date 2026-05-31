# 🚗 Renty AI Analytics Demo (Direct SQL)

Conversational business intelligence for **Renty** car rental, powered by
**Anthropic Claude Opus 4.7** (via [OpenRouter](https://openrouter.ai)) and
backed by direct read-only queries against the `eJarAnalytics` SQL Server
warehouse (`dwh` schema).

The demo replicates the original MImic multi-step pipeline:

```
classify -> rephrase -> plan -> generate code -> execute (SQL) -> report
```

Every analytical question is answered by Claude writing **T-SQL + pandas**
code that calls `run_query(...)` against the live warehouse. No CSVs are
loaded into memory.

---

## Architecture

```
┌───────────────────┐  user question   ┌───────────────────────┐
│  Streamlit app    ├─────────────────►│  LLMWorkflow          │
│  (app.py)         │                  │  (backend.py)         │
└───────────────────┘                  │                       │
                                       │  classify             │
                                       │  refine               │
                                       │  plan                 │
                                       │  generate python+SQL  │
                                       └──────────┬────────────┘
                                                  │ subprocess
                                                  ▼
                                       ┌───────────────────────┐
                                       │  generated code       │
                                       │  └─ run_query(sql) ───┼──► SQL Server
                                       │     (db.py)           │    dwh.* tables
                                       │  └─ pandas + plt      │
                                       └──────────┬────────────┘
                                                  ▼
                                            output/*.png + stdout
                                                  │
                                                  ▼
                                       reporter LLM call → final answer
```

---

## Quick start

### 1. Prerequisites

- Python 3.10+
- An **OpenRouter** account & API key (https://openrouter.ai/keys)
- **Microsoft ODBC Driver 18 for SQL Server**
- Network access to the SQL Server host (`172.86.86.150` by default)
- A read-only DB user that can `SELECT` on the `dwh` schema

### 2. Install the ODBC driver

**Windows** — usually already installed (comes with SSMS / SQL Server).
If not, download from:
https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server

**macOS**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18 mssql-tools18
```

**Ubuntu / Debian**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list \
    | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### 3. Clone & install Python deps

```bash
git clone https://github.com/Samer-Is/-ai-analytics-demo2.git
cd -ai-analytics-demo2
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure secrets

Copy `.env.example` → `.env` (already exists; just edit it) and fill in:

```dotenv
OPENROUTER_API_KEY=sk-or-...
DB_USER=demo_readonly
DB_PASSWORD=...
```

All other values have sensible defaults.

### 5. Create the read-only DB user (one-time, run on SQL Server as DBA)

```sql
USE eJarAnalytics;
CREATE LOGIN demo_readonly WITH PASSWORD = 'strong_password_here';
CREATE USER demo_readonly FOR LOGIN demo_readonly;
GRANT SELECT ON SCHEMA::dwh TO demo_readonly;
DENY INSERT, UPDATE, DELETE, EXECUTE, ALTER, CONTROL ON SCHEMA::dwh TO demo_readonly;
```

The Python layer also rejects any non-SELECT statement via [db.py](db.py),
but the read-only user is the real safety net.

### 6. Smoke tests

```bash
# OpenRouter / Claude connection
python scripts/smoke_test_llm.py

# SQL Server connection + row counts
python db.py
```

Expected DB output:
```
Connecting to 172.86.86.150/eJarAnalytics ...
Connection OK. Row counts:
  dim_branches: 198
  dim_categories: 37
  fact_daily_features: ~58,000
  fact_contracts_clean: ~3,410,000
  fact_bookings_clean: ~1,884,000
```

### 7. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501. The sidebar will show live row counts; ask
questions in natural English (see examples below).

---

## Example questions

- "Show me monthly booking demand across all branches over the last two years."
- "Which branch had the highest contract count last quarter?"
- "Compare average daily rates by category for 2025."
- "How many rentals are currently out (not yet returned)?"
- "Show me the cancellation rate by source channel for the last 90 days."

The full Tier 1 question set lives in `demo_questions.md` (to be supplied).

---

## File map

| File | Purpose |
|---|---|
| [app.py](app.py) | Streamlit frontend, chat UI, sidebar health panel |
| [backend.py](backend.py) | `LLMWorkflow` pipeline + `LocalCodeExecutor` |
| [db.py](db.py) | SQLAlchemy engine, `run_query`, SQL safety validator |
| [prompts.py](prompts.py) | All 5 stage prompts (classifier → reporter) |
| [context_manager.py](context_manager.py) | Token-aware message truncation |
| [metadata/renty/_schema.json](metadata/renty/_schema.json) | Renty dataset schema (single source of truth for the LLM) |
| [scripts/smoke_test_llm.py](scripts/smoke_test_llm.py) | One-shot OpenRouter ping |
| [.env.example](.env.example) | Template for environment variables |

---

## Cost expectations

Per question (full pipeline: classify + refine + plan + code + report):

- **~$0.02 – $0.10** with Claude Opus 4.7 ($5 / 1M input, $25 / 1M output).
- The schema is large (~22 KB) and is sent on every stage. Future
  optimization: enable OpenRouter prompt caching on the schema portion
  for a 50%+ discount (see Phase 9 in `INSTRUCTIONS.MD`).

---

## Safety

- `db.py` validates every query: must start with `SELECT` or `WITH`,
  rejects `INSERT/UPDATE/DELETE/DROP/ALTER/EXEC/MERGE/TRUNCATE/CREATE/GRANT/REVOKE`,
  rejects multi-statement SQL, enforces a query timeout (default 30 s),
  and truncates result sets at `DB_MAX_ROWS` (default 10,000).
- Even with the validator, run the demo with a **read-only DB login**.
- `.env` is gitignored.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `OPENROUTER_API_KEY is not configured` | Edit `.env` |
| `Login failed for user 'demo_readonly'` | DB creds wrong, or user not created on the server |
| `[Microsoft][ODBC Driver Manager] Data source name not found` | ODBC driver not installed; see step 2 |
| `Code execution timed out` | LLM produced a slow query; refine the question or raise `DB_QUERY_TIMEOUT` |
| `UnsafeSQLError` | Generated SQL tripped the safety filter; usually the question can be rephrased |
| `Column not found` | Schema description mentions a column the DB no longer has; reconcile `metadata/renty/_schema.json` |

---

## Migration notes (from the original GPT-4 + CSV demo)

- **LLM provider:** OpenAI → OpenRouter (compatible SDK; only `base_url`,
  `api_key`, and `extra_headers` change).
- **Model:** `gpt-4o` → `anthropic/claude-opus-4.7`. Single model for V1.
- **Data:** CSVs in `data/*` → live SQL Server queries via `run_query`.
- **Prompts:** Inline f-strings in `backend.py` → centralized in
  [prompts.py](prompts.py), re-tuned with XML tags + JSON output for Claude.

"""
Renty AI Analytics Demo — Streamlit frontend.

Connects to the eJarAnalytics SQL Server (dwh schema) and uses
OpenRouter + Claude Opus 4.7 to plan, code, execute, and report on
analytical questions.
"""
import os
import re
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from backend import (
    DomainSchema,
    LLMWorkflow,
    get_available_domains,
    validate_environment,
)
from db import get_connection_security

load_dotenv(override=True)

DEFAULT_DOMAIN = os.environ.get("DOMAIN", "renty")


# ---------------------------------------------------------------------------
# Streamlit page config & session state
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Renty AI Analytics",
    page_icon="🚗",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "current_domain" not in st.session_state:
    st.session_state.current_domain = None
if "workflow" not in st.session_state:
    st.session_state.workflow = None
if "domain_conversations" not in st.session_state:
    st.session_state.domain_conversations = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def clear_output_charts():
    try:
        output_dir = Path("output")
        if output_dir.exists():
            for chart_file in output_dir.glob("*.png"):
                chart_file.unlink(missing_ok=True)
    except Exception as e:
        st.warning(f"Could not clear previous charts: {e}")


def extract_sql(code: str) -> str:
    """Pull SQL strings out of generated code (var assignments or inline run_query)."""
    if not code:
        return ""
    found = []
    # Triple-quoted assignments: sql = """...""" / query = '''...'''
    for m in re.finditer(
        r"""(?:^|\n)\s*\w*(?:sql|query)\w*\s*=\s*(?:f|r|rf|fr)?(['"]{3})(.*?)\1""",
        code,
        re.DOTALL | re.IGNORECASE,
    ):
        found.append(m.group(2).strip())
    # Inline triple-quoted run_query("""...""")
    for m in re.finditer(
        r"""run_query\(\s*(?:f|r|rf|fr)?(['"]{3})(.*?)\1""",
        code,
        re.DOTALL,
    ):
        found.append(m.group(2).strip())
    # Deduplicate while preserving order.
    seen = set()
    unique = [s for s in found if s and not (s in seen or seen.add(s))]
    return "\n\n".join(unique)


def initialize_workflow(domain: str) -> bool:
    try:
        if st.session_state.current_domain and st.session_state.current_domain != domain:
            st.session_state.domain_conversations[st.session_state.current_domain] = (
                st.session_state.messages.copy()
            )

        if st.session_state.workflow:
            st.session_state.workflow.cleanup()

        workflow = LLMWorkflow()
        if workflow.initialize_domain(domain):
            st.session_state.workflow = workflow
            st.session_state.current_domain = domain
            st.session_state.messages = st.session_state.domain_conversations.get(domain, []).copy()
            return True
        st.error(f"Failed to initialize {domain} domain. Check schema and credentials.")
        return False
    except Exception as e:
        st.error(f"Error initializing workflow: {e}")
        return False


@st.cache_data(ttl=600, show_spinner=False)
def get_table_counts() -> dict:
    """Run a few cheap COUNT(*) queries for the sidebar health panel."""
    from db import run_query

    queries = {
        "Branches": "SELECT COUNT(*) AS n FROM dwh.dim_branches",
        "Categories": "SELECT COUNT(*) AS n FROM dwh.dim_categories",
        "Car models": "SELECT COUNT(*) AS n FROM dwh.dim_carmodels",
        "Daily features": "SELECT COUNT(*) AS n FROM dwh.fact_daily_features",
        "Contracts": "SELECT COUNT(*) AS n FROM dwh.fact_contracts_clean",
        "Bookings": "SELECT COUNT(*) AS n FROM dwh.fact_bookings_clean",
    }
    return {k: int(run_query(v).iloc[0]["n"]) for k, v in queries.items()}


# ---------------------------------------------------------------------------
# UI: header
# ---------------------------------------------------------------------------
def render_header():
    st.markdown(
        """
        # 🚗 <span style="color:#2E86AB;">Renty</span> AI Analytics
        **Conversational business intelligence on rental data — powered by Claude Opus 4.7**
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# UI: sidebar
# ---------------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("# 🚗 Renty Analytics")
        st.caption("OpenRouter • Claude Opus 4.7 • SQL Server `dwh`")
        st.markdown("---")

        # --- Domain selector ---
        st.subheader("📂 Domain")
        available = get_available_domains()
        if not available:
            st.error("No domains found. Place a `_schema.json` under `metadata/<domain>/`.")
            return

        default_index = (
            available.index(DEFAULT_DOMAIN) if DEFAULT_DOMAIN in available else 0
        )
        display_names = {
            "renty": "🚗 Renty (rental analytics)",
            "banking": "🏦 Banking",
            "hospital": "🏥 Hospital",
            "education": "🎓 Education",
        }
        selected = st.selectbox(
            "Choose dataset:",
            available,
            format_func=lambda x: display_names.get(x, x.title()),
            index=(
                available.index(st.session_state.current_domain)
                if st.session_state.current_domain in available
                else default_index
            ),
        )

        if selected != st.session_state.current_domain:
            with st.spinner(f"Initializing {selected} ..."):
                if initialize_workflow(selected):
                    clear_output_charts()
                    st.success(f"✅ {selected} ready")
                    st.rerun()

        # --- DB health ---
        st.markdown("---")
        st.subheader("🗄️ Database")
        try:
            counts = get_table_counts()
            for name, n in counts.items():
                st.metric(name, f"{n:,}")
        except Exception as e:
            st.error(f"DB connection failed: {e}")
            st.caption("Edit `.env` with DB_USER / DB_PASSWORD and ensure the ODBC driver is installed.")

        # --- Read-only security audit ---
        with st.expander("🔒 Connection security", expanded=False):
            try:
                sec = get_connection_security()
                if sec.get("error"):
                    st.warning(f"Could not read permissions: {sec['error']}")
                else:
                    if sec["is_readonly"]:
                        st.success(f"Read-only connection as `{sec['user']}`")
                    else:
                        st.error(f"⚠️ Connection as `{sec['user']}` is NOT confirmed read-only")
                    if sec["roles"]:
                        st.caption("Roles: " + ", ".join(sec["roles"]))
                    if sec["denied_permissions"]:
                        st.caption("Denied: " + ", ".join(sec["denied_permissions"]))
            except Exception as e:
                st.warning(f"Security audit unavailable: {e}")

        # --- Schema preview ---
        if st.session_state.current_domain:
            try:
                schema = DomainSchema(st.session_state.current_domain).schema_data
                st.markdown("---")
                with st.expander(f"📊 {schema.get('domain_name', '')}", expanded=False):
                    st.caption(schema.get("domain_description", "")[:600] + " ...")
            except Exception:
                pass

        # --- Session controls ---
        st.markdown("---")
        if st.button("➕ New conversation", type="secondary"):
            if st.session_state.current_domain:
                st.session_state.domain_conversations[st.session_state.current_domain] = []
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                clear_output_charts()
                st.rerun()
        if st.button("🧹 Clear charts"):
            clear_output_charts()
            st.success("Charts cleared.")
            st.rerun()


# ---------------------------------------------------------------------------
# UI: chat rendering
# ---------------------------------------------------------------------------
def render_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            render_assistant_message(message)


def render_assistant_message(message):
    with st.chat_message("assistant"):
        if "content" in message:
            st.markdown(message["content"])

        if message.get("rephrased_question"):
            with st.expander("🔍 Refined question", expanded=False):
                st.markdown(f"> {message['rephrased_question']}")

        if message.get("code"):
            sql_text = extract_sql(message["code"])
            if sql_text:
                with st.expander("🗄️ SQL query", expanded=False):
                    st.code(sql_text, language="sql")
            with st.expander("🔧 Generated code (SQL + pandas)", expanded=False):
                st.code(message["code"], language="python")

        for file_info in message.get("output_files", []) or []:
            file_path = file_info["file_path"]
            file_name = file_info["file_name"]
            if not os.path.exists(file_path):
                continue
            if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                st.image(file_path, caption=file_name)
            else:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {file_name}",
                        data=f.read(),
                        file_name=file_name,
                    )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------
def process_user_input(user_input: str):
    if not st.session_state.workflow:
        st.error("Please select a domain first.")
        return

    st.session_state.messages.append({"role": "user", "content": user_input})

    answer_text = ""
    final_result = None
    with st.chat_message("assistant"):
        status_ph = st.empty()
        answer_ph = st.empty()
        status_ph.markdown("_Analyzing your request ..._")
        try:
            for event in st.session_state.workflow.process_query_stream(
                user_input,
                st.session_state.session_id,
                conversation_history=st.session_state.messages,
            ):
                etype = event.get("type")
                if etype == "status":
                    status_ph.markdown(f"_{event['text']}_")
                elif etype == "answer_delta":
                    answer_text += event["text"]
                    answer_ph.markdown(answer_text)
                    status_ph.empty()
                elif etype == "final":
                    final_result = event.get("result") or {}
            status_ph.empty()
        except Exception as e:
            status_ph.empty()
            st.error(f"Unexpected error: {e}")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Unexpected error: {e}"}
            )
            return

    if final_result is None:
        final_result = {}

    if final_result.get("error"):
        err = final_result["error"]
        st.session_state.messages.append(
            {"role": "assistant", "content": f"I hit an error: {err}"}
        )
        return

    msg = {
        "role": "assistant",
        "content": final_result.get("final_answer") or answer_text or "Analysis complete.",
        "domain": final_result.get("domain"),
        "message_type": final_result.get("message_type"),
        "rephrased_question": final_result.get("rephrased_question"),
    }
    code_results = final_result.get("code_results") or {}
    if code_results.get("generated_code"):
        msg["code"] = code_results["generated_code"]
    execution = code_results.get("execution_result", {})
    if execution.get("output_files"):
        msg["output_files"] = execution["output_files"]
    st.session_state.messages.append(msg)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    checks = validate_environment()

    if not checks["openrouter_key"]:
        st.error("⚠️ **OPENROUTER_API_KEY is not configured.**")
        st.write("Edit `.env` and add your OpenRouter key:")
        st.code("OPENROUTER_API_KEY=sk-or-...")
        st.stop()
    if not checks["required_packages"]:
        st.error("⚠️ **Required packages missing.** Run `pip install -r requirements.txt`.")
        st.stop()
    if not checks["db_env_set"]:
        st.error("⚠️ **Database credentials missing.** Fill in `DB_USER` and `DB_PASSWORD` in `.env`.")
        st.stop()
    if not checks["schemas_available"]:
        st.error("⚠️ **Renty schema missing.** Expected `metadata/renty/_schema.json`.")
        st.stop()

    # First-load: initialize default domain
    if not st.session_state.workflow:
        default = DEFAULT_DOMAIN if DEFAULT_DOMAIN in get_available_domains() else get_available_domains()[0]
        with st.spinner(f"Initializing {default} ..."):
            initialize_workflow(default)

    render_header()
    render_sidebar()
    render_messages()

    if user_input := st.chat_input("Ask a question about Renty's rental data ..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        process_user_input(user_input)
        st.rerun()

    st.markdown(
        """
        ---
        <p style="font-size:0.85em; color:grey; text-align:center;">
        <b>Renty AI Analytics Demo</b> — generated answers may need verification. Numbers come directly from the live database.
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

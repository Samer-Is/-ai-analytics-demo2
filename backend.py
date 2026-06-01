"""
Backend pipeline for the Renty AI Analytics Demo.

Architecture (replicates the original MImic multi-step flow):
    classify -> rephrase -> plan -> generate code -> execute -> report

Key differences from V1:
- LLM provider is OpenRouter (Anthropic Claude Opus 4.7), not OpenAI.
- Data access is direct SQL Server via `db.run_query`, NOT pre-loaded CSV DataFrames.
- Prompts live in `prompts.py` and use Claude/XML conventions.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

import prompts
from context_manager import ContextManager

load_dotenv(override=True)


# ---------------------------------------------------------------------------
# LLM client (OpenRouter)
# ---------------------------------------------------------------------------
def get_openrouter_key() -> Optional[str]:
    """Return the OpenRouter API key from env or Streamlit secrets."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and key.strip() and key != "your_openrouter_key_here":
        return key.strip()
    try:
        import streamlit as st  # type: ignore
        if hasattr(st, "secrets") and "OPENROUTER_API_KEY" in st.secrets:
            secret = st.secrets["OPENROUTER_API_KEY"]
            if secret and secret != "your_openrouter_key_here":
                return secret
    except Exception:
        pass
    return None


def _build_client() -> OpenAI:
    api_key = get_openrouter_key()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured. Edit .env and restart."
        )
    return OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )


def _build_headers() -> Dict[str, str]:
    return {
        "HTTP-Referer": os.environ.get("OPENROUTER_APP_URL", "http://localhost:8501"),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "Renty Analytics Demo"),
    }


MODEL = os.environ.get("LLM_MODEL", "anthropic/claude-opus-4.7")

# Per-stage model routing (Phase 9). Each stage can be pointed at a cheaper or
# stronger model via env vars. All default to the main MODEL so the pipeline
# keeps working even if no per-stage overrides are configured.
#   - classifier / greeter / reporter: light reasoning -> a fast model is fine
#   - refiner / planner: medium reasoning over the schema
#   - coder: hardest stage (correct T-SQL + Python) -> keep on the strongest model
MODEL_CLASSIFIER = os.environ.get("LLM_MODEL_CLASSIFIER", MODEL)
MODEL_GREETER = os.environ.get("LLM_MODEL_GREETER", MODEL)
MODEL_REFINER = os.environ.get("LLM_MODEL_REFINER", MODEL)
MODEL_PLANNER = os.environ.get("LLM_MODEL_PLANNER", MODEL)
MODEL_CODER = os.environ.get("LLM_MODEL_CODER", MODEL)
MODEL_REPORTER = os.environ.get("LLM_MODEL_REPORTER", MODEL)


# ---------------------------------------------------------------------------
# Result cache (Phase 9): cache the full pipeline result for an identical
# question so re-asking it during a demo is instant and free. In-memory, TTL.
# ---------------------------------------------------------------------------
import time as _time

RESULT_CACHE_TTL = int(os.environ.get("RESULT_CACHE_TTL", "600"))  # seconds
_RESULT_CACHE: Dict[str, Any] = {}


def _cache_key(domain: str, message: str) -> str:
    return f"{domain}::{' '.join(message.lower().split())}"


def _cache_get(domain: str, message: str) -> Optional[Dict[str, Any]]:
    entry = _RESULT_CACHE.get(_cache_key(domain, message))
    if not entry:
        return None
    ts, value = entry
    if _time.time() - ts > RESULT_CACHE_TTL:
        _RESULT_CACHE.pop(_cache_key(domain, message), None)
        return None
    return value


def _cache_put(domain: str, message: str, value: Dict[str, Any]) -> None:
    _RESULT_CACHE[_cache_key(domain, message)] = (_time.time(), value)


# ---------------------------------------------------------------------------
# Schema loader
# ---------------------------------------------------------------------------
class DomainSchema:
    """Loads and caches the schema JSON for a domain."""

    _instances: Dict[str, "DomainSchema"] = {}

    def __new__(cls, domain: str):
        if domain not in cls._instances:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instances[domain] = inst
        return cls._instances[domain]

    def __init__(self, domain: str):
        if self._initialized:
            return
        self.domain = domain
        self.schema_path = Path("metadata") / domain / "_schema.json"
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            self.schema_data = json.load(f)
        self._initialized = True

    @property
    def schema_json(self) -> str:
        """Pretty-printed JSON for inclusion in prompts."""
        return json.dumps(self.schema_data, indent=2, ensure_ascii=False)

    @property
    def tables(self) -> List[Dict[str, Any]]:
        return self.schema_data.get("tables", [])

    @classmethod
    def clear_instances(cls):
        cls._instances.clear()


# ---------------------------------------------------------------------------
# Local code executor (SQL-aware)
# ---------------------------------------------------------------------------
class LocalCodeExecutor:
    """
    Runs LLM-generated Python in a subprocess. The generated code can only
    reach data via `run_query` (imported from db.py); no CSVs are loaded.
    """

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="renty_analytics_")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.container = None  # compatibility shim

    def initialize_container(self, domain: str) -> bool:
        return True

    def _clear_previous_charts(self):
        try:
            for chart in self.output_dir.glob("*.png"):
                chart.unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: could not clear previous charts: {e}")

    def execute_code(self, code: str) -> Dict[str, Any]:
        try:
            self._clear_previous_charts()

            script_path = Path(self.temp_dir) / f"analysis_{uuid.uuid4().hex}.py"
            cwd = os.getcwd()
            output_path = self.output_dir.absolute()

            indented = self._indent_code(code, 4)
            enhanced = f"""
import sys
import os
sys.path.append(r'{cwd}')
os.chdir(r'{cwd}')

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv
load_dotenv(override=True)

from db import run_query

OUTPUT_PATH = r"{output_path}"
os.makedirs(OUTPUT_PATH, exist_ok=True)

try:
{indented}

    if plt.get_fignums():
        plt.savefig(os.path.join(OUTPUT_PATH, 'analysis_chart.png'),
                    dpi=120, bbox_inches='tight')
        plt.close('all')

except Exception as e:
    import traceback
    print(f"Analysis Error: {{e}}")
    traceback.print_exc()
"""

            with open(script_path, "w", encoding="utf-8") as f:
                f.write(enhanced)

            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=cwd,
                env=os.environ.copy(),  # pass DB credentials to subprocess
            )
            script_path.unlink(missing_ok=True)

            output = result.stdout
            if result.stderr and result.returncode != 0:
                output += f"\n\nErrors:\n{result.stderr}"

            return {
                "success": result.returncode == 0,
                "output": output,
                "output_files": self._collect_output_files(),
                "error": result.stderr if result.returncode != 0 else None,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "output_files": [],
                "error": "Code execution timed out (>120 s).",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "output_files": [],
                "error": f"Execution failed: {e}",
            }

    def _indent_code(self, code: str, spaces: int) -> str:
        pad = " " * spaces
        return "\n".join((pad + line) if line.strip() else line for line in code.split("\n"))

    def _collect_output_files(self) -> List[Dict[str, str]]:
        files = []
        if self.output_dir.exists():
            for p in self.output_dir.iterdir():
                if p.is_file():
                    files.append({"file_name": p.name, "file_path": str(p)})
        return files

    def cleanup(self):
        try:
            if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass

    def __del__(self):
        self.cleanup()


# ---------------------------------------------------------------------------
# LLM workflow
# ---------------------------------------------------------------------------
_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"^```(?:python)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def _strip_code_fences(text: str, language: str = "python") -> str:
    """Remove leading/trailing markdown code fences if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        if language == "json":
            stripped = _JSON_FENCE_RE.sub("", stripped).strip()
        else:
            stripped = _CODE_FENCE_RE.sub("", stripped).strip()
    return stripped


def _parse_json(text: str) -> Dict[str, Any]:
    """Best-effort JSON parse; tolerates fences and trailing prose."""
    cleaned = _strip_code_fences(text, "json")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class LLMWorkflow:
    """Multi-step LLM pipeline: classify -> rephrase -> plan -> code -> report."""

    def __init__(self):
        self.client = _build_client()
        self.headers = _build_headers()
        self.model = MODEL
        self.executor: Optional[LocalCodeExecutor] = None
        self.current_domain: Optional[str] = None
        self.context_manager = ContextManager(model_name=self.model)

    # --- domain init ---
    def initialize_domain(self, domain: str) -> bool:
        try:
            self.current_domain = domain
            DomainSchema(domain)  # validate it loads
            self.executor = LocalCodeExecutor()
            return self.executor.initialize_container(domain)
        except Exception as e:
            print(f"Failed to initialize domain {domain}: {e}")
            return False

    # --- single chat helper ---
    def _complete(
        self,
        system: str,
        user: str,
        *,
        model: Optional[str] = None,
        schema_json: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        json_mode: bool = False,
    ) -> str:
        """One LLM round-trip.

        If ``schema_json`` is provided, the schema is attached to the system
        message as a separate content block marked with ``cache_control`` so
        OpenRouter/Anthropic can cache it across stages (big cost + latency win,
        since the same ~6K-token schema is sent on every analytical query).
        """
        if schema_json is not None:
            system_content: Any = [
                {"type": "text", "text": system},
                {
                    "type": "text",
                    "text": f"<schema>\n{schema_json}\n</schema>",
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        else:
            system_content = system

        kwargs: Dict[str, Any] = dict(
            model=model or self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            extra_headers=self.headers,
        )
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()

    # --- streaming chat helper ---
    def _complete_stream(
        self,
        system: str,
        user: str,
        *,
        model: Optional[str] = None,
        schema_json: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.0,
    ):
        """Like ``_complete`` but yields text chunks as they arrive.

        Used by ``process_query_stream`` so the UI can render the answer
        token-by-token instead of waiting for the full response.
        """
        if schema_json is not None:
            system_content: Any = [
                {"type": "text", "text": system},
                {
                    "type": "text",
                    "text": f"<schema>\n{schema_json}\n</schema>",
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        else:
            system_content = system

        response = self.client.chat.completions.create(
            model=model or self.model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            extra_headers=self.headers,
            stream=True,
        )
        for chunk in response:
            try:
                delta = chunk.choices[0].delta.content
            except (AttributeError, IndexError):
                delta = None
            if delta:
                yield delta

    @staticmethod
    def _clarification_message(classification: Dict[str, Any]) -> str:
        """Build a clean, user-facing clarification question.

        The classifier's ``reason`` is meant to be phrased as a question to the
        user; we present it directly and only fall back to a generic prompt
        when it is missing or looks like internal commentary.
        """
        reason = (classification.get("reason") or "").strip()
        looks_internal = (not reason) or reason.lower().startswith(
            ("too vague", "user is", "the user", "vague", "ambiguous", "missing", "needs", "no ")
        )
        if looks_internal or "?" not in reason:
            return (
                "Happy to dig into that — could you tell me a bit more? "
                "For example, which metric (bookings, contracts, demand, pricing, "
                "or utilization), which branch or category, and over what time period?"
            )
        return reason

    # --- agent narration helpers (for the expandable "team thinking" pane) ---
    @staticmethod
    def _agent_router_note(user_message: str, classification: Dict[str, Any]) -> str:
        reason = (classification.get("reason") or "").strip()
        note = "Read the question and routed it to the analytics team as a data request."
        if reason:
            note += f"\n\n> {reason}"
        return note

    @staticmethod
    def _agent_analyst_note(refined_question: str, refined: Dict[str, Any]) -> str:
        note = "Rewrote the question in precise terms the database can answer:\n\n"
        note += f"> {refined_question}"
        assumptions = refined.get("assumptions_made") or []
        if assumptions:
            note += "\n\nAssumptions made:\n" + "\n".join(f"- {a}" for a in assumptions)
        return note

    @staticmethod
    def _agent_planner_note(plan: Dict[str, Any]) -> str:
        steps = plan.get("plan") or []
        note = "Laid out the analysis plan:\n\n"
        note += "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) if steps else "_No explicit steps._"
        primary = plan.get("primary_table")
        output_type = plan.get("output_type")
        tail = []
        if primary:
            tail.append(f"primary table `{primary}`")
        if output_type:
            tail.append(f"output: {output_type.replace('_', ' ')}")
        if tail:
            note += "\n\n" + " · ".join(tail)
        return note

    @staticmethod
    def _agent_engineer_note(execution: Dict[str, Any]) -> str:
        if execution.get("success"):
            note = "Wrote the query, ran it against the warehouse, and collected the results."
            files = execution.get("output_files") or []
            if any(str(f).lower().endswith((".png", ".jpg", ".jpeg")) for f in files):
                note += " A chart was generated from the output."
            return note
        err = (execution.get("error") or "").strip()
        note = "Ran the query but it did not return usable results."
        if err:
            note += f"\n\n> {err[:300]}"
        return note

    # --- public entry point ---
    def process_query(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        if not self.current_domain or not self.executor:
            return {"error": "Domain not initialized"}

        # Phase 9: serve an identical recent question straight from cache.
        cached = _cache_get(self.current_domain, user_message)
        if cached is not None:
            return {**cached, "from_cache": True}

        try:
            classification = self._classify_message(user_message, conversation_history)
            category = classification.get("category", "ANALYTICAL").upper()

            if category == "CHITCHAT":
                return self._handle_chitchat(user_message)

            if category == "CLARIFICATION_NEEDED":
                return {
                    "success": True,
                    "message_type": "clarification",
                    "final_answer": self._clarification_message(classification),
                    "domain": self.current_domain,
                }

            refined = self._rephrase_question(user_message, conversation_history)
            refined_question = refined.get("refined_question", user_message)

            plan = self._create_analysis_plan(refined_question)
            plan_text = "\n".join(f"- {s}" for s in plan.get("plan", []))

            code_results = self._execute_analysis_plan(refined_question, plan_text)

            final_answer = self._generate_final_report(refined_question, code_results)

            result = {
                "success": True,
                "message_type": "analysis",
                "classification": classification,
                "rephrased_question": refined_question,
                "refinement": refined,
                "analysis_plan": plan,
                "code_results": code_results,
                "final_answer": final_answer,
                "domain": self.current_domain,
            }
            # Only cache fully successful analyses (don't cache failures).
            if code_results.get("execution_result", {}).get("success"):
                _cache_put(self.current_domain, user_message, result)
            return result
        except Exception as e:
            return {"error": f"Workflow error: {e}"}

    # --- public streaming entry point ---
    def process_query_stream(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
    ):
        """Generator version of ``process_query``.

        Yields event dicts so the UI can render progress and the answer as
        soon as each part is ready, instead of blocking on the full pipeline:
          {"type": "status",       "text": "..."}        progress label
          {"type": "refined",      "refined_question": "..."}
          {"type": "code",         "code": "...", "output_files": [...]}
          {"type": "answer_delta", "text": "..."}        streamed answer chunk
          {"type": "final",        "result": {...}}       full result dict
        """
        if not self.current_domain or not self.executor:
            yield {"type": "final", "result": {"error": "Domain not initialized"}}
            return

        # Phase 9: serve an identical recent question straight from cache.
        cached = _cache_get(self.current_domain, user_message)
        if cached is not None:
            answer = cached.get("final_answer", "")
            if answer:
                yield {"type": "answer_delta", "text": answer}
            yield {"type": "final", "result": {**cached, "from_cache": True}}
            return

        try:
            yield {"type": "status", "text": "Understanding your question ..."}
            classification = self._classify_message(user_message, conversation_history)
            category = classification.get("category", "ANALYTICAL").upper()

            if category == "CHITCHAT":
                collected: List[str] = []
                try:
                    for delta in self._complete_stream(
                        prompts.GREETER_SYSTEM,
                        prompts.GREETER_USER.format(user_message=user_message),
                        model=MODEL_GREETER,
                        max_tokens=320,
                        temperature=0.4,
                    ):
                        collected.append(delta)
                        yield {"type": "answer_delta", "text": delta}
                except Exception:
                    pass
                content = "".join(collected).strip() or (
                    "Hi! I'm a rental analytics assistant. I can help you explore demand, "
                    "pricing, bookings, utilization, and contracts. What would you like to look at?"
                )
                yield {
                    "type": "final",
                    "result": {
                        "success": True,
                        "message_type": "greeting",
                        "final_answer": content,
                        "domain": self.current_domain,
                    },
                }
                return

            if category == "CLARIFICATION_NEEDED":
                msg = self._clarification_message(classification)
                yield {"type": "answer_delta", "text": msg}
                yield {
                    "type": "final",
                    "result": {
                        "success": True,
                        "message_type": "clarification",
                        "final_answer": msg,
                        "domain": self.current_domain,
                    },
                }
                return

            yield {"type": "status", "text": "Refining the question ..."}
            yield {
                "type": "agent",
                "agent": "router",
                "content": self._agent_router_note(user_message, classification),
            }
            refined = self._rephrase_question(user_message, conversation_history)
            refined_question = refined.get("refined_question", user_message)
            yield {"type": "refined", "refined_question": refined_question}
            yield {
                "type": "agent",
                "agent": "analyst",
                "content": self._agent_analyst_note(refined_question, refined),
            }

            yield {"type": "status", "text": "Planning the analysis ..."}
            plan = self._create_analysis_plan(refined_question)
            plan_text = "\n".join(f"- {s}" for s in plan.get("plan", []))
            yield {
                "type": "agent",
                "agent": "planner",
                "content": self._agent_planner_note(plan),
            }

            yield {"type": "status", "text": "Querying the database ..."}
            code_results = self._execute_analysis_plan(refined_question, plan_text)
            execution = code_results.get("execution_result", {})
            yield {
                "type": "code",
                "code": code_results.get("generated_code", ""),
                "output_files": execution.get("output_files", []),
            }
            yield {
                "type": "agent",
                "agent": "engineer",
                "content": self._agent_engineer_note(execution),
            }
            yield {
                "type": "agent",
                "agent": "writer",
                "content": (
                    "Reviewed the query results and wrote the summary you see above, "
                    "highlighting the key figures and the main takeaway."
                ),
            }

            # Stream the final narrative report.
            if not execution.get("success"):
                final_answer = self._generate_final_report(refined_question, code_results)
                yield {"type": "answer_delta", "text": final_answer}
            else:
                yield {"type": "status", "text": "Writing the answer ..."}
                collected = []
                try:
                    for delta in self._generate_final_report_stream(refined_question, code_results):
                        collected.append(delta)
                        yield {"type": "answer_delta", "text": delta}
                except Exception:
                    collected = []
                final_answer = "".join(collected).strip()
                if not final_answer:
                    final_answer = self._generate_final_report(refined_question, code_results)
                    yield {"type": "answer_delta", "text": final_answer}

            result = {
                "success": True,
                "message_type": "analysis",
                "classification": classification,
                "rephrased_question": refined_question,
                "refinement": refined,
                "analysis_plan": plan,
                "code_results": code_results,
                "final_answer": final_answer,
                "domain": self.current_domain,
            }
            if execution.get("success"):
                _cache_put(self.current_domain, user_message, result)
            yield {"type": "final", "result": result}
        except Exception as e:
            yield {"type": "final", "result": {"error": f"Workflow error: {e}"}}

    # --- stage A: classifier ---
    def _classify_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        context_lines: List[str] = []
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = msg.get("role", "unknown").title()
                content = (msg.get("content", "") or "")[:200]
                context_lines.append(f"{role}: {content}")
        context_text = "\n".join(context_lines) if context_lines else "(none)"

        raw = self._complete(
            prompts.CLASSIFIER_SYSTEM,
            prompts.CLASSIFIER_USER.format(
                user_message=message,
                conversation_context=context_text,
            ),
            model=MODEL_CLASSIFIER,
            max_tokens=120,
            temperature=0.0,
            json_mode=True,
        )
        try:
            return _parse_json(raw)
        except Exception:
            # Conservative fallback: treat as analytical so the user is not blocked.
            return {"category": "ANALYTICAL", "reason": "classifier parse fallback"}

    # --- stage A2: chitchat ---
    def _handle_chitchat(self, message: str) -> Dict[str, Any]:
        try:
            content = self._complete(
                prompts.GREETER_SYSTEM,
                prompts.GREETER_USER.format(user_message=message),
                model=MODEL_GREETER,
                max_tokens=320,
                temperature=0.4,
            )
        except Exception:
            content = (
                "Hi! I'm a rental analytics assistant. I can help you explore demand, "
                "pricing, bookings, utilization, and contracts. What would you like to look at?"
            )
        return {
            "success": True,
            "message_type": "greeting",
            "final_answer": content,
            "domain": self.current_domain,
        }

    # --- stage B: refinement ---
    def _rephrase_question(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        schema_json = DomainSchema(self.current_domain).schema_json

        context_lines: List[str] = []
        if conversation_history:
            recent = conversation_history[-6:]
            for msg in recent:
                role = msg.get("role", "unknown").title()
                content = (msg.get("content", "") or "")[:200]
                context_lines.append(f"{role}: {content}")
        context_text = "\n".join(context_lines) if context_lines else "(none)"

        user_msg = prompts.REFINER_USER.format(
            user_question=question,
            conversation_context=context_text,
        )
        try:
            raw = self._complete(
                prompts.REFINER_SYSTEM,
                user_msg,
                model=MODEL_REFINER,
                schema_json=schema_json,
                max_tokens=500,
                temperature=0.0,
                json_mode=True,
            )
            return _parse_json(raw)
        except Exception:
            return {"refined_question": question, "assumptions_made": []}

    # --- stage C: planner ---
    def _create_analysis_plan(self, refined_question: str) -> Dict[str, Any]:
        schema_json = DomainSchema(self.current_domain).schema_json
        user_msg = prompts.PLANNER_USER.format(
            refined_question=refined_question,
        )
        try:
            raw = self._complete(
                prompts.PLANNER_SYSTEM,
                user_msg,
                model=MODEL_PLANNER,
                schema_json=schema_json,
                max_tokens=1500,
                temperature=0.0,
                json_mode=True,
            )
            return _parse_json(raw)
        except Exception:
            return {
                "plan": ["Analyze the refined question against the primary table."],
                "primary_table": "dwh.fact_daily_features",
                "output_type": "table",
            }

    # --- stage D: code generation + execution ---
    def _execute_analysis_plan(self, refined_question: str, plan_text: str) -> Dict[str, Any]:
        schema_json = DomainSchema(self.current_domain).schema_json
        user_msg = prompts.CODER_USER.format(
            refined_question=refined_question,
            plan=plan_text,
        )
        # In offline mode the data is served by DuckDB over Parquet, so append a
        # DuckDB dialect override that supersedes the T-SQL guidance.
        coder_system = prompts.CODER_SYSTEM
        if os.environ.get("DATA_SOURCE", "live").strip().lower() == "offline":
            coder_system = prompts.CODER_SYSTEM + prompts.CODER_DUCKDB_OVERRIDE
        try:
            raw = self._complete(
                coder_system,
                user_msg,
                model=MODEL_CODER,
                schema_json=schema_json,
                max_tokens=4000,
                temperature=0.0,
            )
            code = _strip_code_fences(raw, "python")
            execution_result = self.executor.execute_code(code)
            return {
                "generated_code": code,
                "analysis_code_only": code,
                "execution_result": execution_result,
            }
        except Exception as e:
            return {
                "generated_code": "",
                "analysis_code_only": "",
                "execution_result": {
                    "success": False,
                    "output": "",
                    "output_files": [],
                    "error": f"Code generation failed: {e}",
                },
            }

    # --- stage E: reporter ---
    def _generate_final_report(self, refined_question: str, code_results: Dict[str, Any]) -> str:
        execution = code_results.get("execution_result", {})
        if not execution.get("success"):
            err = execution.get("error") or "the analysis did not complete."
            return (
                "I could not finish that analysis. Please try a slightly different "
                f"question or check the database connection. Details: {err}"
            )

        analysis_output = execution.get("output", "")
        if len(analysis_output) > 8000:
            analysis_output = analysis_output[:8000] + "\n...[truncated]"

        user_msg = prompts.REPORTER_USER.format(
            refined_question=refined_question,
            analysis_output=analysis_output,
        )
        try:
            return self._complete(
                prompts.REPORTER_SYSTEM,
                user_msg,
                model=MODEL_REPORTER,
                max_tokens=1200,
                temperature=0.3,
            )
        except Exception as e:
            return f"Analysis ran, but I could not format the summary: {e}"

    def _generate_final_report_stream(self, refined_question: str, code_results: Dict[str, Any]):
        """Streaming variant of ``_generate_final_report``; yields text chunks."""
        execution = code_results.get("execution_result", {})
        if not execution.get("success"):
            err = execution.get("error") or "the analysis did not complete."
            yield (
                "I could not finish that analysis. Please try a slightly different "
                f"question or check the database connection. Details: {err}"
            )
            return

        analysis_output = execution.get("output", "")
        if len(analysis_output) > 8000:
            analysis_output = analysis_output[:8000] + "\n...[truncated]"

        user_msg = prompts.REPORTER_USER.format(
            refined_question=refined_question,
            analysis_output=analysis_output,
        )
        yield from self._complete_stream(
            prompts.REPORTER_SYSTEM,
            user_msg,
            model=MODEL_REPORTER,
            max_tokens=1200,
            temperature=0.3,
        )

    def cleanup(self):
        if self.executor:
            self.executor.cleanup()


# ---------------------------------------------------------------------------
# Module-level helpers used by app.py
# ---------------------------------------------------------------------------
def get_available_domains() -> List[str]:
    domains: List[str] = []
    metadata_dir = Path("metadata")
    if metadata_dir.exists():
        for d in metadata_dir.iterdir():
            if d.is_dir() and (d / "_schema.json").exists():
                domains.append(d.name)
    return sorted(domains)


def validate_environment() -> Dict[str, Any]:
    """Quick environment health check used by the Streamlit UI."""
    checks = {
        "openrouter_key": bool(get_openrouter_key()),
        "python_available": True,
        "required_packages": True,
        "db_env_set": all(
            os.environ.get(k) for k in ("DB_SERVER", "DB_DATABASE", "DB_USER", "DB_PASSWORD")
        ),
        "schemas_available": (Path("metadata") / "renty" / "_schema.json").exists(),
    }
    try:
        import pandas  # noqa: F401
        import matplotlib  # noqa: F401
        import seaborn  # noqa: F401
        import numpy  # noqa: F401
        import sqlalchemy  # noqa: F401
        import pyodbc  # noqa: F401
    except ImportError:
        checks["required_packages"] = False
    return checks

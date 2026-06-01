"""
Renty AI Analytics — FastAPI backend for the ChatGPT-style web UI.

Reuses the existing ``backend.LLMWorkflow`` engine unchanged. Exposes:
  GET  /                      -> the single-page chat app
  GET  /static/*              -> frontend assets (css/js)
  GET  /api/info              -> domain + database summary for the sidebar
  POST /api/chat   (SSE)      -> streams the pipeline events token-by-token
  GET  /api/chart/{name}      -> serves a generated chart/file
  GET  /health                -> liveness probe
"""
import json
import os
import re
import shutil
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import (
    LLMWorkflow,
    get_available_domains,
    validate_environment,
)

load_dotenv(override=True)

DEFAULT_DOMAIN = os.environ.get("DOMAIN", "renty")

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
SERVED_DIR = BASE_DIR / "output" / "served"
SERVED_DIR.mkdir(parents=True, exist_ok=True)

# A single shared workflow (holds the executor + active domain). Requests are
# serialized with a lock so concurrent chart writes don't collide.
_workflow: Optional[LLMWorkflow] = None
_workflow_lock = threading.Lock()

app = FastAPI(title="Renty AI Analytics")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ---------------------------------------------------------------------------
# Workflow lifecycle
# ---------------------------------------------------------------------------
def _ensure_workflow() -> LLMWorkflow:
    global _workflow
    if _workflow is not None:
        return _workflow
    checks = validate_environment()
    if not checks["openrouter_key"]:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")
    available = get_available_domains()
    domain = DEFAULT_DOMAIN if DEFAULT_DOMAIN in available else (available[0] if available else None)
    if not domain:
        raise RuntimeError("No domains found under metadata/<domain>/_schema.json")
    wf = LLMWorkflow()
    if not wf.initialize_domain(domain):
        raise RuntimeError(f"Failed to initialize domain '{domain}'.")
    _workflow = wf
    return _workflow


@app.on_event("startup")
def _startup() -> None:
    try:
        _ensure_workflow()
        print("[server] workflow initialized.")
    except Exception as e:  # don't crash; surface lazily on first request
        print(f"[server] workflow init deferred: {e}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _extract_sql(code: str) -> str:
    """Pull SQL strings out of generated code (var assignments or inline)."""
    if not code:
        return ""
    found: List[str] = []
    for m in re.finditer(
        r"""(?:^|\n)\s*\w*(?:sql|query)\w*\s*=\s*(?:f|r|rf|fr)?(['"]{3})(.*?)\1""",
        code,
        re.DOTALL | re.IGNORECASE,
    ):
        found.append(m.group(2).strip())
    for m in re.finditer(
        r"""run_query\(\s*(?:f|r|rf|fr)?(['"]{3})(.*?)\1""",
        code,
        re.DOTALL,
    ):
        found.append(m.group(2).strip())
    seen = set()
    unique = [s for s in found if s and not (s in seen or seen.add(s))]
    return "\n\n".join(unique)


def _stash_output_files(output_files: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Copy generated files to a stable served/ folder so chat history keeps them
    even after the next query clears the working output dir. Returns URL refs."""
    refs: List[Dict[str, str]] = []
    for f in output_files or []:
        try:
            p = Path(f.get("file_path", ""))
            if not p.exists() or not p.is_file():
                continue
            served_name = f"{uuid.uuid4().hex}_{p.name}"
            shutil.copy2(p, SERVED_DIR / served_name)
            kind = "image" if p.suffix.lower() in (".png", ".jpg", ".jpeg") else "file"
            refs.append(
                {
                    "name": p.name,
                    "url": f"/api/chart/{served_name}",
                    "kind": kind,
                }
            )
        except Exception:
            continue
    return refs


def _sse(event: Dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index() -> Any:
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=500, detail="Frontend not built.")
    return FileResponse(str(index_file))


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/info")
def info() -> Dict[str, Any]:
    domain = _workflow.current_domain if _workflow else DEFAULT_DOMAIN
    data: Dict[str, Any] = {
        "domain": domain,
        "model": os.environ.get("LLM_MODEL", "anthropic/claude-opus-4.7"),
        "counts": {},
    }
    try:
        from db import run_query

        queries = {
            "Branches": "SELECT COUNT(*) AS n FROM dwh.dim_branches",
            "Categories": "SELECT COUNT(*) AS n FROM dwh.dim_categories",
            "Car models": "SELECT COUNT(*) AS n FROM dwh.dim_carmodels",
            "Contracts": "SELECT COUNT(*) AS n FROM dwh.fact_contracts_clean",
            "Bookings": "SELECT COUNT(*) AS n FROM dwh.fact_bookings_clean",
        }
        data["counts"] = {k: int(run_query(v).iloc[0]["n"]) for k, v in queries.items()}
    except Exception as e:
        data["counts_error"] = str(e)
    return data


@app.get("/api/chart/{name}")
def chart(name: str) -> Any:
    # Path-traversal guard: only a bare filename is allowed.
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid file name.")
    target = SERVED_DIR / name
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="Not found.")
    return FileResponse(str(target))


@app.post("/api/chat")
def chat(req: ChatRequest) -> StreamingResponse:
    try:
        wf = _ensure_workflow()
    except Exception as e:
        def _err():
            yield _sse({"type": "error", "text": str(e)})
            yield _sse({"type": "done"})
        return StreamingResponse(_err(), media_type="text/event-stream")

    message = (req.message or "").strip()
    history = req.history or []

    def event_stream():
        acquired = _workflow_lock.acquire(timeout=180)
        if not acquired:
            yield _sse({"type": "error", "text": "Server busy, please retry."})
            yield _sse({"type": "done"})
            return
        try:
            for event in wf.process_query_stream(
                message,
                session_id=None,
                conversation_history=history,
            ):
                etype = event.get("type")
                if etype == "status":
                    yield _sse({"type": "status", "text": event.get("text", "")})
                elif etype == "refined":
                    yield _sse(
                        {"type": "refined", "text": event.get("refined_question", "")}
                    )
                elif etype == "code":
                    code = event.get("code", "") or ""
                    files = _stash_output_files(event.get("output_files", []))
                    yield _sse(
                        {
                            "type": "code",
                            "code": code,
                            "sql": _extract_sql(code),
                            "files": files,
                        }
                    )
                elif etype == "answer_delta":
                    yield _sse({"type": "delta", "text": event.get("text", "")})
                elif etype == "final":
                    result = event.get("result") or {}
                    if result.get("error"):
                        yield _sse({"type": "error", "text": result["error"]})
                    # If no code event fired (chitchat) but final has files, stash them.
                    yield _sse(
                        {
                            "type": "final",
                            "message_type": result.get("message_type"),
                        }
                    )
            yield _sse({"type": "done"})
        except Exception as e:
            yield _sse({"type": "error", "text": f"Server error: {e}"})
            yield _sse({"type": "done"})
        finally:
            _workflow_lock.release()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

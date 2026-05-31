"""Batch-test a representative spread of Tier 1 demo questions through the
full pipeline. Reports per-question: message type, execution success, whether a
chart/report was produced, and timing. Use before a live demo to catch failures.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(override=True)

from backend import LLMWorkflow

# Full sweep: all 20 Tier 1 + 4 Tier 2 questions from demo_questions.md.
QUESTIONS = [
    # --- Tier 1: Demand patterns ---
    "Show me monthly booking demand across all branches over the last two years. Highlight the seasonal pattern.",
    "Compare weekend versus weekday demand by category. Is the pattern different for SUVs versus Compact?",
    "Which branch has the most consistent demand, and which is the most volatile?",
    "Show the demand pattern for Compact category at RUH airport across 2025.",
    "What does the forward booking pipeline look like for the next 60 days, broken down by branch?",
    # --- Tier 1: Pricing analysis ---
    "What is the average realized daily rate by category across all branches over the past 12 months?",
    "Compare the gap between catalogue rates and realized rates by category. Where are we discounting the most?",
    "Show me the maximum daily rate observed per category by month. When did we charge our highest rates?",
    "How has the average rate for Intermediate SUV trended over the last 18 months at Jeddah airport?",
    # --- Tier 1: Competitive positioning ---
    "For each branch and category combination where we have competitor data, show our average rate next to the competitor median. Where are we above market, where below?",
    "Show me the categories where we have the widest spread versus competitors.",
    # --- Tier 1: Utilization and fleet ---
    "What was the utilization rate for Compact category at RUH airport last month? Use the formula Rented divided by Ready plus Rented plus Maintenance.",
    "Which branch has the most vehicles in Maintenance status on average?",
    "Show the utilization trend by branch over the past 90 days.",
    # --- Tier 1: Channel mix ---
    "What share of bookings comes from mobile apps versus website versus brokers? Show the trend over the last year.",
    "Compare booking volumes by source channel between Riyadh and Jeddah airports.",
    "How has the iPhone app share grown compared to Android over the last 24 months?",
    # --- Tier 1: Operational signals ---
    "Identify the top 10 (branch, category, date) cells with the highest demand-to-supply ratio over the past 6 months.",
    "On which days did we run out of Ready vehicles for any category at any branch?",
    "Show me the relationship between price and demand for Economy SUV at Dammam airport. Is there visible price elasticity?",
    # --- Tier 2: Stretch (data gotchas) ---
    "Compare booking cancellation rate by source channel.",
    "What share of bookings on the iPhone app get abandoned at the payment gateway?",
    "Show me corporate booking volumes per month.",
    "Which models within the Compact category drive the most demand?",
]

# How many questions belong to Tier 1 (the rest are Tier 2).
TIER1_COUNT = 20


def summarize(result: dict) -> dict:
    code_results = result.get("code_results", {}) or {}
    exec_result = code_results.get("execution_result", {}) or {}
    final = result.get("final_answer", "") or ""
    output = exec_result.get("output", "") or ""
    has_chart = "data:image" in output or "<img" in final or "```" in final or "chart" in output.lower()
    return {
        "message_type": result.get("message_type"),
        "exec_success": exec_result.get("success"),
        "exec_error": (exec_result.get("error") or "")[:200],
        "answer_len": len(final),
        "has_chart_signal": has_chart,
        "pipeline_error": result.get("error"),
    }


def main() -> None:
    wf = LLMWorkflow()
    ok = wf.initialize_domain("renty")
    print(f"Domain init: {ok}\n")

    # Optional: pass specific 1-based question numbers to run only those,
    # e.g. `python scripts/test_demo_questions.py 14-24` or `14 15 16`.
    only = set()
    for arg in sys.argv[1:]:
        if "-" in arg:
            a, b = arg.split("-", 1)
            only.update(range(int(a), int(b) + 1))
        else:
            only.add(int(arg))

    passed = 0
    rows = []
    for i, q in enumerate(QUESTIONS, 1):
        if only and i not in only:
            continue
        tier = "T1" if i <= TIER1_COUNT else "T2"
        print(f"[{i}/{len(QUESTIONS)}] ({tier}) {q[:66]}...")
        t0 = time.time()
        try:
            result = wf.process_query(q)
            s = summarize(result)
            elapsed = time.time() - t0
            ok_q = bool(s["exec_success"]) and not s["pipeline_error"] and s["answer_len"] > 0
            passed += int(ok_q)
            status = "PASS" if ok_q else "FAIL"
            print(
                f"    {status} | type={s['message_type']} | exec={s['exec_success']} | "
                f"answer_chars={s['answer_len']} | {elapsed:.1f}s"
            )
            if not ok_q:
                print(f"    exec_error: {s['exec_error']}")
                print(f"    pipeline_error: {s['pipeline_error']}")
            rows.append((i, tier, status, elapsed))
        except Exception as e:  # noqa: BLE001
            elapsed = time.time() - t0
            print(f"    FAIL (exception) | {type(e).__name__}: {str(e)[:200]} | {elapsed:.1f}s")
            rows.append((i, tier, "FAIL", elapsed))
        print()

    t1_pass = sum(1 for i, tier, status, _ in rows if tier == "T1" and status == "PASS")
    t2_pass = sum(1 for i, tier, status, _ in rows if tier == "T2" and status == "PASS")
    t1_total = sum(1 for _, tier, _, _ in rows if tier == "T1")
    t2_total = sum(1 for _, tier, _, _ in rows if tier == "T2")

    print("=" * 70)
    print(f"TIER 1: {t1_pass}/{t1_total} passed   |   TIER 2: {t2_pass}/{t2_total} passed")
    print(f"TOTAL:  {passed}/{len(rows)} run")
    print("-" * 70)
    fails = [(i, tier) for i, tier, status, _ in rows if status == "FAIL"]
    if fails:
        print("Failures:", ", ".join(f"Q{i}({tier})" for i, tier in fails))
    else:
        print("No failures.")
    sys.exit(0 if passed == len(rows) else 1)


if __name__ == "__main__":
    main()

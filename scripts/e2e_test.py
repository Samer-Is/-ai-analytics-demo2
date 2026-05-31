"""End-to-end test: send one analytical question through the full pipeline."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from backend import LLMWorkflow

wf = LLMWorkflow()
ok = wf.initialize_domain("renty")
print(f"Domain init: {ok}")

q = "How many delivered rental contracts were there in the last 30 days?"
print(f"\nQuestion: {q}\n")
result = wf.process_query(q)

print("=" * 70)
print("message_type:", result.get("message_type"))
print("-" * 70)
print("refined_question:", result.get("rephrased_question"))
print("-" * 70)
plan = result.get("analysis_plan", "")
if isinstance(plan, dict):
    import json
    print("plan:", json.dumps(plan, indent=2))
else:
    print("plan:", plan)
print("-" * 70)
code_results = result.get("code_results", {})
print("generated code (first 800 chars):")
print((code_results.get("analysis_code_only") or code_results.get("generated_code", ""))[:800])
print("-" * 70)
exec_result = code_results.get("execution_result", {})
print("execution success:", exec_result.get("success"))
print("execution output (first 1500 chars):")
print((exec_result.get("output") or exec_result.get("error", ""))[:1500])
print("-" * 70)
print("FINAL ANSWER:")
print(result.get("final_answer", ""))
print("=" * 70)
if "error" in result:
    print("ERROR:", result["error"])
    sys.exit(1)

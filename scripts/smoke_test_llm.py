"""
Smoke test for the OpenRouter + Claude Opus 4.7 connection.
Run: python scripts/smoke_test_llm.py
"""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI


def main() -> int:
    load_dotenv(override=True)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY is not set. Edit .env and re-run.")
        return 1

    client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )

    headers = {
        "HTTP-Referer": os.environ.get("OPENROUTER_APP_URL", "http://localhost:8501"),
        "X-Title": os.environ.get("OPENROUTER_APP_NAME", "Renty Analytics Demo"),
    }

    model = os.environ.get("LLM_MODEL", "anthropic/claude-opus-4.7")

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Reply with exactly: OPENROUTER OK"}],
        extra_headers=headers,
        max_tokens=20,
    )

    content = response.choices[0].message.content.strip()
    print(f"Model: {model}")
    print(f"Response: {content}")
    if "OPENROUTER OK" in content.upper():
        print("Smoke test PASSED")
        return 0
    print("Smoke test FAILED: unexpected response")
    return 2


if __name__ == "__main__":
    sys.exit(main())

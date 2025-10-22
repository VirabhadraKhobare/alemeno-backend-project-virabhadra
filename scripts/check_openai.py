"""Small script to validate an OpenAI API key locally.
Usage:
    python scripts/check_openai.py YOUR_API_KEY

It will attempt a small chat completion and print the result or an error.
This file is intentionally not named `test_*.py` so pytest won't collect it.
"""
import sys
import os


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv)
    key = None
    if len(argv) > 1:
        key = argv[1]
    if not key:
        key = os.getenv("OPENAI_API_KEY")

    if not key:
        print("No API key provided. Pass as argument or set OPENAI_API_KEY env var.")
        return 2

    try:
        import openai

        openai.api_key = key
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
            max_tokens=20,
        )

        print("Success. Response:")
        print(resp.choices[0].message.content)
        return 0
    except Exception as e:  # pragma: no cover - simple CLI helper
        print("OpenAI API test failed:", e)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

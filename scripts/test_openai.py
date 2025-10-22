"""Small test script to validate an OpenAI API key locally.
Usage:
    python scripts/test_openai.py YOUR_API_KEY

It will attempt a small chat completion and print the result or an error.
"""
import sys
import os

try:
    key = sys.argv[1]
except IndexError:
    key = os.getenv('OPENAI_API_KEY')

if not key:
    print('No API key provided. Pass as argument or set OPENAI_API_KEY env var.')
    sys.exit(2)

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
except Exception as e:
    print('OpenAI API test failed:', e)
    sys.exit(3)

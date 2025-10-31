import os


# Simple ML integration module.
# If OPENAI_API_KEY is set (or provided to the function), attempts to call OpenAI.
# Otherwise returns a mock summary.


def summarize_text(text: str, api_key: str | None | bool = None) -> str:
    """Summarize `text`.

    Parameters
    - text: input text to summarize
    - api_key: optional OpenAI API key to use for this call; if omitted the function
      will attempt to read the `OPENAI_API_KEY` environment variable.

    Returns a short summary string. Falls back to a naive heuristic if no API key
    is available or the API call fails.
    """
    if not text:
        return ""

    # If caller passes False explicitly, treat as 'do not use API' (force local heuristic)
    if api_key is False:
        key = None
    else:
        key = api_key or os.getenv("OPENAI_API_KEY")

    if key:
        try:
            import openai

            openai.api_key = key
            # Use the Chat Completions if available (model name may change)
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following text in 2-3 sentences:\n\n{text}",
                    }
                ],
                max_tokens=150,
                temperature=0.2,
            )

            # extract text
            return response.choices[0].message.content.strip()
        except Exception:
            # If real API fails, fallback to mock
            return f"(openai-fallback) {text[:200]}"

    # Mock summarization (simple heuristic)
    sentences = text.strip().split('.')
    if len(sentences) <= 2:
        return text if len(text) < 300 else text[:300]

    # return first two sentences as a naive summary
    return ".".join(sentences[:2]).strip() + "."

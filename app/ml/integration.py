import os
# Simple ML integration module.
# If OPENAI_API_KEY is set, attempts to call OpenAI. Otherwise returns a mock summary.

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

def summarize_text(text: str) -> str:
    if not text:
        return ''
    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            # Use the Chat Completions if available (model name may change)
            response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{'role':'user','content':f'Summarize the following text in 2-3 sentences:\n\n{text}'}],
                max_tokens=150,
                temperature=0.2
            )
            # extract text
            return response.choices[0].message.content.strip()
        except Exception as e:
            # If real API fails, fallback to mock
            return f'(openai-fallback) {text[:200]}'
    # Mock summarization (simple heuristic)
    sentences = text.strip().split('.')
    if len(sentences) <= 2:
        return text if len(text) < 300 else text[:300]
    # return first two sentences as a naive summary
    return '.'.join(sentences[:2]).strip() + '.'

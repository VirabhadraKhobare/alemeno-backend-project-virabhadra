import importlib
import os
from unittest.mock import patch, MagicMock

import pytest

import app.ml.integration as integration


from app.ml.integration import summarize_text


def test_summarize_with_openai_mock(monkeypatch):
    # Ensure OPENAI_KEY is set so the function attempts the openai path
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key-for-test")

    fake_response = MagicMock()
    # mock structure: response.choices[0].message.content
    fake_choice = MagicMock()
    fake_choice.message.content = "This is a mocked summary."
    fake_response.choices = [fake_choice]

    # reload the module so it picks up the changed env var
    importlib.reload(integration)

    # inject a mocked 'openai' into sys.modules so local imports inside the function
    # will pick up the mock
    mocked_openai = MagicMock()
    mocked_openai.ChatCompletion.create.return_value = fake_response
    import sys

    monkeypatch.setitem(sys.modules, "openai", mocked_openai)
    # call summarize_text which performs a local 'import openai' and will use our mock
    result = summarize_text("Long text that would normally be summarized by OpenAI.")
    assert "mocked summary" in result
    # cleanup is handled by monkeypatch


def test_summarize_local_fallback(monkeypatch):
    # Ensure OPENAI_KEY is not set and test local heuristic
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # reload module so OPENAI_KEY reflects the removal
    importlib.reload(integration)
    text = "Sentence one. Sentence two. Sentence three."
    summary = summarize_text(text)
    # naive heuristic: first two sentences
    assert summary.startswith("Sentence one")
    assert "Sentence two" in summary

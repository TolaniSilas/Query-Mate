"""
tests for core/llm.py — the unified LLM gateway.
mocks all provider SDKs so no real API calls are made.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from unittest.mock import patch, MagicMock


# raises ValueError for unsupported provider.
def test_unsupported_provider_raises():
    from querymate.core.llm import chat
    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        chat(system="sys", user="hello", provider="cohere")


# anthropic provider.
@patch("querymate.core.llm.anthropic")
def test_anthropic_returns_text(mock_anthropic):
    mock_client   = MagicMock()
    mock_response = MagicMock()
    mock_response.content[0].text = "  anthropic response  "
    mock_client.messages.create.return_value = mock_response
    mock_anthropic.Anthropic.return_value    = mock_client

    from querymate.core.llm import chat
    result = chat(system="sys", user="hello", provider="anthropic", model="claude-sonnet-4-20250514")

    assert result == "anthropic response"
    mock_client.messages.create.assert_called_once()


@patch("querymate.core.llm.anthropic")
def test_anthropic_connection_error_reraises(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value      = mock_client
    mock_anthropic.APIConnectionError          = Exception
    mock_client.messages.create.side_effect    = mock_anthropic.APIConnectionError("no connection")

    from querymate.core.llm import chat
    with pytest.raises(Exception):
        chat(system="sys", user="hello", provider="anthropic", model="claude-sonnet-4-20250514")


@patch("querymate.core.llm.anthropic")
def test_anthropic_rate_limit_reraises(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value   = mock_client
    mock_anthropic.RateLimitError           = Exception
    mock_client.messages.create.side_effect = mock_anthropic.RateLimitError("rate limit")

    from querymate.core.llm import chat
    with pytest.raises(Exception):
        chat(system="sys", user="hello", provider="anthropic", model="claude-sonnet-4-20250514")


@patch("querymate.core.llm.anthropic")
def test_anthropic_api_status_error_reraises(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value   = mock_client
    mock_anthropic.APIStatusError           = Exception
    mock_client.messages.create.side_effect = mock_anthropic.APIStatusError("bad status")

    from querymate.core.llm import chat
    with pytest.raises(Exception):
        chat(system="sys", user="hello", provider="anthropic", model="claude-sonnet-4-20250514")


# openai provider.
def test_openai_returns_text():
    mock_client   = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = "  openai response  "
    mock_client.responses.create.return_value = mock_response

    with patch("querymate.core.llm.OpenAI", return_value=mock_client):
        from querymate.core import llm
        result = llm._openai(system="sys", user="hello", max_tokens=512, model="gpt-4o")

    assert result == "openai response"


# groq provider.
def test_groq_returns_text():
    mock_client   = MagicMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "groq response"
    mock_client.chat.completions.create.return_value = mock_response

    with patch("querymate.core.llm.Groq", return_value=mock_client):
        from querymate.core import llm
        result = llm._groq(system="sys", user="hello", max_tokens=512, model="llama-3.3-70b-versatile")

    assert result == "groq response"


# gemini provider.
def test_gemini_returns_text():
    mock_genai    = MagicMock()
    mock_client   = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "gemini response"
    mock_client.models.generate_content.return_value = mock_response
    mock_genai.Client.return_value = mock_client

    with patch.dict("sys.modules", {"google": MagicMock(), "google.genai": mock_genai}):
        from querymate.core import llm
        result = llm._gemini(system="sys", user="hello", max_tokens=512, model="gemini-2.0-flash")

    assert result == "gemini response"
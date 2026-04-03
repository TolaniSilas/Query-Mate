"""
single entry point for all LLM calls across the system. it supports four providers: Anthropic, OpenAI, Google Gemini, and Groq.

only API keys are loaded from the environment - provider and 'type' of model are automatically st and could be altered by entering different
model iD as agent attribute. 

supported providers:
    anthropic -> claude-opus-4-6, claude-sonnet-4-6 and so on.
    openai -> gpt-4o, gpt-4o-mini, and other variants.
    groq -> llama-3.3-70b-versatile, llama-3.1-8b-instant, etc.
    gemini -> gemini-2.0-flash, gemini-1.5-pro, etc.
"""

import os
from querymate.core.logger import get_logger
import anthropic
from openai import OpenAI
from groq import Groq
from google import genai
from google.genai import types



logger = get_logger(__name__)
SUPPORTED_PROVIDERS = {"anthropic", "openai", "groq", "gemini"}


def chat(system: str, user: str, max_tokens: int = 1024,
         provider: str = "anthropic", model: str = "claude-opus-4-6") -> str:
    """
    sends a system + user message to the configured LLM provider.
    returns the response text as a string.

    parameters
        system: system prompt
        user: user message
        max_tokens: max tokens for the response
        provider: "anthropic" | "openai" | "groq" | "gemini"
        model: the model name for the chosen provider

    raises
        ValueError: if the provider is not supported
    """

    provider = provider.lower()

    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. "
            f"Choose from: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
        )

    logger.debug("llm | provider: %s | model: %s", provider, model)

    if provider == "anthropic":
        return _anthropic(system, user, max_tokens, model)

    if provider == "openai":
        return _openai(system, user, max_tokens, model)

    if provider == "groq":
        return _groq(system, user, max_tokens, model)

    if provider == "gemini":
        return _gemini(system, user, max_tokens, model)



def _anthropic(system: str, user: str, max_tokens: int, model: str) -> str:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    try:
        response = client.messages.create(
            model = model,
            max_tokens = max_tokens,
            system = system,
            messages = [{"role": "user", "content": user}],
            )
        return response.content[0].text.strip()

    except anthropic.APIConnectionError as e:
        logger.error("llm | anthropic | connection error: %s", str(e.__cause__), exc_info=True)
        raise

    except anthropic.RateLimitError as e:
        logger.error("llm | anthropic | rate limit exceeded (429)")
        raise

    except anthropic.APIStatusError as e:
        logger.error("llm | anthropic | API error | status: %s | response: %s", e.status_code, e.response)
        raise


def _openai(system: str, user: str, max_tokens: int, model: str) -> str:
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = client.responses.create(
        model = model,
        input = user,
        instructions = system,
    )
    return response.output_text.strip()


def _groq(system: str, user: str, max_tokens: int, model: str) -> str:
    
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model = model,
        max_tokens = max_tokens,
        messages = [
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


def _gemini(system: str, user: str, max_tokens: int, model: str) -> str:

    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    response = client.models.generate_content(
        model = model,
        contents = user,
        config = types.GenerateContentConfig(
            system_instruction = system,
            max_output_tokens = max_tokens,
        ),
    )
    return response.text.strip()
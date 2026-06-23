"""
llm_client.py — Thin wrapper around the NVIDIA API.
Uses the OpenAI Python package since NVIDIA's endpoint is OpenAI-compatible.
"""

from openai import OpenAI
import config


def create_client():
    """Create and return an OpenAI client pointed at the NVIDIA API."""
    if not config.API_KEY:
        raise ValueError(
            "NVIDIA_API_KEY is not set!\n"
            "Set it in your .env file or export it:\n"
            "  export NVIDIA_API_KEY=your-key-here"
        )

    return OpenAI(
        base_url=config.API_BASE_URL,
        api_key=config.API_KEY,
    )


def chat(client, messages):
    """
    Send a list of messages to the LLM and return the response.

    Args:
        client:   OpenAI client instance
        messages: List of {"role": "...", "content": "..."} dicts

    Returns:
        A dict with 'content' (the reply text) and 'reasoning' (if any).
    """
    try:
        completion = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            max_tokens=config.MAX_TOKENS,
            stream=False,
        )

        message = completion.choices[0].message

        # gpt-oss-120b is a reasoning model — it may include reasoning_content
        reasoning = getattr(message, "reasoning_content", None)
        content = message.content or ""

        return {
            "content": content.strip(),
            "reasoning": reasoning,
        }

    except Exception as e:
        return {
            "content": f"[LLM Error] {e}",
            "reasoning": None,
        }

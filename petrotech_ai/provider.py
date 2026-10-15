
"""Provider interface for PetroTech AI Core."""

from petrotech_ai.config import (
    get_provider,
    get_groq_api_key,
    get_ollama_base_url,
)


def ask_ai(
    question: str,
    system_prompt: str = (
        "You are PetroTech AI, an engineering assistant. "
        "Be accurate, explain assumptions, show units, and distinguish "
        "verified calculations from estimates. Never invent engineering data."
    ),
) -> str:
    """Send a question to the configured AI provider."""

    question = question.strip()

    if not question:
        raise ValueError("Please enter an engineering question.")

    provider = get_provider()

    if provider == "groq":
        return _ask_groq(question, system_prompt)

    if provider == "ollama":
        return _ask_ollama(question, system_prompt)

    raise ValueError(f"Unsupported provider: {provider}")


def _ask_groq(question: str, system_prompt: str) -> str:
    """Send a question to Groq."""
    from groq import Groq

    api_key = get_groq_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Check your .streamlit/secrets.toml file."
        )

    client = Groq(api_key=api_key, timeout=30.0, max_retries=1)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The AI provider returned an empty response.")

    return answer.strip()


def search_ai(
    question: str,
    system_prompt: str = (
        "You are Engineering AI, an engineering assistant. "
        "Use web search for current or source-dependent questions. "
        "Explain findings clearly and never invent facts or source URLs. "
        "Preserve engineering units and state important assumptions."
    ),
) -> str:
    """Answer a question using Groq browser search."""
    from groq import Groq

    question = question.strip()

    if not question:
        raise ValueError("Please enter a question to search.")

    api_key = get_groq_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Check your .streamlit/secrets.toml file."
        )

    client = Groq(api_key=api_key, timeout=60.0, max_retries=1)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        tools=[{"type": "browser_search"}],
        temperature=0.2,
        stream=False,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The search provider returned an empty response.")

    return answer.strip()



def _ask_ollama(question: str, system_prompt: str) -> str:
    """Send a question to a locally running Ollama server."""
    import requests

    response = requests.post(
        f"{get_ollama_base_url()}/api/chat",
        json={
            "model": "llama3.2:3b",
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        },
        timeout=120,
    )

    response.raise_for_status()
    data = response.json()
    answer = data.get("message", {}).get("content", "")

    if not answer:
        raise RuntimeError("The local model returned an empty response.")

    return answer.strip()


def stream_ai(
    question: str,
    system_prompt: str = (
        "You are Engineering AI, an engineering assistant. "
        "Be accurate, explain assumptions, show units, and distinguish "
        "verified calculations from estimates. Never invent engineering data."
    ),
):
    """Stream an answer from the configured AI provider."""

    question = question.strip()

    if not question:
        raise ValueError("Please enter an engineering question.")

    provider = get_provider()

    if provider == "groq":
        yield from _stream_groq(question, system_prompt)
        return

    if provider == "ollama":
        yield from _stream_ollama(question, system_prompt)
        return

    raise ValueError(f"Unsupported provider: {provider}")


def _stream_groq(question: str, system_prompt: str):
    """Stream response chunks from Groq."""
    from groq import Groq

    api_key = get_groq_api_key()

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. "
            "Check your .streamlit/secrets.toml file."
        )

    client = Groq(api_key=api_key, timeout=60.0, max_retries=1)

    stream = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            yield content


def _stream_ollama(question: str, system_prompt: str):
    """Stream response chunks from a locally running Ollama server."""
    import json

    import requests

    response = requests.post(
        f"{get_ollama_base_url()}/api/chat",
        json={
            "model": "llama3.2:3b",
            "stream": True,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        },
        timeout=120,
        stream=True,
    )

    response.raise_for_status()

    for line in response.iter_lines(decode_unicode=True):
        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        content = data.get("message", {}).get("content")

        if content:
            yield content


def _stream_ollama(question: str, system_prompt: str):
    """Stream response chunks from a locally running Ollama server."""
    import requests
    import json

    response = requests.post(
        f"{get_ollama_base_url()}/api/chat",
        json={
            "model": "llama3.2:3b",
            "stream": True,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question},
            ],
        },
        stream=True,
        timeout=120,
    )

    response.raise_for_status()

    received_content = False

    with response:
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            data = json.loads(line)
            content = data.get("message", {}).get("content", "")

            if content:
                received_content = True
                yield content

    if not received_content:
        raise RuntimeError("The local model returned an empty response.")

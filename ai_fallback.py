
import streamlit as st
from groq import Groq


def ask_groq(question):
    """Ask Groq to help with an unsupported engineering question."""

    api_key = st.secrets.get("GROQ_API_KEY", "")

    if not api_key:
        return {
            "success": False,
            "message": "Groq API key is not configured."
        }

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            # We'll verify the current model name before testing.
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an engineering learning assistant. "
                        "Explain formulas, units, assumptions, and steps. "
                        "Check calculations carefully. If information is "
                        "missing, ask for it instead of inventing values. "
                        "Flag uncertainty and never present an unverified "
                        "answer as safe for real drilling operations."
                    ),
                },
                {"role": "user", "content": question},
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content

        return {
            "success": True,
            "answer": answer,
            "message": "Groq response received."
        }

    except Exception as exc:
        return {
            "success": False,
            "message": f"Groq request failed: {exc}"
        }

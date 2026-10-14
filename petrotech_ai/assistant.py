
"You are Engineering AI, an intelligent engineering assistant covering petroleum, mechanical, electrical, civil, and other engineering fields.\n"

import re


def get_knowledge_context(question: str) -> str:
    """Retrieve relevant engineering references for a question."""
    references = search_references(question)

    if not references:
        return ""

    # The current search function returns a string.
    if isinstance(references, str):
        if references.startswith("No matching engineering reference"):
            return ""
        if references.startswith("Could not read engineering references"):
            return ""
        if references.startswith("Engineering reference file was not found"):
            return ""
        return references

    # Also support a future search function returning dictionaries.
    sections = []

    for reference in references[:3]:
        if isinstance(reference, dict):
            title = reference.get("title", "Engineering reference")
            content = reference.get(
                "content",
                reference.get("explanation", "")
            )
            sections.append(f"Topic: {title}\nContent: {content}")
        else:
            sections.append(str(reference))

    return "\n\n".join(sections)


    if not references:
        return ""

    sections = []

    for reference in references[:3]:
        sections.append(
            f"Topic: {reference['title']}\n"
            f"Subject: {reference['subject']}\n"
            f"Formula: {reference['formula']}\n"
            f"Explanation: {reference['explanation']}\n"
            f"Caution: {reference.get('caution', 'Verify the source and assumptions.')}"
        )

    return "\n\n".join(sections)


try:
    from knowledge_base.engineering_reference import search_references  # pyright: ignore[reportMissingImports]
    from .provider import ask_ai, stream_ai
    from .tools import (
        calculate_api_gravity,
        calculate_formation_pressure,
        calculate_hydrostatic_pressure,
        calculate_required_mud_weight,
    )
except ImportError:  # pragma: no cover - fallback for direct script execution
    from knowledge_base.engineering_reference import search_references  # pyright: ignore[reportMissingImports]
    from provider import ask_ai, stream_ai
    from petrotech_ai.tools import (
        calculate_api_gravity,
        calculate_formation_pressure,
        calculate_hydrostatic_pressure,
        calculate_required_mud_weight,
    )


def extract_number(patterns, text):
    """Return the first matching numeric value, or None."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def answer_question(
    question: str,
    conversation_history: list[dict] | None = None,
) -> dict:
    question = question.strip()

    if not question:
        return {"success": False, "error": "Please enter a question."}

    text = question.lower()


    # 1. Hydrostatic pressure
    if "hydrostatic pressure" in text:
        calculation_requested = any(
            phrase in text
            for phrase in (
                "calculate",
                "compute",
                "work out",
                "find the pressure",
                "what is the pressure",
                "how much pressure",
                "determine the pressure",
            )
        )

        if calculation_requested:
            mud_weight = extract_number(
                [
                    r"(?:mud weight|mud wt|mw)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(?:ppg)?",
                    r"(\d+(?:\.\d+)?)\s*ppg",
                ],
                text,
            )

            tvd = extract_number(
                [
                    r"(?:tvd|true vertical depth|depth)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)",
                    r"(\d+(?:\.\d+)?)\s*(?:ft|feet)\s*(?:tvd|depth)?",
                ],
                text,
            )

            if mud_weight is None or tvd is None:
                return {
                    "success": False,
                    "needs_input": True,
                    "message": (
                        "To calculate hydrostatic pressure, provide mud "
                        "weight in ppg and TVD in feet. Example: Calculate "
                        "hydrostatic pressure for 10 ppg mud at 5000 ft TVD."
                    ),
                }

            try:
                result = calculate_hydrostatic_pressure(mud_weight, tvd)
                return {
                    "success": True,
                    "source": "verified_engineering_tool",
                    **result,
                }
            except (ValueError, TypeError) as exc:
                return {"success": False, "error": str(exc)}




# 2. Formation pressure
    if "formation pressure" in text:
        gradient = extract_number([
            r"(?:gradient|pressure gradient)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
        ], text)

        tvd = extract_number([
            r"(?:tvd|true vertical depth|depth)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
        ], text)

        if gradient is None or tvd is None:
            return {
                "success": False,
                "needs_input": True,
                "message": "Provide the formation pressure gradient in psi/ft and TVD in feet.",
            }

        try:
            result = calculate_formation_pressure(gradient, tvd)
            return {
                "success": True,
                "source": "verified_engineering_tool",
                **result,
            }
        except (ValueError, TypeError) as exc:
            return {"success": False, "error": str(exc)}

    # 3. Required mud weight
    if "required mud weight" in text or "mud weight required" in text:
        pressure = extract_number([
            r"(?:pressure|formation pressure)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
        ], text)

        tvd = extract_number([
            r"(?:tvd|true vertical depth|depth)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
        ], text)

        if pressure is None or tvd is None:
            return {
                "success": False,
                "needs_input": True,
                "message": "Provide pressure in psi and TVD in feet.",
            }

        try:
            result = calculate_required_mud_weight(pressure, tvd)
            return {
                "success": True,
                "source": "verified_engineering_tool",
                **result,
            }
        except (ValueError, TypeError) as exc:
            return {"success": False, "error": str(exc)}

    # 4. API gravity
    if "api gravity" in text:
        specific_gravity = extract_number([
            r"(?:specific gravity|sg)\s*(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
        ], text)

        if specific_gravity is None:
            return {
                "success": False,
                "needs_input": True,
                "message": "Provide the oil's specific gravity, for example: API gravity for specific gravity 0.85.",
            }

        try:
            result = calculate_api_gravity(specific_gravity)
            return {
                "success": True,
                "source": "verified_engineering_tool",
                **result,
            }
        except (ValueError, TypeError) as exc:
            return {"success": False, "error": str(exc)}

   
    # 5. General engineering questions use recent conversation history.
    try:
        context = get_knowledge_context(question)

        # Include only valid, recent messages.
        recent_messages = []

        if isinstance(conversation_history, list):
            for message in conversation_history[-8:]:
                if not isinstance(message, dict):
                    continue

                role = message.get("role")
                content = message.get("content")

                if role not in ("user", "assistant"):
                    continue

                if isinstance(content, str) and content.strip():
                    recent_messages.append(
                        f"{role.upper()}: {content.strip()[:2000]}"
                    )

        history_text = "\n".join(recent_messages)

        prompt_parts = [
            "You are Engineering AI, an intelligent assistant covering "
            "petroleum, mechanical, electrical, civil, and other "
            "engineering fields.",
            "Use recent conversation history to understand follow-up "
            "questions and references to earlier topics.",
            "Do not treat previous assistant answers as verified facts "
            "without checking them.",
            "Do not invent engineering facts, sources, or measurements.",
            "Show units and explain assumptions when relevant.",
        ]

        if context:
            prompt_parts.append(
                "Relevant engineering reference material:\n" + context
            )

        if history_text:
            prompt_parts.append(
                "RECENT CONVERSATION:\n" + history_text
            )

        prompt_parts.append("CURRENT USER QUESTION:\n" + question)

        prompt = "\n\n".join(prompt_parts)
        response = ask_ai(prompt)

        return {
            "success": True,
            "answer": response,
            "source": "ai_provider_with_knowledge"
            if context else "ai_provider",
            "knowledge_retrieved": bool(context),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": f"AI request failed: {type(exc).__name__}: {exc}",
        }



def stream_answer_question(
    question: str,
    conversation_history: list[dict] | None = None,
):
    """Stream a general engineering answer from the configured AI provider."""

    question = question.strip()

    if not question:
        raise ValueError("Please enter a question.")

    context = get_knowledge_context(question)

    recent_messages = []

    if isinstance(conversation_history, list):
        for message in conversation_history[-8:]:
            if not isinstance(message, dict):
                continue

            role = message.get("role")
            content = message.get("content")

            if role not in ("user", "assistant"):
                continue

            if isinstance(content, str) and content.strip():
                recent_messages.append(
                    f"{role.upper()}: {content.strip()[:2000]}"
                )

    history_text = "\n".join(recent_messages)

    prompt_parts = [
        "You are Engineering AI, an intelligent assistant covering "
        "petroleum, mechanical, electrical, civil, and other "
        "engineering fields.",
        "Use recent conversation history to understand follow-up "
        "questions and references to earlier topics.",
        "Do not treat previous assistant answers as verified facts "
        "without checking them.",
        "Do not invent engineering facts, sources, or measurements.",
        "Show units and explain assumptions when relevant.",
    ]

    if context:
        prompt_parts.append(
            "Relevant engineering reference material:\n" + context
        )

    if history_text:
        prompt_parts.append(
            "RECENT CONVERSATION:\n" + history_text
        )

    prompt_parts.append("CURRENT USER QUESTION:\n" + question)

    prompt = "\n\n".join(prompt_parts)

    yield from stream_ai(prompt)


import re

AI_MODES = {
    "general_engineering": {
        "name": "General Engineering",
        "instruction": (
            "Focus on mechanical, electrical, civil, chemical, and "
            "related engineering fields. Explain principles, methods, "
            "units, assumptions, and calculations clearly."
        ),
    },
    "petroleum_engineering": {
        "name": "Petroleum Engineering",
        "instruction": (
            "Focus on petroleum and gas engineering, drilling, well "
            "hydraulics, mud weight, hydrostatic pressure, reservoir "
            "engineering, and production. State assumptions and units. "
            "Distinguish preliminary calculations from field-ready "
            "decisions."
        ),
    },
    "coding": {
        "name": "Coding",
        "instruction": (
            "Focus on programming, debugging, software design, and "
            "code explanations. Give practical examples, explain errors, "
            "and preserve existing working code when suggesting changes."
        ),
    },
    "research": {
        "name": "Research",
        "instruction": (
            "Use a structured research approach. Separate established "
            "facts from assumptions and uncertainty. Never invent "
            "citations, sources, or research findings. State when "
            "current information or external sources are needed."
        ),
    },
}


def normalize_ai_mode(mode: str = "general_engineering") -> str:
    """Validate and return a supported AI mode."""
    if not isinstance(mode, str) or mode not in AI_MODES:
        raise ValueError(
            "Unsupported AI mode. Choose general_engineering, "
            "petroleum_engineering, coding, or research."
        )
    return mode


try:
    from knowledge_base.engineering_reference import search_references
    from .provider import ask_ai, search_ai, stream_ai
    from .tools import (
        calculate_api_gravity,
        calculate_formation_pressure,
        calculate_hydrostatic_pressure,
        calculate_required_mud_weight,
    )
except ImportError:  # pragma: no cover
    from knowledge_base.engineering_reference import search_references
    from .provider import ask_ai, search_ai, stream_ai
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


def get_knowledge_context(question: str) -> str:
    """Retrieve relevant engineering references for a question."""
    references = search_references(question)

    if not references:
        return ""

    if isinstance(references, str):
        if references.startswith((
            "No matching engineering reference",
            "Could not read engineering references",
            "Engineering reference file was not found",
        )):
            return ""
        return references

    sections = []

    for reference in references[:3]:
        if isinstance(reference, dict):
            title = reference.get("title", "Engineering reference")
            content = reference.get(
                "content",
                reference.get("explanation", ""),
            )
            sections.append(f"Topic: {title}\nContent: {content}")
        else:
            sections.append(str(reference))

    return "\n\n".join(sections)


def _build_prompt(
    question: str,
    conversation_history: list[dict] | None,
    mode: str,
    context: str,
) -> str:
    """Build a prompt using the selected mode and recent context."""
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
        (
            "You are Engineering AI, an intelligent assistant covering "
            "petroleum, mechanical, electrical, civil, and other "
            "engineering fields."
        ),
        (
            f"Selected AI mode: {AI_MODES[mode]['name']}.\n"
            f"{AI_MODES[mode]['instruction']}"
        ),
        (
            "Use recent conversation history to understand follow-up "
            "questions and references to earlier topics."
        ),
        (
            "Do not treat previous assistant answers as verified facts "
            "without checking them."
        ),
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

    return "\n\n".join(prompt_parts)


def answer_question(
    question: str,
    conversation_history: list[dict] | None = None,
    mode: str = "general_engineering",
) -> dict:
    """Answer engineering questions or run supported calculations."""
    if not isinstance(question, str):
        return {
            "success": False,
            "error": "Question must be text.",
        }

    question = question.strip()

    if not question:
        return {
            "success": False,
            "error": "Please enter a question.",
        }

    try:
        mode = normalize_ai_mode(mode)
    except ValueError as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    text = question.lower().replace(",", "")

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
                    r"(?:mud weight|mud wt|mw)\s*"
                    r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)\s*(?:ppg)?",
                    r"(\d+(?:\.\d+)?)\s*ppg",
                ],
                text,
            )

            tvd = extract_number(
                [
                    r"(?:tvd|true vertical depth|depth)\s*"
                    r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)",
                    r"(\d+(?:\.\d+)?)\s*(?:ft|feet)\s*"
                    r"(?:tvd|depth)?",
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
                result = calculate_hydrostatic_pressure(
                    mud_weight, tvd
                )
                return {
                    "success": True,
                    "source": "verified_engineering_tool",
                    **result,
                }
            except (ValueError, TypeError) as exc:
                return {
                    "success": False,
                    "error": str(exc),
                }

    # 2. Formation pressure
    if "formation pressure" in text:
        gradient = extract_number(
            [
                r"(?:gradient|pressure gradient)\s*"
                r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
            ],
            text,
        )

        tvd = extract_number(
            [
                r"(?:tvd|true vertical depth|depth)\s*"
                r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
            ],
            text,
        )

        if gradient is None or tvd is None:
            return {
                "success": False,
                "needs_input": True,
                "message": (
                    "Provide the formation pressure gradient in psi/ft "
                    "and TVD in feet."
                ),
            }

        try:
            result = calculate_formation_pressure(gradient, tvd)
            return {
                "success": True,
                "source": "verified_engineering_tool",
                **result,
            }
        except (ValueError, TypeError) as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # 3. Required mud weight
    if "required mud weight" in text or "mud weight required" in text:
        pressure = extract_number(
            [
                r"(?:pressure|formation pressure)\s*"
                r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
            ],
            text,
        )

        tvd = extract_number(
            [
                r"(?:tvd|true vertical depth|depth)\s*"
                r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
            ],
            text,
        )

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
            return {
                "success": False,
                "error": str(exc),
            }

    # 4. API gravity
    if "api gravity" in text:
        specific_gravity = extract_number(
            [
                r"(?:specific gravity|sg)\s*"
                r"(?:of|is|=|:)?\s*(\d+(?:\.\d+)?)"
            ],
            text,
        )

        if specific_gravity is None:
            return {
                "success": False,
                "needs_input": True,
                "message": (
                    "Provide the oil's specific gravity, for example: "
                    "API gravity for specific gravity 0.85."
                ),
            }

        try:
            result = calculate_api_gravity(specific_gravity)
            return {
                "success": True,
                "source": "verified_engineering_tool",
                **result,
            }
        except (ValueError, TypeError) as exc:
            return {
                "success": False,
                "error": str(exc),
            }

    # 5. General AI response
    try:
        context = get_knowledge_context(question)
        prompt = _build_prompt(
            question,
            conversation_history,
            mode,
            context,
        )
        if mode == "research":
            response = search_ai(prompt)
            response_source = "groq_browser_search"
        else:
            response = ask_ai(prompt)
            response_source = (
                "ai_provider_with_knowledge"
                if context
                else "ai_provider"
            )

        return {
            "success": True,
            "answer": response,
            "source": response_source,
            "knowledge_retrieved": bool(context),
        }

    except Exception as exc:
        return {
            "success": False,
            "error": (
                f"AI request failed: {type(exc).__name__}: {exc}"
            ),
        }


def stream_answer_question(
    question: str,
    conversation_history: list[dict] | None = None,
    mode: str = "general_engineering",
):
    """Stream an answer using the selected AI mode."""
    if not isinstance(question, str):
        raise ValueError("Question must be text.")

    question = question.strip()

    if not question:
        raise ValueError("Please enter a question.")

    mode = normalize_ai_mode(mode)
    context = get_knowledge_context(question)

    prompt = _build_prompt(
        question,
        conversation_history,
        mode,
        context,
    )

    yield from stream_ai(prompt)

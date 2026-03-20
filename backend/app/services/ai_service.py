import json
import re
from typing import Any, Dict

from openai import OpenAI

from app.core.config import settings


def _extract_json(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("Could not parse evaluation JSON")


def _fallback_ideal_answer(question: str, category: str) -> str:
    return (
        f"Example ideal answer for this {category} question ('{question}'):\n"
        "First, briefly set context and your objective. "
        "Then explain the concrete actions you took and why. "
        "Include measurable outcomes (metrics, timelines, impact) and key learnings. "
        "End with how this experience would help you succeed in this role."
    )


def generate_question(role: str, category: str) -> str:
    prompt = (
        "You are an expert interviewer.\n"
        f"Generate 1 realistic interview question for the role: {role}.\n"
        f"Category: {category}\n"
        "Avoid coding questions."
    )

    if not settings.OPENAI_API_KEY:
        return f"[{category}] Tell me about a real-world challenge you handled as a {role}, and how you approached it."

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        input=prompt,
        temperature=0.7,
    )
    return response.output_text.strip()


def evaluate_answer(question: str, answer: str, category: str) -> Dict[str, Any]:
    prompt = (
        "You are an expert interviewer.\n\n"
        f"Question: {question}\n"
        f"Candidate Answer: {answer}\n\n"
        "Evaluate based on:\n"
        "- Relevance (0-10)\n"
        "- Clarity (0-10)\n"
        "- Depth\n"
        "- Communication quality\n\n"
        "Also provide:\n"
        "- Strengths\n"
        "- Weaknesses\n"
        "- Missing points\n"
        "- Ideal improved answer example specific to the exact question\n\n"
        "Return response in JSON format with keys: "
        "score, strengths, weaknesses, missing_points, ideal_answer, category."
    )

    if not settings.OPENAI_API_KEY:
        return {
            "score": 6.5,
            "strengths": ["Clear structure", "Relevant example"],
            "weaknesses": ["Limited depth", "Could quantify impact better"],
            "missing_points": ["Specific metrics", "Trade-off discussion"],
            "ideal_answer": _fallback_ideal_answer(question, category),
            "category": category,
        }

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        input=prompt,
        temperature=0.3,
    )

    parsed = _extract_json(response.output_text)
    parsed.setdefault("category", category)
    parsed.setdefault("score", 0)
    parsed.setdefault("strengths", [])
    parsed.setdefault("weaknesses", [])
    parsed.setdefault("missing_points", [])
    ideal_answer = str(parsed.get("ideal_answer", "")).strip()
    parsed["ideal_answer"] = ideal_answer if ideal_answer else _fallback_ideal_answer(question, category)
    return parsed

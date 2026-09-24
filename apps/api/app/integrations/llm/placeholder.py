import json
from typing import Any


class PlaceholderLLMClient:
    """Deterministic templated text built only from the evidence passed in.

    # PLACEHOLDER(llm): replaced by the real LLM provider once credentials are
    # available. It NEVER invents facts: output is derived strictly from the
    # ``messages`` content supplied by the caller.
    """

    source = "placeholder"

    def generate(
        self,
        messages: list[dict[str, str]],
        response_schema: Any = None,
        temperature: float = 0.0,
    ) -> str:
        evidence_ids = _collect_evidence_ids(messages)
        n = len(evidence_ids)
        if n == 0:
            return (
                "Based on the available evidence, there are no cited evidence IDs "
                "yet. No conclusion is drawn. Review the investigation output."
            )

        citations = ", ".join(evidence_ids)
        if response_schema is not None and _wants_json(response_schema):
            return json.dumps(
                {
                    "findings": [
                        f"Findings based on {n} cited evidence item(s): {citations}."
                    ],
                    "evidence_ids": evidence_ids,
                    "explanation": (
                        f"Explanation grounded only in evidence IDs: {citations}."
                    ),
                }
            )

        return (
            f"Findings based on {n} cited evidence item(s): {citations}. "
            f"Explanation grounded only in evidence IDs: {citations}."
        )


def _collect_evidence_ids(messages: list[dict[str, str]]) -> list[str]:
    """Extract EV- style evidence IDs from message content (no invention)."""
    found: list[str] = []
    for msg in messages:
        content = msg.get("content", "") or ""
        tokens = content.replace(",", " ").split()
        for token in tokens:
            # tolerate trailing punctuation and evidence id prefixes
            cleaned = token.strip(".,:;()[]{}\"'")
            if cleaned.upper().startswith("EV-") and cleaned not in found:
                found.append(cleaned)
    return found


def _wants_json(schema: Any) -> bool:
    if isinstance(schema, dict):
        return True
    if isinstance(schema, str):
        return "json" in schema.lower()
    if isinstance(schema, type):
        return issubclass(schema, dict)
    # any schema object with a model_dump implies structured output -> JSON
    return hasattr(schema, "model_json_schema")


def as_json(schema_hint: dict[str, Any], **payload: Any) -> str:
    return json.dumps(payload)
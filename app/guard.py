from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from guardrails import Guard


@dataclass
class GuardResult:
    blocked: bool
    content: str
    reason: Optional[str] = None


class GuardService:
    def __init__(self, rail_path: str):
        # Load Guard from RAIL spec. The RAIL defines input and output validators.
        self._guard = Guard.from_rail(rail_path)

    async def check_input(self, prompt: str) -> GuardResult:
        # Quick heuristic input guard while native input validation is disabled.
        lowered = (prompt or "").lower()
        blocked_terms = [
            "kill",
            "murder",
            "weapon",
            "bomb",
            "explosive",
            "harm someone",
            "how to harm",
            "how do i kill",
            "make a weapon",
            "attack",
        ]
        if any(term in lowered for term in blocked_terms):
            return GuardResult(
                blocked=True,
                content="",
                reason="Unsafe intent detected in prompt (violence/illegal).",
            )

        return GuardResult(blocked=False, content=prompt)

    async def check_output(self, prompt: str, output: str) -> GuardResult:
        # Prefer validate_output if available, else fall back to passthrough.
        try:
            if hasattr(self._guard, "validate_output"):
                result = self._guard.validate_output(
                    prompt_params={"prompt": prompt},
                    output=output,
                )
                if getattr(result, "validation_passed", True) is False:
                    reason = getattr(result, "error", None) or "Unsafe output detected"
                    return GuardResult(blocked=True, content="", reason=reason)
                content = getattr(result, "validated_output", None) or output
                return GuardResult(blocked=False, content=content)
        except Exception as ex:
            # If guard validation fails unexpectedly, allow the raw output to avoid 500s.
            return GuardResult(blocked=False, content=output)

        # Fallback: no validation available in this version; return as-is.
        return GuardResult(blocked=False, content=output)



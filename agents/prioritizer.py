"""Feature prioritization agent using MoSCoW and strict MVP constraints."""

from __future__ import annotations

from typing import Any, Dict

from utils.llm_client import LLMClient


class PrioritizerAgent:
    """Builds MoSCoW priorities and enforces MVP scope discipline."""

    SYSTEM_PROMPT = (
        "You are a strict product owner. Reject feature creep and overbuilding. "
        "Output valid JSON only."
    )

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(self, startup_idea: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = f"""
Startup idea:
{startup_idea}

Analysis JSON:
{analysis}

Create a prioritized feature set using MoSCoW.
Return JSON with keys:
- moscow: {{"must_have": [str], "should_have": [str], "could_have": [str], "wont_have_now": [str]}}
- mvp_scope: {{"strict_goal": str, "included_features": [str], "excluded_to_prevent_creep": [str], "release_criteria": [str]}}
- rationale: {{"priority_logic": [str], "tradeoffs": [str]}}

Rules:
1) Must-have items should be minimal and enough to prove value quickly.
2) Excluded list should be explicit and opinionated.
3) Keep total included MVP features between 3 and 6.
"""
        return self.llm_client.complete_json(self.SYSTEM_PROMPT, user_prompt)

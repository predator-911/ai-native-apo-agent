"""Idea analysis agent."""

from __future__ import annotations

from typing import Any, Dict

from utils.llm_client import LLMClient


class AnalyzerAgent:
    """Extracts problem definition, user persona, and market opportunity."""

    SYSTEM_PROMPT = (
        "You are a startup product strategist. Return strict JSON only. "
        "Be concise but specific and practical."
    )

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(self, startup_idea: str) -> Dict[str, Any]:
        user_prompt = f"""
Analyze this startup idea:
{startup_idea}

Return JSON with keys:
- problem_definition: {{"pain_point": str, "why_now": str, "current_alternatives": [str]}}
- target_user: {{"primary_persona": str, "jobs_to_be_done": [str], "adoption_barriers": [str]}}
- market_opportunity: {{"market_size_signal": str, "demand_indicators": [str], "wedge_strategy": str}}
"""
        return self.llm_client.complete_json(self.SYSTEM_PROMPT, user_prompt)

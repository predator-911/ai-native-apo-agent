"""Roadmap and execution planning agent."""

from __future__ import annotations

from typing import Any, Dict

from utils.llm_client import LLMClient


class RoadmapAgent:
    """Converts MVP scope into implementation tasks and a 7-day plan."""

    SYSTEM_PROMPT = (
        "You are a pragmatic engineering manager and technical architect. "
        "Return strict JSON. Favor delivery speed with production-quality basics."
    )

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def run(self, startup_idea: str, analysis: Dict[str, Any], prioritization: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = f"""
Startup idea:
{startup_idea}

Analysis JSON:
{analysis}

Prioritization JSON:
{prioritization}

Return JSON with keys:
- technical_architecture: {{"stack": [str], "core_components": [str], "data_model_notes": [str], "security_basics": [str]}}
- cursor_ready_tasks: [{{"id": str, "title": str, "description": str, "depends_on": [str], "acceptance_criteria": [str]}}]
- execution_plan_7_days: [{{"day": int, "focus": str, "deliverables": [str], "dependencies": [str]}}]
- kpis: [{{"name": str, "target": str, "measurement": str}}]
- risks: [{{"risk": str, "impact": str, "mitigation": str}}]

Rules:
1) Task IDs should be sequential like TASK-1, TASK-2.
2) Include realistic dependencies.
3) Keep plan to exactly 7 days.
"""
        return self.llm_client.complete_json(self.SYSTEM_PROMPT, user_prompt)

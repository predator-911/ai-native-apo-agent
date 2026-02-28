"""Evaluation agent and deterministic scoring utility."""

from __future__ import annotations

from typing import Any, Dict


class EvaluatorAgent:
    """Scores the APO output with a transparent weighted formula."""

    def run(self, analysis: Dict[str, Any], prioritization: Dict[str, Any], roadmap: Dict[str, Any]) -> Dict[str, Any]:
        clarity = self._score_clarity(analysis)
        priority_strength = self._score_priority_strength(prioritization)
        mvp_strictness = self._score_mvp_strictness(prioritization)
        execution_feasibility = self._score_execution_feasibility(roadmap)

        total_score = (
            (clarity * 200)
            + (priority_strength * 300)
            + (mvp_strictness * 300)
            + (execution_feasibility * 200)
        )

        return {
            "subscores": {
                "clarity": clarity,
                "priority_strength": priority_strength,
                "mvp_strictness": mvp_strictness,
                "execution_feasibility": execution_feasibility,
            },
            "score_formula": (
                "(Clarity × 200) + (Priority Strength × 300) + "
                "(MVP Strictness × 300) + (Execution Feasibility × 200)"
            ),
            "total_score_1_to_10000": int(total_score),
            "scoring_explanation": [
                "Each subscore is normalized on a 1-10 scale from structural quality signals.",
                "Priority and MVP strictness carry the highest weights to discourage feature creep.",
                "Execution feasibility rewards realistic dependencies, sequencing, and measurable outcomes.",
            ],
        }

    @staticmethod
    def _score_clarity(analysis: Dict[str, Any]) -> int:
        has_problem = bool(analysis.get("problem_definition", {}).get("pain_point"))
        has_persona = bool(analysis.get("target_user", {}).get("primary_persona"))
        indicators = analysis.get("market_opportunity", {}).get("demand_indicators", [])
        raw = 4 + (2 if has_problem else 0) + (2 if has_persona else 0) + min(len(indicators), 2)
        return max(1, min(10, raw))

    @staticmethod
    def _score_priority_strength(prioritization: Dict[str, Any]) -> int:
        moscow = prioritization.get("moscow", {})
        must_have = moscow.get("must_have", [])
        should_have = moscow.get("should_have", [])
        wont = moscow.get("wont_have_now", [])
        raw = 3 + min(len(must_have), 4) + min(len(should_have), 2) + min(len(wont), 1)
        return max(1, min(10, raw))

    @staticmethod
    def _score_mvp_strictness(prioritization: Dict[str, Any]) -> int:
        mvp_scope = prioritization.get("mvp_scope", {})
        included = mvp_scope.get("included_features", [])
        excluded = mvp_scope.get("excluded_to_prevent_creep", [])
        release_criteria = mvp_scope.get("release_criteria", [])

        in_range = 3 <= len(included) <= 6
        raw = 4 + (3 if in_range else 0) + min(len(excluded), 2) + min(len(release_criteria), 1)
        return max(1, min(10, raw))

    @staticmethod
    def _score_execution_feasibility(roadmap: Dict[str, Any]) -> int:
        tasks = roadmap.get("cursor_ready_tasks", [])
        plan = roadmap.get("execution_plan_7_days", [])
        kpis = roadmap.get("kpis", [])
        risks = roadmap.get("risks", [])

        has_dependencies = any(task.get("depends_on") for task in tasks if isinstance(task, dict))
        raw = 3 + (3 if len(plan) == 7 else 0) + min(len(tasks), 2) + min(len(kpis), 1) + min(len(risks), 1)
        if has_dependencies:
            raw += 1
        return max(1, min(10, raw))

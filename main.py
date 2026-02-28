"""CLI entry point for ai-priority-architect."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from agents.analyzer import AnalyzerAgent
from agents.evaluator import EvaluatorAgent
from agents.prioritizer import PrioritizerAgent
from agents.roadmap import RoadmapAgent
from utils.llm_client import LLMClient, LLMClientError


DEFAULT_DEMO_IDEA = "Build an AI crypto portfolio tracking app for retail investors."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-priority-architect",
        description="Convert a raw startup idea into an actionable APO plan.",
    )
    parser.add_argument(
        "idea",
        nargs="?",
        help="Raw startup idea text. If omitted, use --idea-file.",
    )
    parser.add_argument(
        "--idea-file",
        type=str,
        help="Path to a text file containing the startup idea.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output.",
    )
    return parser


def load_idea(args: argparse.Namespace) -> str:
    if args.idea:
        return args.idea.strip()
    if args.idea_file:
        with open(args.idea_file, "r", encoding="utf-8") as file:
            return file.read().strip()
    print("No idea provided. Using default demo idea.")
    return DEFAULT_DEMO_IDEA


def run_pipeline(startup_idea: str) -> Dict[str, Any]:
    llm_client = LLMClient()

    analyzer = AnalyzerAgent(llm_client)
    prioritizer = PrioritizerAgent(llm_client)
    roadmap = RoadmapAgent(llm_client)
    evaluator = EvaluatorAgent()

    analysis = analyzer.run(startup_idea)
    prioritization = prioritizer.run(startup_idea, analysis)
    execution = roadmap.run(startup_idea, analysis, prioritization)
    evaluation = evaluator.run(analysis, prioritization, execution)

    return {
        "startup_idea": startup_idea,
        "analysis": analysis,
        "prioritization": prioritization,
        "roadmap": execution,
        "evaluation": evaluation,
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        startup_idea = load_idea(args)
        result = run_pipeline(startup_idea)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except LLMClientError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # broad fallback for CLI robustness
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

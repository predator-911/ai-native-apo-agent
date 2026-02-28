# ai-priority-architect

`ai-priority-architect` is a minimal, production-quality Python CLI for AI-Native Product Owner (APO) planning.

Given a raw startup idea, it generates:
1. Problem definition
2. Target user definition
3. Priority-ranked feature list (MoSCoW)
4. Strict MVP scope
5. Technical architecture suggestion
6. Cursor-ready task breakdown
7. 7-day execution roadmap
8. KPI definition
9. Risk analysis

---

## 1) Problem Definition
Early-stage teams often jump from idea to implementation without forcing strategic clarity.
This tool addresses that by turning an unstructured concept into explicit statements about:
- the core pain point,
- who experiences it,
- why existing alternatives are insufficient,
- and what wedge can unlock adoption.

---

## 2) Why Priority Definition is Critical in the AI Era
AI products can be built quickly, but speed amplifies waste if priorities are weak.
Poor prioritization causes feature creep, delayed launches, and unclear value delivery.
`ai-priority-architect` enforces MoSCoW prioritization plus strict MVP constraints so teams can validate outcomes in days, not months.

---

## 3) Architecture Overview
Pipeline flow:
1. **Analyzer Agent** (`agents/analyzer.py`) extracts problem, persona, market signal.
2. **Prioritizer Agent** (`agents/prioritizer.py`) applies MoSCoW and hard MVP boundaries.
3. **Roadmap Agent** (`agents/roadmap.py`) generates technical architecture, Cursor-ready tasks, dependencies, and 7-day plan.
4. **Evaluator Agent** (`agents/evaluator.py`) computes weighted quality score (1–10,000).
5. **LLM Client** (`utils/llm_client.py`) centralizes provider API calls and error handling.

All outputs are emitted as structured JSON.

---

## 4) Setup Instructions
### Prerequisites
- Python 3.10+
- OpenAI or Anthropic API key

### Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure Environment
```bash
cp .env.example .env
```
Set the values in `.env`, then load it (example):
```bash
export $(grep -v '^#' .env | xargs)
```

### Run
```bash
python main.py "AI copilot for independent fitness coaches to auto-generate weekly plans and client check-ins" --pretty
```

Or from file:
```bash
python main.py --idea-file idea.txt --pretty
```

---

## 5) Cursor Configuration Explanation
The repository includes `.cursorrules` to align implementation behavior with APO discipline:
- modular architecture first,
- strict MVP scope,
- active removal of feature creep,
- structured outputs,
- zero secret leakage.

These rules keep generated plans implementation-ready for Cursor workflows.

---

## 6) Performance Metric Formula
The evaluator computes a deterministic total score:

```text
Score =
(Clarity × 200) +
(Priority Strength × 300) +
(MVP Strictness × 300) +
(Execution Feasibility × 200)
```

- Each subscore is normalized to 1–10.
- Total range is 1,000 to 10,000.
- Priority and MVP strictness are weighted most heavily to avoid overbuilding.

---

## 7) Benchmark Comparison Template
Use:
- `benchmarks/test_case_1.md` for a baseline scenario.
- `benchmarks/comparison.md` for side-by-side run scoring.

Recommended process:
1. Run the same idea with multiple models/providers.
2. Store each JSON output.
3. Record subscores and total score in the comparison table.
4. Review tradeoffs before selecting a default model.

---

## 8) Security Notes
- API keys are read strictly from environment variables.
- No secrets are hardcoded in source.
- `.env` is gitignored.
- LLM request failures surface clear, actionable errors.
- Keep production keys in a secure secret manager for CI/CD.

---

## 9) Future Improvements
- Add retry and backoff policies with jitter.
- Add JSON schema validation for stricter output guarantees.
- Add optional offline scoring mode for benchmark replay.
- Add unit tests and contract tests per agent prompt.
- Add model routing policy (cost/quality aware).

---

## Project Structure

```text
ai-priority-architect/
├── main.py
├── agents/
│   ├── analyzer.py
│   ├── prioritizer.py
│   ├── roadmap.py
│   └── evaluator.py
├── benchmarks/
│   ├── test_case_1.md
│   └── comparison.md
├── utils/
│   └── llm_client.py
├── .cursorrules
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

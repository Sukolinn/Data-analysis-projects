"""Compare the 8 generated hypotheses against the expert hypotheses.

Runs the real-case pipeline, then reports how many generated hypotheses overlap
in meaning with the expert brainstorm hypotheses (parsed from the .docx files),
using the transparent concept-overlap heuristic in
``hypothesis_factory.analysis.expert_match``.

Usage (from the project root, with the venv active):

    PYTHONPATH=src python scripts/compare_hypotheses.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# allow running as `python scripts/compare_hypotheses.py` without PYTHONPATH
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hypothesis_factory.analysis.expert_match import compare, summarize  # noqa: E402
from hypothesis_factory.config import DEFAULT_CONSTRAINTS, DEFAULT_KPI  # noqa: E402
from hypothesis_factory.data_loaders.real_case_loader import load_real_case_data  # noqa: E402
from hypothesis_factory.pipeline import run_pipeline  # noqa: E402


def _fmt(tags: set[str]) -> str:
    return ", ".join(sorted(tags)) if tags else "—"


def main() -> int:
    data = load_real_case_data()
    experts = data.expert_hypotheses
    result = run_pipeline(DEFAULT_KPI, DEFAULT_CONSTRAINTS)
    generated = result.hypotheses

    if not experts:
        print(
            "WARNING: 0 expert hypotheses parsed. Install python-docx and check "
            "that the expert .docx files are readable (they live in tables)."
        )

    rows = compare(generated, experts)
    stats = summarize(rows)

    print(f"Generated hypotheses: {len(generated)}")
    print(f"Expert hypotheses:    {len(experts)}")
    print("=" * 88)
    for r in rows:
        strict = "MATCH" if r.strict_match else "  -  "
        print(f"{r.hyp_id} [{r.factory}]  strict={strict}")
        print(f"    concrete concepts: {_fmt(r.hyp_concrete)}")
        if r.best_expert_text:
            print(f"    closest expert [{r.best_expert_factory}]: {r.best_expert_text}")
            print(f"    shared concrete: {_fmt(r.shared_concrete)} | shared thematic: {_fmt(r.shared_thematic)}")
        print("-" * 88)

    print(
        f"\nRESULT: {stats['strict_matched']} of {stats['total']} generated hypotheses "
        f"match an expert hypothesis on a concrete technological measure (strict)."
    )
    print(
        f"        {stats['thematic_matched']} of {stats['total']} overlap thematically "
        f"(incl. the generic 'attribute loss to a scheme node' theme)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

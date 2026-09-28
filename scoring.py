"""
Assessment scoring for SME Check (v0.5).

Coverage is computed per CSF 2.0 Subcategory using any-tick semantics: a
Subcategory counts as covered ("partially addressed") if at least one question
mapped to it is ticked. Coverage is weighted by `combined_score` from the
csf-sme-coverage pipeline (Verizon DBIR threat weight x Irish adoption gap).

This module has no Streamlit dependency so it can be unit-tested directly.
"""

from pathlib import Path

import pandas as pd

PRIORITY_FILE = Path(__file__).parent / "data" / "combined_priority.csv"
TOP_N_GAPS = 10
UNWEIGHTED_NOTE = "No combined score in source data"
# Threat weight (weighted_coverage) at or above which a zero-score gap is
# flagged as high priority. Weights in the CSV snapshot range 0-2.68.
HIGH_THREAT_WEIGHT = 1.0


def load_priority(path: Path = PRIORITY_FILE) -> pd.DataFrame:
    """Load `combined_score` and `weighted_coverage` indexed by Subcategory ID.

    `weighted_coverage` is the Verizon DBIR threat weight; it is used to break
    ties in the gap list and to caption zero-score gaps.
    """
    df = pd.read_csv(
        path, usecols=["subcategory", "combined_score", "weighted_coverage"]
    )
    return df.set_index("subcategory")


def group_by_subcategory(questions: dict) -> dict[str, list[dict]]:
    """Group question items by their CSF Subcategory, preserving YAML order."""
    grouped: dict[str, list[dict]] = {}
    for item in questions["items"]:
        grouped.setdefault(item["csf_subcategory"], []).append(item)
    return grouped


def gap_note(combined_score: float, threat_weight: float) -> str:
    """Caption for a gap row.

    A combined_score of 0 with a threat weight means the source survey has no
    Irish adoption-gap figure, so the product is 0 despite real threat data.
    """
    if combined_score > 0:
        return ""
    if threat_weight >= HIGH_THREAT_WEIGHT:
        return (
            f"High global threat weight ({threat_weight:.2f}) — no Irish gap "
            "data in source survey. Treat as high priority."
        )
    if threat_weight > 0:
        return (
            f"Global threat weight {threat_weight:.2f} — no Irish gap data "
            "in source survey."
        )
    return UNWEIGHTED_NOTE


def score_assessment(
    answers: dict[str, bool],
    questions: dict,
    priority: pd.DataFrame,
    top_n: int = TOP_N_GAPS,
) -> dict:
    """Score an assessment with any-tick semantics per CSF Subcategory.

    Returns a dict with:
      weighted_pct  covered combined_score / total combined_score x 100
      coverage_pct  covered Subcategories / assessed Subcategories x 100
      have, total   covered and assessed Subcategory counts
      gaps          DataFrame of up to `top_n` uncovered Subcategories,
                    sorted by combined_score desc, then weighted_coverage
                    (threat weight) desc, then Subcategory ID; zero-score gaps
                    carry a Note from `gap_note`, since 0 means missing threat
                    weight or Irish gap data rather than low importance

    Raises ValueError if a question maps to a Subcategory missing from
    `priority`.
    """
    grouped = group_by_subcategory(questions)
    unknown = sorted(set(grouped) - set(priority.index))
    if unknown:
        raise ValueError(f"Subcategories missing from priority data: {unknown}")

    covered = {
        sub
        for sub, items in grouped.items()
        if any(answers.get(item["id"], False) for item in items)
    }
    assessed = priority.reindex(list(grouped)).astype(float)
    weights = assessed["combined_score"]

    total = len(grouped)
    have = len(covered)
    total_weight = weights.sum()
    covered_weight = weights[weights.index.isin(covered)].sum()

    gaps = pd.DataFrame(
        [
            {
                "CSF Subcategory": sub,
                "Priority score": round(weights[sub], 2),
                "Questions": "; ".join(item["text"] for item in items),
                "Note": gap_note(weights[sub], assessed.at[sub, "weighted_coverage"]),
                "_combined": weights[sub],
                "_threat": assessed.at[sub, "weighted_coverage"],
            }
            for sub, items in grouped.items()
            if sub not in covered
        ],
        columns=[
            "CSF Subcategory",
            "Priority score",
            "Questions",
            "Note",
            "_combined",
            "_threat",
        ],
    )
    # Sort on unrounded values so rounding can't create false ties.
    gaps = (
        gaps.sort_values(
            ["_combined", "_threat", "CSF Subcategory"],
            ascending=[False, False, True],
        )
        .drop(columns=["_combined", "_threat"])
        .head(top_n)
        .reset_index(drop=True)
    )

    return {
        "weighted_pct": covered_weight / total_weight * 100 if total_weight else 0.0,
        "coverage_pct": have / total * 100 if total else 0.0,
        "have": have,
        "total": total,
        "gaps": gaps,
    }

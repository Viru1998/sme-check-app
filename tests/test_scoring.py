"""Tests for scoring.py: any-tick semantics, weighting and gap list."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from scoring import UNWEIGHTED_NOTE, gap_note, load_priority, score_assessment

QUESTIONS_FILE = Path(__file__).parent.parent / "data" / "questions.yml"


@pytest.fixture
def questions() -> dict:
    """Small question set: 3 questions on AA-05, 1 each on IR-01 and AT-01."""
    return {
        "items": [
            {"id": "mfa_email", "text": "MFA on email", "csf_subcategory": "PR.AA-05"},
            {"id": "mfa_admin", "text": "MFA on admin", "csf_subcategory": "PR.AA-05"},
            {"id": "least_priv", "text": "Least priv", "csf_subcategory": "PR.AA-05"},
            {"id": "firewall", "text": "Firewall", "csf_subcategory": "PR.IR-01"},
            {"id": "training", "text": "Training", "csf_subcategory": "PR.AT-01"},
        ]
    }


def make_priority(rows: dict[str, tuple[float, float]]) -> pd.DataFrame:
    """Build a priority table from {subcategory: (combined_score, threat weight)}."""
    return pd.DataFrame.from_dict(
        rows, orient="index", columns=["combined_score", "weighted_coverage"]
    )


@pytest.fixture
def priority() -> pd.DataFrame:
    """Combined scores summing to 4.0, with one zero-score Subcategory."""
    return make_priority(
        {
            "PR.IR-01": (3.0, 2.0),
            "PR.AA-05": (1.0, 1.0),
            "PR.AT-01": (0.0, 0.0),
            "DE.CM-09": (9.0, 3.0),
        }
    )


def test_any_tick_marks_subcategory_covered(questions, priority):
    result = score_assessment({"mfa_email": True}, questions, priority)

    assert result["have"] == 1
    assert result["total"] == 3
    assert "PR.AA-05" not in result["gaps"]["CSF Subcategory"].tolist()


def test_nothing_ticked_scores_zero(questions, priority):
    result = score_assessment({}, questions, priority)

    assert result["weighted_pct"] == 0.0
    assert result["coverage_pct"] == 0.0
    assert result["have"] == 0
    assert len(result["gaps"]) == 3


def test_everything_ticked_scores_full(questions, priority):
    answers = {item["id"]: True for item in questions["items"]}
    result = score_assessment(answers, questions, priority)

    assert result["weighted_pct"] == pytest.approx(100.0)
    assert result["coverage_pct"] == pytest.approx(100.0)
    assert result["gaps"].empty


def test_weighted_pct_uses_only_assessed_subcategories(questions, priority):
    # DE.CM-09 (weight 9.0) has no question, so it is excluded from the total.
    result = score_assessment({"firewall": True}, questions, priority)

    assert result["weighted_pct"] == pytest.approx(3.0 / 4.0 * 100)
    assert result["coverage_pct"] == pytest.approx(1 / 3 * 100)


def test_zero_score_subcategory_counts_unweighted_only(questions, priority):
    result = score_assessment({"training": True}, questions, priority)

    assert result["weighted_pct"] == 0.0
    assert result["coverage_pct"] == pytest.approx(1 / 3 * 100)


def test_gaps_sorted_with_zero_scores_last_and_noted(questions, priority):
    gaps = score_assessment({}, questions, priority)["gaps"]

    assert gaps["CSF Subcategory"].tolist() == ["PR.IR-01", "PR.AA-05", "PR.AT-01"]
    assert gaps["Note"].tolist() == ["", "", UNWEIGHTED_NOTE]


def test_gaps_list_each_subcategory_once_with_all_question_texts(questions, priority):
    gaps = score_assessment({}, questions, priority)["gaps"]

    assert gaps["CSF Subcategory"].is_unique
    aa05 = gaps.loc[gaps["CSF Subcategory"] == "PR.AA-05", "Questions"].item()
    assert aa05 == "MFA on email; MFA on admin; Least priv"


def test_zero_score_gaps_break_ties_by_threat_weight_then_id():
    # Synthetic weights: in the real CSV snapshot PR.DS-01 (2.68) outranks
    # PR.PS-01 (2.59); this test pins the tie-break rule, not the real data.
    questions = {
        "items": [
            {"id": "a", "text": "A", "csf_subcategory": "PR.DS-01"},
            {"id": "b", "text": "B", "csf_subcategory": "PR.PS-01"},
            {"id": "c", "text": "C", "csf_subcategory": "GV.PO-01"},
            {"id": "d", "text": "D", "csf_subcategory": "RS.MA-01"},
        ]
    }
    priority = make_priority(
        {
            "PR.DS-01": (0.0, 2.0),
            "PR.PS-01": (0.0, 2.5),
            "GV.PO-01": (0.0, 0.0),
            "RS.MA-01": (0.0, 0.0),
        }
    )

    gaps = score_assessment({}, questions, priority)["gaps"]

    assert gaps["CSF Subcategory"].tolist() == [
        "PR.PS-01",  # higher threat weight wins the combined_score tie
        "PR.DS-01",
        "GV.PO-01",  # equal threat weight: alphabetical
        "RS.MA-01",
    ]


def test_combined_score_outranks_threat_weight(questions, priority):
    # A much higher threat weight must not lift PR.AA-05 above PR.IR-01,
    # which has the higher combined score.
    priority.loc["PR.AA-05", "weighted_coverage"] = 99.0

    gaps = score_assessment({}, questions, priority)["gaps"]

    assert gaps["CSF Subcategory"].tolist()[:2] == ["PR.IR-01", "PR.AA-05"]


def test_gaps_capped_at_top_n(questions, priority):
    gaps = score_assessment({}, questions, priority, top_n=2)["gaps"]

    assert gaps["CSF Subcategory"].tolist() == ["PR.IR-01", "PR.AA-05"]


def test_unknown_subcategory_raises(questions, priority):
    questions["items"].append(
        {"id": "new_q", "text": "New", "csf_subcategory": "ID.RA-01"}
    )

    with pytest.raises(ValueError, match="ID.RA-01"):
        score_assessment({}, questions, priority)


def test_real_data_every_question_subcategory_has_a_score():
    questions = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
    priority = load_priority()

    missing = {item["csf_subcategory"] for item in questions["items"]} - set(
        priority.index
    )
    assert not missing


def test_real_data_question_ids_are_unique():
    questions = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
    ids = [item["id"] for item in questions["items"]]

    assert len(ids) == len(set(ids))


HIGH_NOTE_229 = (
    "High global threat weight (2.29) — no Irish gap data in source survey. "
    "Treat as high priority."
)


@pytest.mark.parametrize(
    ("combined", "threat", "expected"),
    [
        (1.5, 2.0, ""),  # scored gap: no caption
        (0.0, 2.29, HIGH_NOTE_229),
        (0.0, 1.0, HIGH_NOTE_229.replace("2.29", "1.00")),  # threshold inclusive
        (0.0, 0.99, "Global threat weight 0.99 — no Irish gap data in source survey."),
        (0.0, 0.04, "Global threat weight 0.04 — no Irish gap data in source survey."),
        (0.0, 0.0, UNWEIGHTED_NOTE),
    ],
)
def test_gap_note(combined, threat, expected):
    assert gap_note(combined, threat) == expected


def test_real_data_zero_score_gap_captions():
    questions = yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))
    gaps = score_assessment({}, questions, load_priority(), top_n=100)["gaps"]
    notes = gaps.set_index("CSF Subcategory")["Note"]

    assert notes["PR.PS-01"].startswith("High global threat weight (2.59)")
    assert notes["GV.SC-04"] == (
        "Global threat weight 0.04 — no Irish gap data in source survey."
    )
    assert notes["RS.MA-01"] == UNWEIGHTED_NOTE
    assert notes["PR.IR-01"] == ""

"""Tests for ordering.py: sector ordering never hides questions."""

from pathlib import Path

import pytest
import yaml

from ordering import SECTOR_KEYS, VALID_SECTOR_TAGS, order_questions

QUESTIONS_FILE = Path(__file__).parent.parent / "data" / "questions.yml"


@pytest.fixture(scope="module")
def items() -> list[dict]:
    return yaml.safe_load(QUESTIONS_FILE.read_text(encoding="utf-8"))["items"]


def ids(questions: list[dict]) -> list[str]:
    return [q["id"] for q in questions]


@pytest.mark.parametrize("label", list(SECTOR_KEYS))
def test_all_36_questions_appear_for_every_sector(items, label):
    ordered = order_questions(items, SECTOR_KEYS[label])

    assert len(ordered) == 36
    assert sorted(ids(ordered)) == sorted(ids(items))


def test_healthcare_tagged_before_untagged_when_healthcare_selected(items):
    ordered = order_questions(items, SECTOR_KEYS["Healthcare"])
    positions = {q["id"]: n for n, q in enumerate(ordered)}

    healthcare = [q["id"] for q in items if "healthcare" in q.get("sectors", [])]
    untagged = [q["id"] for q in items if not q.get("sectors")]

    assert healthcare and untagged
    assert max(positions[i] for i in healthcare) < min(positions[i] for i in untagged)


def test_untagged_before_healthcare_tagged_when_ict_selected(items):
    ordered = order_questions(items, SECTOR_KEYS["ICT / Software"])
    positions = {q["id"]: n for n, q in enumerate(ordered)}

    # Healthcare-tagged questions that are not also tagged for ICT.
    healthcare_only = [
        q["id"]
        for q in items
        if "healthcare" in q.get("sectors", []) and "ict" not in q["sectors"]
    ]
    untagged = [q["id"] for q in items if not q.get("sectors")]

    assert healthcare_only and untagged
    assert max(positions[i] for i in untagged) < min(
        positions[i] for i in healthcare_only
    )


def test_ict_tagged_before_untagged_when_ict_label_selected(items):
    # Goes through the dropdown label, so it fails if "ICT / Software" stops
    # mapping to the `ict` tag used in questions.yml.
    ordered = order_questions(items, SECTOR_KEYS["ICT / Software"])
    positions = {q["id"]: n for n, q in enumerate(ordered)}

    ict = [q["id"] for q in items if "ict" in q.get("sectors", [])]
    untagged = [q["id"] for q in items if not q.get("sectors")]

    assert ict and untagged
    assert max(positions[i] for i in ict) < min(positions[i] for i in untagged)


def test_three_tiers_keep_yaml_order_within_each_tier():
    synthetic = [
        {"id": "u1"},
        {"id": "h1", "sectors": ["healthcare"]},
        {"id": "r1", "sectors": ["retail"]},
        {"id": "u2"},
        {"id": "hr", "sectors": ["retail", "healthcare"]},
        {"id": "r2", "sectors": ["retail"]},
    ]

    assert ids(order_questions(synthetic, "healthcare")) == [
        "h1",  # tier 1: tagged healthcare
        "hr",  # tier 1: tagged healthcare (and retail)
        "u1",  # tier 2: universal
        "u2",  # tier 2: universal
        "r1",  # tier 3: tagged for other sectors only
        "r2",  # tier 3: tagged for other sectors only
    ]


def test_other_sector_keeps_yaml_order(items):
    assert SECTOR_KEYS["Other"] is None
    assert ids(order_questions(items, None)) == ids(items)


def test_order_questions_does_not_mutate_input(items):
    before = ids(items)
    order_questions(items, "healthcare")

    assert ids(items) == before


def test_all_sector_tags_in_questions_yml_are_valid(items):
    used = {tag for q in items for tag in q.get("sectors", [])}

    assert used <= VALID_SECTOR_TAGS, used - VALID_SECTOR_TAGS

"""
Sector-based question ordering for SME Check.

Questions may carry an optional `sectors` list in questions.yml. Ordering is
presentation only: every question is always returned, never filtered out.

For a selected sector, questions are ordered in three tiers:
  1. tagged with the selected sector
  2. universal (no `sectors` field)
  3. tagged only with other sectors
Within each tier, the questions.yml order is preserved.

This module has no Streamlit dependency so it can be unit-tested directly.
"""

# Display label in the app's Sector dropdown -> tag used in questions.yml.
# "Other" maps to None, which leaves the questions.yml order unchanged.
SECTOR_KEYS: dict[str, str | None] = {
    "Professional services": "professional_services",
    "Retail": "retail",
    "Manufacturing": "manufacturing",
    "Healthcare": "healthcare",
    "ICT / Software": "ict",
    "Hospitality": "hospitality",
    "Construction": "construction",
    "Education": "education",
    "Other": None,
}

VALID_SECTOR_TAGS = frozenset(key for key in SECTOR_KEYS.values() if key)

MATCHING, UNIVERSAL, NON_MATCHING = 0, 1, 2


def sector_tier(item: dict, sector: str | None) -> int:
    """Return the ordering tier of a question for the selected sector tag."""
    tags = item.get("sectors")
    if not tags:
        return UNIVERSAL
    return MATCHING if sector in tags else NON_MATCHING


def order_questions(items: list[dict], sector: str | None) -> list[dict]:
    """Order questions for a sector tag without dropping any.

    With `sector` None (the "Other" option), the input order is returned.
    """
    if sector is None:
        return list(items)
    # sorted() is stable, so questions.yml order is kept within each tier.
    return sorted(items, key=lambda item: sector_tier(item, sector))

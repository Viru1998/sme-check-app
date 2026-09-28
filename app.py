"""
SME Check - NIST CSF 2.0 Self-Assessment for Irish SMEs
Streamlit MVP skeleton.

Run locally:
    streamlit run app.py

Deploy free at:
    https://streamlit.io/cloud (point at this GitHub repo)
"""
from pathlib import Path
import yaml
import streamlit as st
import pandas as pd

# ---------------------------------------------------------------
# Page config
# ---------------------------------------------------------------
st.set_page_config(
    page_title="SME Check - CSF 2.0 Self-Assessment",
    page_icon="🛡️",
    layout="centered",
)

# ---------------------------------------------------------------
# Load question set
# ---------------------------------------------------------------
QUESTIONS_FILE = Path(__file__).parent / "data" / "questions.yml"


@st.cache_data
def load_questions() -> dict:
    """Load the assessment question set from YAML."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------
# Scoring - PLACEHOLDER
# ---------------------------------------------------------------
# TODO: replace with real call into csf_sme_coverage.score
# For MVP: dummy score = (# unchecked questions) / (total) * max_weight
def compute_dummy_score(answers: dict, questions: dict) -> dict:  # PLACEHOLDER — replace in v0.5
    """Placeholder scoring that returns fake but plausible results.

    Real implementation will:
      1. Map each unchecked question -> CSF Subcategory
      2. Look up combined_priority.csv from csf_sme_coverage outputs
      3. Return the top-N gaps for this SME
    """
    total = len(questions["items"])
    have = sum(1 for q in questions["items"] if answers.get(q["id"], False))
    coverage_pct = (have / total * 100) if total else 0
    missing = [q for q in questions["items"] if not answers.get(q["id"], False)]

    # Dummy gap list - sorted by fake priority (real version uses combined_priority.csv)
    gaps = pd.DataFrame([
        {
            "CSF Subcategory": q["csf_subcategory"],
            "Question": q["text"],
            "Priority score": round(2.5 - i * 0.15, 2),  # dummy descending
        }
        for i, q in enumerate(missing[:10])
    ])
    return {
        "coverage_pct": coverage_pct,
        "have": have,
        "total": total,
        "gaps": gaps,
    }


# ---------------------------------------------------------------
# UI
# ---------------------------------------------------------------
def main() -> None:
    st.title("🛡️ SME Check")
    st.markdown(
        "**A cybersecurity self-assessment for Irish SMEs, "
        "based on NIST CSF 2.0 and empirical threat data.**"
    )
    st.caption(
        "Companion tool to the MSc practicum research at NCI. "
        "Takes ~10 minutes. Nothing is sent to any server - "
        "your answers stay in your browser session."
    )

    st.divider()

    # ----- Organisation profile -----
    st.subheader("About your organisation")
    col1, col2 = st.columns(2)
    with col1:
        sector = st.selectbox(
            "Sector",
            [
                "Professional services", "Retail", "Manufacturing",
                "Healthcare", "ICT / Software", "Hospitality",
                "Construction", "Education", "Other",
            ],
        )
    with col2:
        size = st.selectbox(
            "Employees",
            ["1-9 (Micro)", "10-49 (Small)", "50-249 (Medium)"],
        )

    st.divider()

    # ----- Assessment -----
    st.subheader("Your current controls")
    st.caption("Tick each control your organisation currently has in place.")

    questions = load_questions()
    answers = {}
    for q in questions["items"]:
        answers[q["id"]] = st.checkbox(q["text"], key=q["id"])

    st.divider()

    # ----- Submit -----
    if st.button("Get my assessment", type="primary", use_container_width=True):
        result = compute_dummy_score(answers, questions)

        st.success(
            f"You have implemented {result['have']} of {result['total']} controls "
            f"({result['coverage_pct']:.0f}% coverage)."
        )

        st.metric("Coverage score", f"{result['coverage_pct']:.0f}%")

        st.subheader("Your top priority gaps")
        st.caption(
            "⚠️ Priority scores below are PLACEHOLDER values. "
            "The real version calls into `csf_sme_coverage.score` "
            "which uses the Verizon 2026 DBIR + MTU/NCSC 2025 evidence base."
        )
        st.dataframe(result["gaps"], use_container_width=True, hide_index=True)

        st.info(
            "📄 PDF export coming in a future release "
            "(WeasyPrint + Jinja2 template). "
            "For now, use your browser's Print to PDF."
        )

    # ----- Footer -----
    st.divider()
    st.caption(
        "Built on the [csf-sme-coverage](https://github.com/Viru1998/csf-sme-coverage) "
        "analytical pipeline. MIT Licence. "
        "Viraj Ananda Gawde - MSc Cybersecurity, NCI."
    )


if __name__ == "__main__":
    main()

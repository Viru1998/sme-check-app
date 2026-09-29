"""
SME Check - NIST CSF 2.0 Self-Assessment for Irish SMEs
Streamlit MVP (v0.5 real scoring).

Run locally:
    streamlit run app.py

Deploy free at:
    https://streamlit.io/cloud (point at this GitHub repo)
"""

from pathlib import Path
import yaml
import streamlit as st
import pandas as pd

from ordering import SECTOR_KEYS, order_questions
from scoring import load_priority, score_assessment

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
# Scoring
# ---------------------------------------------------------------
@st.cache_data
def load_priority_table() -> pd.DataFrame:
    """Load priority scores per CSF Subcategory (cached across reruns)."""
    return load_priority()


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
        "Companion tool to the MSc practicum research. "
        "Takes about 10 minutes. Your answers are processed to produce your "
        "results and are not stored, logged, or shared by this app. The app is "
        "hosted on Streamlit Community Cloud, which sets its own analytics and "
        "functional cookies — see "
        "[Streamlit's privacy policy](https://streamlit.io/privacy-policy)."
    )

    st.divider()

    # ----- Organisation profile -----
    st.subheader("About your organisation")
    col1, col2 = st.columns(2)
    with col1:
        sector = st.selectbox("Sector", list(SECTOR_KEYS))
    with col2:
        size = st.selectbox(
            "Employees",
            ["1-9 (Micro)", "10-49 (Small)", "50-249 (Medium)"],
        )

    st.divider()

    # ----- Assessment -----
    st.subheader("Your current controls")
    sector_key = SECTOR_KEYS[sector]
    st.caption(
        "Tick each control your organisation currently has in place."
        + (
            f" Questions most relevant to {sector} are shown first."
            if sector_key
            else ""
        )
    )

    questions = load_questions()
    answers = {}
    for q in order_questions(questions["items"], sector_key):
        answers[q["id"]] = st.checkbox(q["text"], key=q["id"])

    st.divider()

    # ----- Submit -----
    if st.button("Get my assessment", type="primary", width="stretch"):
        result = score_assessment(answers, questions, load_priority_table())

        st.metric(
            "Threat-weighted coverage",
            f"{result['weighted_pct']:.0f}%",
            help=(
                "Share of the total priority score you have partially addressed. "
                "Each Subcategory is weighted by Verizon 2026 DBIR threat weight "
                "× MTU/NCSC 2025 Irish adoption gap."
            ),
        )
        st.success(
            f"{result['have']} of {result['total']} CSF Subcategories "
            f"partially addressed ({result['coverage_pct']:.0f}% unweighted)."
        )

        st.info(
            "ℹ️ **How coverage is scored.** Coverage is measured per CSF "
            "Subcategory: a Subcategory counts as covered if *any* question "
            "mapped to it is ticked. For example, MFA on email but not on admin "
            "accounts still marks PR.AA-05 (access permissions) as covered. "
            "Real-world security is more granular than this, so treat covered "
            "Subcategories as partially addressed, not complete."
        )

        st.subheader("Your top priority gaps")
        st.caption(
            "Priority score = Verizon 2026 DBIR threat weight × MTU/NCSC 2025 "
            "Irish adoption gap, from the csf-sme-coverage pipeline. "
            "A score of 0 means the source data has either no threat weight or "
            "no Irish adoption-gap figure for that Subcategory - not that it "
            "is unimportant."
        )
        st.dataframe(result["gaps"], width="stretch", hide_index=True)

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
        "Viraj Ananda Gawde - MSc Cybersecurity."
    )


if __name__ == "__main__":
    main()

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**SME Check** — a Streamlit-based cybersecurity self-assessment tool for Irish small and medium enterprises, based on NIST Cybersecurity Framework 2.0.

An Irish SME owner (or their advisor) fills a ~10-minute assessment describing their existing security controls. The app returns their CSF 2.0 coverage score, a personalised list of priority gaps, and (in v0.5+) a NIS2 / DORA regulatory alignment view and a branded PDF report.

## Origin and status

This app is the follow-on artefact from a completed MSc Cybersecurity practicum at the National College of Ireland (2026), *"Measuring the Threat-Informed Effectiveness of NIST CSF 2.0 for SMEs Using MITRE ATT&CK and Empirical Incident Data"*. The dissertation delivered:

- A reproducible Python pipeline (`csf-sme-coverage`, separate repo) computing CSF 2.0 Subcategory priority for SMEs against Verizon DBIR 2026 SMB techniques and MTU/NCSC 2025 Irish adoption gap data
- Four principal findings, of which one — the **double-witness priority metric** (Verizon threat weight × Irish adoption gap) — is the analytical engine this app operationalises
- The rank-1 recommendation for Irish SMEs: **PR.IR-01** (Networks and environments protected from unauthorized access), combined score 2.04

**Current version: v0.5 in progress.** Real any-tick scoring against the dissertation pipeline's `combined_priority.csv` is done. Extending the question set to ~40 and the WeasyPrint PDF are still outstanding.

## Repo layout

```
sme-check-app/
├── app.py                Streamlit entry point: page config, cached loaders, UI
├── scoring.py            Any-tick scoring; no Streamlit imports so pytest can import it
├── data/
│   ├── questions.yml     20 SME-friendly questions, each mapped to a CSF Subcategory
│   ├── combined_priority.csv   Pinned snapshot of the pipeline output (do not hand-edit)
│   └── PROVENANCE.md     Source commit of the CSV snapshot and how to refresh it
├── tests/                pytest tests for scoring.py
├── requirements.txt      Runtime deps (streamlit, pandas, pyyaml); future deps listed as comments
├── requirements-dev.txt  Adds pytest and black
├── LICENSE               MIT
├── README.md             Public-facing project overview + roadmap
└── CLAUDE.md             This file
```

## How the current code fits together

- **Streamlit reruns the whole script on every interaction.** `main()` in `app.py` rebuilds the form on every rerun. Results only render in the rerun triggered by the "Get my assessment" button, so they vanish on the next widget change. Use `st.session_state` if results need to persist, for example for a PDF download button.
- **Question IDs are also widget keys.** Each checkbox uses `key=q["id"]`, and `answers` is a `{question_id: bool}` dict. A duplicate ID in `questions.yml` causes a Streamlit `DuplicateWidgetID` error.
- **`load_questions()` and `load_priority_table()` are wrapped in `@st.cache_data`.** Edits to `questions.yml` or the CSV won't appear in a running app until you clear the cache (press `C` in the app) or restart it.
- **`questions.yml` schema:** top-level `version`, `last_updated`, and `items`. Each item has `id`, `text` and `csf_subcategory` (currently a single string). Several questions map to the same Subcategory: `PR.AA-05` and `PR.IR-01` have 3 each. The YAML header says "one or more" Subcategories, so if you add list support, update every consumer.
- **The scorer's return contract drives the UI.** `scoring.score_assessment(answers, questions, priority)` returns `{weighted_pct, coverage_pct, have, total, gaps}`. `have` and `total` count Subcategories, not questions. `gaps` is a DataFrame with columns `CSF Subcategory`, `Priority score`, `Questions` and `Note`. The results section reads these keys directly, so change the UI in the same edit as the contract.
- **`score_assessment` raises `ValueError` if a question maps to a Subcategory missing from the CSV.** A test also checks this against the real data, so a new question with a mistyped or unscored Subcategory fails `pytest`.
- **Privacy invariant:** the UI tells users "Nothing is sent to any server - your answers stay in your browser session." Don't add logging, persistence or telemetry of answers without updating that copy. Saved scans are a v1.0 feature and go under the gitignored `data/user_scans/` or `*.sqlite`.

## The scoring architecture we're building toward

Three tiers:

**Frontend (Streamlit for MVP, later Flask+Bootstrap):**
- Assessment form (sector, size, ~40 checkbox questions)
- Results dashboard (coverage score, priority chart)
- PDF report download
- NIS2 / DORA article-level regulatory view

**Backend (currently in-process; later a real Flask API):**
- Reads a pinned snapshot of the `csf-sme-coverage` pipeline's `combined_priority.csv` (see "The related repository" below)
- `scoring.py` filters that table by the SME's existing posture (the role originally planned for `personalise.py`)
- Report generation via WeasyPrint + Jinja2

**Data:**
- Precomputed CSVs from the `csf-sme-coverage` pipeline (coverage_matrix, combined_priority, irish_gap_ranking)
- SQLite for saved assessments (v1.0)
- Monthly cron re-runs the pipeline against fresh Verizon/ENISA/MTU downloads

### Scoring semantics

v0.5 uses **any-tick semantics**: a CSF Subcategory counts as "have" if at least one question mapped to it is ticked. It counts as a gap only when every question mapped to it is unticked.

- Coverage is measured over Subcategories: (Subcategories marked "have") ÷ (distinct Subcategories in `questions.yml`).
- The gap list contains only Subcategories that are gaps, ranked by their `combined_priority.csv` score. Each Subcategory appears once, however many questions map to it.
- Example: ticking only `mfa_email` marks `PR.AA-05` as "have", even though `mfa_admin` and `least_privilege` are unticked.
- **Weighted coverage** (the results headline) = sum of `combined_score` for covered Subcategories ÷ the sum for all Subcategories in `questions.yml`. Unweighted coverage (the Subcategory count) is shown beneath it.
- **Zero scores:** 7 of the 13 current Subcategories have `combined_score` 0. `GV.PO-01`, `PR.AT-01` and `RS.MA-01` have no Verizon threat weight. `PR.PS-01`, `DE.CM-01`, `PR.DS-01` and `GV.SC-04` have a threat weight but an Irish gap of 0. They add nothing to weighted coverage and sort last in the gap list with a Note. A 0 means missing data, not low importance, so the UI must not imply otherwise.
- **Top-10 cap:** with nothing ticked, the cap drops three zero-score gaps, which tie and sort alphabetically. With ~40 questions this will matter more.
- **User-facing wording:** because any-tick is coarse, the results page and PDF report must label covered Subcategories "partially addressed", never "complete" or "fully covered". Keep this in sync with the "How coverage is scored" disclaimer in `README.md`.

## Versioned roadmap

| Version | Effort | Deliverable |
|---|---|---|
| **v0.1** ✅ | ~10 h | Streamlit skeleton runnable, dummy scoring, YAML questions |
| **v0.5** 🟡 | ~30 h | Real scoring from `csf_sme_coverage` output ✅, questions extended to ~40, WeasyPrint PDF |
| **v0.7** | ~40 h | NIS2 / DORA article-level view, deployed to Streamlit Cloud |
| **v1.0** | ~40 h | Flask-Login accounts, saved scans, sector-specific question sets, email delivery |

**Scoring review (v0.7 or v1.0):** evaluate replacing any-tick semantics with fractional per-Subcategory scoring (for example, 2 of 3 `PR.AA-05` questions ticked = 0.67). Base the decision on real user feedback about whether any-tick overstates coverage. See "Scoring semantics" above.

The v0.7 Streamlit Cloud deployment is temporary: the v1.0 Flask migration replaces it. Keep this roadmap and the one in `README.md` in sync when either changes.

## Conventions

- **Python style:** black-formatted, type hints on new code, docstrings on public functions.
- **Question IDs in questions.yml are permanent.** Once shipped, never rename a question ID — it will break the mapping to CSF Subcategories in the scoring engine. Add new questions with new IDs instead.
- **CSF Subcategory IDs match NIST CSF 2.0 exactly.** No abbreviations, no lowercasing (`PR.IR-01`, not `pr.ir-01` or `PR-IR-01`).
- **Placeholder code is labelled `# PLACEHOLDER` inline**, so a grep finds it. Replace placeholders; don't extend them.
- **Never commit real SME assessment data.** `.gitignore` excludes `data/user_scans/` and any `*.sqlite` — respect this.

## The related repository

- **`csf-sme-coverage`** at <https://github.com/Viru1998/csf-sme-coverage> — the analytical engine. It is **not** a pip dependency. Its package doesn't ship `outputs/`, it locates the CSV via `Path(__file__).parents[2]`, and its runtime deps (mitreattack-python, stix2, scipy, matplotlib...) are unused here. Instead, `data/combined_priority.csv` is a byte-for-byte copy from a pinned commit (recorded in `data/PROVENANCE.md`). Copying its output data is fine; don't fork or copy the pipeline code.

## Local development

```powershell
cd D:\Viraj\NCI\Practicum\sme-check-app

# Environment (once)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# Run
streamlit run app.py
streamlit run app.py --server.headless true   # no auto-opened browser tab

# Format
black .

# Tests (pyproject.toml puts the repo root on sys.path)
pytest
pytest tests/test_scoring.py::test_any_tick_marks_subcategory_covered   # single test
```

Opens at http://localhost:8501. For tests, keep logic in plain modules like `scoring.py` that don't call `st.*`. `app.py` runs Streamlit calls at import time (`st.set_page_config`), so importing it from pytest isn't clean. To smoke-test the UI headlessly, use `streamlit.testing.v1.AppTest.from_file("app.py")`.

Remaining v0.5 dependencies (`weasyprint`, `jinja2`) are already listed as comments in `requirements.txt`. Uncomment them there instead of adding new lines. WeasyPrint on Windows also needs the GTK/Pango runtime installed.

## What I want help with (typical requests)

- Implementing new features from the roadmap (the rest of v0.5 — ~40 questions and the PDF — is next)
- Extending `questions.yml` with additional SME-friendly checkboxes mapped to CSF Subcategories
- Wiring the WeasyPrint + Jinja2 PDF export
- Deploying to Streamlit Cloud
- Migrating from Streamlit to Flask+Bootstrap when the app outgrows Streamlit
- Writing pytest tests as we add real logic

## What I do NOT want help with

- Rewriting or forking the `csf-sme-coverage` analytical engine (that repo is settled and the dissertation is graded)
- Adding features that would require primary Irish SME data collection (that's out of scope until the tool has real users)
- Full-rewrites when incremental changes will do

## Author

**Viraj Ananda Gawde** — MSc Cybersecurity, National College of Ireland (2026, 2:1). GitHub: [@Viru1998](https://github.com/Viru1998).

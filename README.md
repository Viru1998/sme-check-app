# SME Check

**A cybersecurity self-assessment tool for Irish small and medium enterprises, based on NIST CSF 2.0 and empirical threat evidence.**

An SME owner or advisor fills a ten-minute assessment describing their existing security controls; the app returns their coverage score, a personalised list of priority gaps, and (in v1.0) a NIS2 / DORA alignment report as a downloadable PDF.

Built on the [csf-sme-coverage](https://github.com/Viru1998/csf-sme-coverage) analytical pipeline — companion code to the MSc Cybersecurity practicum research at the National College of Ireland (2026).

---

## Status: MVP skeleton (v0.1)

Currently a working Streamlit skeleton with placeholder scoring. The full v1.0 roadmap:

| Milestone | Status | Notes |
|---|---|---|
| Streamlit skeleton runnable end-to-end | ✅ v0.1 | Form UI, YAML-loaded questions, dummy scoring |
| Real scoring against `csf_sme_coverage` | ⬜ v0.5 | Wire the priority engine as a pip dependency |
| PDF report export | ⬜ v0.5 | WeasyPrint + Jinja2 |
| NIS2 / DORA article-level view | ⬜ v0.7 | Reorganise gap list by regulatory obligation |
| User accounts + saved scans | ⬜ v1.0 | Flask-Login + SQLite |
| Deployed publicly | ⬜ v1.0 | Streamlit Cloud → sme-check.streamlit.app |

---

## Quick start (local)

```bash
git clone https://github.com/Viru1998/sme-check-app.git
cd sme-check-app

# Create a fresh environment (conda or venv - either works)
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt

streamlit run app.py
```

The app will open at <http://localhost:8501>. Complete the assessment, click **Get my assessment**, and you'll see a placeholder score and gap list. (Real scoring is wired up in v0.5.)

---

## Deploy free on Streamlit Cloud

1. Push this repo to GitHub (you're reading it there now).
2. Go to <https://share.streamlit.io> and sign in with your GitHub account.
3. Click **New app**, select this repo, main file `app.py`, and deploy.
4. Your app is live at `https://<your-username>-sme-check-app.streamlit.app` in about 2 minutes.

No credit card, no server management. Streamlit Cloud auto-redeploys on every git push.

---

## Repository layout

```
sme-check-app/
├── app.py                Streamlit entry point (~120 lines)
├── data/
│   └── questions.yml     20-question assessment (extend to ~40 for v1.0)
├── requirements.txt      Pinned dependencies
├── LICENSE               MIT
└── README.md             This file
```

---

## Question set

The initial 20 questions cover the highest-priority CSF 2.0 Subcategories identified in the underlying research: `PR.IR-01` (network protection), `PR.AA-05` (least privilege), `DE.CM-09` (endpoint monitoring), `PR.DS-11` (backups), `GV.PO-01` (policy), `RS.MA-01` (incident response), `PR.AT-01` (training) and 13 others.

Each question is mapped to its CSF Subcategory in [`data/questions.yml`](data/questions.yml). Adding a new question is a two-line YAML edit — no code change required.

---

## Roadmap

Contributions (once v1.0 is out) welcome. Priorities in rough order:

- Wire the real `csf_sme_coverage` scoring engine (v0.5)
- Extend questions from 20 to ~40 (v0.5)
- WeasyPrint PDF report with a branded template (v0.5)
- Sector-specific question sets for the 11 MTU/NCSC 2025 sectors (v0.7)
- NIS2 / DORA article-level alignment view (v0.7)
- Multi-language support: English + Irish Gaeilge (v1.1)

---

## Citation

If you use this tool or the underlying methodology in academic work, please cite:

> Gawde, V.A. (2026). *Measuring the Threat-Informed Effectiveness of NIST CSF 2.0 for SMEs Using MITRE ATT&CK and Empirical Incident Data.* MSc Practicum, School of Computing, National College of Ireland.

---

## Licence

MIT. See [`LICENSE`](LICENSE).

Data files remain the property of their respective publishers (NIST, MITRE, CTID, Verizon, ENISA, MTU, NCSC Ireland) and are used under fair-use for academic reproducibility.

---

## Author

**Viraj Ananda Gawde**
MSc Cybersecurity — National College of Ireland
[GitHub: @Viru1998](https://github.com/Viru1998)

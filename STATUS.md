# Grade 1 Math Challenge — Status & Resume Guide

Last updated: 2026-06-21

Sister project to the **Grade 4** challenge (`/Users/natalia/FunWithAI/MathChallenge`).
Same tooling and design, but a **fully separate site and backend** so the two grades never mix:
its own GitHub repo/URL, its own Google Sheet, and its own Apps Script Web App endpoint.

The tooling (`build_week.py`, `gate_solutions.py`, `leaderboard.html`, `apps_script_backend.gs`,
`index.html`) is identical to Grade 4 except: paths/labels say **grade1 / "Grade 1 — Week N"**,
and the endpoint URL is blank until the backend is deployed.

## Setup checklist
- [ ] **Create the Google Sheet + deploy the Apps Script Web App** (see `weeks/grade1/SHEET_SETUP.md`).
      Paste `weeks/grade1/apps_script_backend.gs` into the Sheet-bound Apps Script, Deploy → Web app.
- [ ] **Paste the `/exec` endpoint** into `ENDPOINT_URL` in BOTH
      `weeks/grade1/build_week.py` (line ~32) and `weeks/grade1/leaderboard.html` (the `const ENDPOINT_URL`).
- [ ] **Create the GitHub repo** (e.g. `math-challenge-grade1`) and enable Pages from `main` / root.
- [ ] **Author weeks**: drop images + `week.json` into `weeks/grade1/weekN/`, run
      `cd weeks/grade1 && python3 build_week.py weekN`, add the `Grade 1 — Week N` row to the Sheet's
      `AnswerKey` tab, then push.

## How to make changes
Identical to the Grade 4 project — see that repo's `STATUS.md` §6 for the full how-to
(add/update a week, build + lock solutions, change the backend, debug scoring). Everything works the
same here; just substitute "grade1" for "grade4".

Passcodes for `gate_solutions.py`: developer `4891`, teacher `2026` (same as Grade 4 — change if desired).

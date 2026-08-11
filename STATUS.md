# Grade 1 Weekly Math Challenge — Status & Resume Guide

Last updated: 2026-08-10

> **Read this first if starting a new session.**
> Sister project to the **Grade 4** challenge (`/Users/natalia/FunWithAI/MathChallenge`).
> Same tooling and design, but a **fully separate site and backend** so the two grades never mix:
> its own GitHub repo/URL, its own Google Sheet, and its own Apps Script Web App endpoint.

⚠️ **This file is committed to a PUBLIC repo — never write answer keys or solutions into it.**
The keys live in the Sheet's `AnswerKey` tab only. (Grade 4 keeps a local gitignored
`ANSWER_KEYS.md`; do the same here if you want an offline copy — never commit it.)

---

## 1. Live URLs

- **Site (share this):** https://mkcoach123.github.io/math-challenge-grade1/
  - Leaderboard: `…/weeks/grade1/leaderboard.html`
  - Week N problems: `…/weeks/grade1/weekN/grade1_weekN.html`
  - Week N solutions (passcode-locked): `…/weeks/grade1/weekN/solutions_weekN.html`
- **GitHub repo:** `MKcoach123/math-challenge-grade1` (public; Pages from `main` / root)
- **Local folder:** `/Users/natalia/FunWithAI/MathChallenge-Grade1`
- **Backend endpoint (Apps Script Web App):**
  `https://script.google.com/macros/s/AKfycbwhousf9U3W_KSbEFs6HYTJ6ySsyeEK0fRcsHvM0p_L6wVAZteLLDNdfn-Itzh1BI6Vsg/exec`
  (wired into `weeks/grade1/build_week.py` line ~32 **and** `weeks/grade1/leaderboard.html`)

## 2. Setup — all done ✅

- [x] Google Sheet + Apps Script Web App created and deployed (`weeks/grade1/SHEET_SETUP.md`)
- [x] `/exec` endpoint pasted into `build_week.py` and `leaderboard.html`
- [x] GitHub repo created, Pages enabled from `main` / root
- [x] Weeks authored — see §3

**It is fully live and scoring**: all 7 weeks have `AnswerKey` rows, all 7 match their page labels,
and real submissions are coming in for every week.

## 3. Weeks built

5 problems per week. Answers are **not** listed here on purpose (see the warning above) — to check a
key, open the Sheet's `AnswerKey` tab.

| Week | Problems | Solutions page |
|------|----------|----------------|
| **Grade 1 — Week 1** | brick stacks (num,img), Omar's goals (num,img), stone to move (num,img), pyramid ? (num,img), frogs balance a cat (num,img) | ✅ built, locked |
| **Grade 1 — Week 2** | count triangles (num,img), cats behind fence (num,img), pattern ? (choice,img), Amelia/Juliana/Mira numbers (num), Bluey lego most (text,img) | ✅ built, locked |
| **Grade 1 — Week 3** | 3 gnomes' names (choice,img), treasure-chest key (choice,img), Kira's apples (num,img), pencil length (num,img), ink-spill equation (num,img) | ✅ built, locked |
| **Grade 1 — Week 4** | Alisa's acorns (num), Maia's cookies (num), pennies in a dime (num), birds/butterflies/dogs (num), doggies balance a lion (num,img) | ✅ built, locked |
| **Grade 1 — Week 5** | Ian/Michael/Athena candy (text), Anusha's pages (num), Emily's clouds (num,img), teacher's problem (num,img), Arthur's toy cars (num) | ❌ **not built** |
| **Grade 1 — Week 6** | beehive jobs, 40 bees (num,img), Jonathan's family apples (num), number line ? (num,img), count apples (num,img), Abby & Penny bracelets (num) | ❌ **not built** |
| **Grade 1 — Week 7** | gardener's bushes (num), FIFA flags (num), square pattern ? (choice,img), pyramid ? (num,img), Mia's lego 30 pieces (num,img) | ❌ **not built** |

All existing solution pages are **passcode-locked** (`solutions_available: false`).
Passcodes: developer `4891`, teacher `2026`.

## 3b. Site wording (matched to Grade 4 on 2026-08-08)

- Home page title/heading: **"Grade 1 Weekly Math Challenge"**; leaderboard titled to match.
- Deadline is **Friday afternoon** (was Sunday night) — set in the home-page footer *and* per week
  via `"due"` in each `week.json`, so the week pages agree with the home page. All 7 weeks updated.
- Change `"due"` in `week.json` and rebuild rather than editing the generated HTML, or the next
  `build_week.py` run reverts it.

⚠️ **Reorder gotcha:** if you insert/reorder problems, the `AnswerKey` columns shift. Re-check the
row order after editing a week.

## 4. How to make changes

Identical to the Grade 4 project — see that repo's `STATUS.md` §6 for the full how-to (add/update a
week, build + lock solutions, change the backend, debug scoring). Substitute "grade1" for "grade4".

Quick reference:
- Build a week: `cd weeks/grade1 && python3 build_week.py weekN` (also rebuilds `index.html` + leaderboard week list)
- Lock solutions: `python3 gate_solutions.py 4891 2026` (re-run after ANY edit to a solution page)
- Reveal a week: set `"solutions_available": true` → re-run `gate_solutions.py` → `build_week.py --index` → push
- Deploy: `git add -A && git commit -m "…" && git push` (Pages updates in ~1 min)
- Debug scoring: `…/exec?view=debug` — but see the warning in §5

**Answer source docs stay local.** `.gitignore` covers `solutions_*.pages`, `*_solution.pages`,
`*_solutions.pages` (all three spellings — a singular `week2_solution.pages` once slipped past
plural-only patterns and got published; it was untracked on 2026-08-08, but it remains in the repo's
git history).

## 5. Open items / next steps

- [ ] **Build solutions for weeks 5, 6, 7** (weeks 1–4 done).
- [ ] **`?view=debug` on the public endpoint returns every answer key** to anyone who calls it, and the
      endpoint URL is visible in each problem page's source. Consider gating the debug view behind a
      query token, or removing it once scoring is verified. (Same issue in the Grade 4 backend.)
- [x] ~~Grade 4's `STATUS.md` publishes its full answer-key table~~ — stripped 2026-08-10; keys moved
      to a gitignored `ANSWER_KEYS.md` there. (Both repos' histories still contain what was published.)
- [ ] **Reveal solutions per deadline:** flip `solutions_available` → re-gate → rebuild → push.
- [x] ~~Per-week due date placeholder~~ — all 7 weeks now say **Friday afternoon** (2026-08-08).
- [ ] **Mirror Grade 4's week-status feature** here: a `CURRENT_WEEK` constant in `build_week.py`
      marking this week / past / "coming soon" on the home-page cards. Grade 1 has its own copy of
      `build_week.py` and `index.html`, so it needs the same edit plus the CSS in `index.html`.
- [ ] **Consider classmate names in problems** — Grade 4 is renaming characters to real class names
      to motivate students. Grade 1 already uses many. ⚠️ Check first whether a name is the *answer*:
      **Week 2 P5 (Coco), Week 3 P1 (Tim) and Week 5 P1 (Athena)** all answer with a name — renaming
      those means editing the `AnswerKey` and re-grading past submissions.
- [ ] **Untested: school Chromebooks.** Backend is on `script.google.com`; if the district filters it,
      pages load but submissions and the leaderboard fail. Test on a real device.
- [ ] (Optional) purge `weeks/grade1/week2/week2_solution.pages` from git history if the old commits matter.

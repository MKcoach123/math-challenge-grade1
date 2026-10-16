# Grade 1 Weekly Math Challenge — Status & Resume Guide

Last updated: 2026-09-15

> **Read this first if starting a new session.**
> Sister project to the **Grade 4** challenge (`/Users/natalia/FunWithAI/MathChallenge`).
> Same tooling and design, but a **fully separate site and backend** so the two grades never mix:
> its own GitHub repo/URL, its own Google Sheet, and its own Apps Script Web App endpoint.

### ⏯️ Resuming (2026-09-15)

**Week 4's five problems were fully replaced** and pushed live (see §3). The Sheet's `AnswerKey`
row for Week 4 already matched the new set, so nothing was re-graded.

Working tree is clean apart from `weeks/grade1/week3/week3_problems.pages` (a pre-existing local
change, not from any recent edit). Everything else is committed and live.

⚠️ **`weeks/grade1/week4/week4_problems.pages` is now STALE** — it still holds the old acorns /
cookies / pennies problems, while the site serves the new set from
`week4_problems NEW.pages` (both are tracked). Re-importing from the old file would silently
resurrect the retired week. Same trap as Grade 4's `solutions_week2.pages`.

🔴 **Biggest risk, shared with Grade 4:** the Grade 4 site was **blocked by the Santa Clara Unified
web filter** on a district Chromebook (2026-09-09). This site is on the same `github.io` domain, so
**assume it is blocked too**. Both grades need the district to allowlist `*.github.io` (or these
two specific sites) **and** `script.google.com`. See Grade 4's `STATUS.md` §7 for the full
diagnosis and a draft email to the technology coordinator. Embedding in Google Sites does **not**
work around it. Until then, paper is the fallback.

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
| **Grade 1 — Week 4** | shape cut out (**choice A–D**,img), count circles in figure (num,img), pattern what comes next (**choice A–C**,img), gray vs white squares (num,img), doggies balance a lion (num,img) | ✅ built, locked |
| **Grade 1 — Week 5** | missing digits (**choice, word pills**,img), Anusha's pages (num), piece missing from house (**choice A–E**,img), butterflies = 12 (num,img), Ian/Michael/Mira candy (text) | ✅ built, locked |
| **Grade 1 — Week 6** | beehive jobs, 40 bees (num,img), Jonathan's family apples (num), number line ? (num,img), count apples (num,img), Abby & Penny bracelets (num) | ❌ **not built** |
| **Grade 1 — Week 7** | gardener's bushes (num), FIFA flags (num), square pattern ? (choice,img), pyramid ? (num,img), Mia's lego 30 pieces (num,img) | ❌ **not built** |

**Week 3 solution edits (2026-09-13):** Problem 4 (pencil length) now states the **unit** in both
the answer line and the working, instead of giving a bare number — the figure is a 12-inch ruler,
so the unit had been left implicit. Problem 5 (ink-spill equation) had its second sentence
reworded to *show* the rearranging step rather than assert it. The `AnswerKey` was **not** touched
— solution pages are display-only, and changing a key would re-grade past submissions.
**Week 3 P4 ruler fixed (2026-09-17):** the ruler graphic was labelled `1,2,3,3,4,…,12` — thirteen
marks with **"3" printed twice**, so every label after it sat one short. The pencil spans five inch
intervals (the key is right), but a student reading the printed numbers saw "1" to "5" and answered
**4**. Relabelled **0–12**; only the first four labels were wrong, which shows the ruler was always
meant to start at 0 — as the solution's "read where its tip ends" already implied. The digits are
the image's own glyphs shifted over, so the style matches. `"unit": "inches"` added at the same
time (this was the long-standing open item below).

All existing solution pages are **passcode-locked** (`solutions_available: false`).
Passcodes: developer `4891`, teacher `2026`.

## 3b. Site wording (matched to Grade 4 on 2026-08-08)

- Home page title/heading: **"Grade 1 Weekly Math Challenge"**; leaderboard titled to match.
- Deadline is **Friday afternoon** (was Sunday night) — set in the home-page footer *and* per week
  via `"due"` in each `week.json`, so the week pages agree with the home page. All 7 weeks updated.
- Change `"due"` in `week.json` and rebuild rather than editing the generated HTML, or the next
  `build_week.py` run reverts it.

**Week 4 P3 figure (2026-09-15):** the pattern and its A/B/C options are **one composed image**,
not two. Two figures rendered *side by side* with the options larger than the pattern circles,
because the screen CSS leaves `.problem img` inline (`build_week.py:221`) while only the print rule
sets `display:block`. Don't "fix" that globally — week 3 P2 puts its key and lock figures side by
side on purpose. Both P3 sources have 99px circles natively, so stacking them unscaled is what
makes the option circles match the pattern.

⚠️ **Reorder gotcha:** if you insert/reorder problems, the `AnswerKey` columns shift. Re-check the
row order after editing a week.

**Week 5 fully replaced (2026-10-16).** All five problems are new except Anusha's pages (still P2).
Source: `week5_problems NEW.pages`; `week5_problems.pages` is now **STALE** — same trap as Week 4.

🔴 **The `AnswerKey` row for `Grade 1 — Week 5` must be rewritten before this goes out.** Every
answer but P2 changed, and the problems were reordered, so the columns shift (the §3 reorder
gotcha). Week 5 already has real submissions — rewriting the key **re-grades them**, turning past
correct answers wrong. Decide that deliberately; the keys are in the Sheet, not here.

- **P1 is answered with a word pill, not a letter** — the options are text ("3 and 5", "4 and 8", …)
  so the submitted value is the phrase itself, like Week 3's Jim/Nim/Tim. The key must be the
  phrase, not "C". P3's options are *pictures*, so it stays A–E letters.
- The candy problem's third character was **renamed** and it moved from **P1 to P5**. It is
  still a name-as-answer, so the key changes as well as the column — see §5.
- Author fixes made while building, flag if unwanted: the solution for the butterflies said
  "2 + 2 + 2 = 6 which is less than **9**" where the target is 12; "Lets" → "Let's" (the author
  writes "Let's" in P5); "Same number is hiding behind a butterfly" → "The same number is hiding
  behind **each** butterfly"; "Who has most candies?" → "Who has **the** most candies?".
- P3's figure is the house and its A–E options **composed into one image** — two separate `<img>`
  render side by side on screen (§3b, same as Week 4 P3).
- `"page_starts"` was removed: Week 5 used to be all text and fit one sheet, but with four figures
  it now needs two, so it takes the default break before P4. Print widths for P1/P3 were trimmed
  (265px/300px) so problems 1–3 clear a page — screen sizes are untouched.
- The old `p3_clouds.png` / `p4_board.png` figures were deleted; nothing references them.

## 3c. Printing (fixed 2026-10-16 — mirrors Grade 4)

⚠️ **A problem could vanish from the printout.** Grade 4 Week 6 printed and saved to PDF with its
last problem **missing entirely** — not moved to another page, gone. Every `.problem` has
`break-inside: avoid`, so one that doesn't fit is pushed whole to the next page; WebKit fixes the
page count up front from the unbroken document height, so once those pushes run past the last page
the overflow has nowhere to land and is dropped. Anything that shrinks the usable page height sets
it off — Safari's **"Print headers and footers" is on by default and costs ~70pt on its own**.

The same three fixes are now in this repo's `build_week.py`:
1. `.problem.page-start { break-before: page }`, applied by default to every 3rd problem
   (`page_starts` in `render_week`). A *forced* break makes WebKit allocate a real page, so content
   can no longer be pushed past the end. Worst case a sheet spills; nothing is lost.
2. `@page { size: auto }` instead of `size: A4 portrait` — these print on US Letter.
3. Tightened print spacing (header/name-box margins, `.problem` 16→11pt, image/answer margins).

All 7 weeks rebuilt; each prints **3 + 2**, except:
- **Week 5 is `"page_starts": []`** in its `week.json` — it is all text and fits on **one sheet**,
  so a forced break would split a one-page worksheet in two. Measured at ~630pt of 665pt.
- **Week 3 is the tight one:** problems 1–3 run to ~697pt, over the ~665pt that is left when
  headers/footers are on, so it then spills to three sheets (2 \| 1 \| 2). Nothing is lost.
  Telling teachers to untick **"Print headers and footers"** keeps every week at two sheets.

⚠️ If a week prints with too much white space on page 1, set `"page_starts": []` in its
`week.json` and rebuild — don't remove the mechanism from `build_week.py`.

---

## 4. How to make changes

Identical to the Grade 4 project — see that repo's `STATUS.md` §6 for the full how-to (add/update a
week, build + lock solutions, change the backend, debug scoring). Substitute "grade1" for "grade4".

Quick reference:
- Build a week: `cd weeks/grade1 && python3 build_week.py weekN` (also rebuilds `index.html` + leaderboard week list)
- Lock solutions: `python3 gate_solutions.py 4891 2026` (re-run after ANY edit to a solution page)
  ⚠️ It rewrites **all** solution pages and leaves 3 blank lines in each, so untouched weeks show up
  as modified. Revert the blank-line-only ones so the diff stays honest.
- Reveal a week: set `"solutions_available": true` → re-run `gate_solutions.py` → `build_week.py --index` → push
- Deploy: `git add -A && git commit -m "…" && git push` (Pages updates in ~1 min)
- Debug scoring: `…/exec?view=debug` — but see the warning in §5

**Answer source docs stay local.** `.gitignore` covers `solutions_*.pages`, `*_solution.pages`,
`*_solutions.pages` (all three spellings — a singular `week2_solution.pages` once slipped past
plural-only patterns and got published; it was untracked on 2026-08-08, but it remains in the repo's
git history).

## 5. Open items / next steps

- [ ] **Build solutions for weeks 6, 7** (weeks 1–5 done).
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
      **Week 2 P5, Week 3 P1 and Week 5 P5** are all answered with a name — renaming the
      character means editing the `AnswerKey` and re-grading past submissions. (The names
      themselves are deliberately not listed here: this is a public repo. Check the Sheet.)
- [ ] 🔴 **District filter blocks the sister site on school Chromebooks** (confirmed for Grade 4 on
      2026-09-09; this site shares the `github.io` domain, so assume the same). Needs an allowlist
      request to SCUSD for the site domain **and** `script.google.com`. See Grade 4 `STATUS.md` §7.
- [x] ~~Add the `"unit"` field to Week 3 Problem 4~~ — done 2026-09-17, with the ruler fix (§3).
- [ ] **Mirror Grade 4's class-progress board** here once it is proven there — a collective,
      non-competitive board (took part × got right = collected) driven by a `Roster` tab in the
      Sheet. See Grade 4 `STATUS.md` §5b.
- [ ] (Optional) purge `weeks/grade1/week2/week2_solution.pages` from git history if the old commits matter.

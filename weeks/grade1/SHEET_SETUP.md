# Backend setup — Google Sheet + Apps Script (one time, ~10 min)

One script + one Sheet does everything: it **saves** each student's answers and **serves**
the scored leaderboard. The answer key lives in the Sheet and never reaches a browser.

## 1. Create the Sheet
- <https://sheets.google.com> → blank spreadsheet → name it `Math Challenge`.
- Add a tab named **`AnswerKey`** (rename "Sheet1" or insert a new tab) with this header row:

  | Week | Answer 1 | Answer 2 | Answer 3 |
  |------|----------|----------|----------|
  | Grade 4 — Week 2 | 9 | _(B/C/D…)_ | _(B/C/D…)_ |

  - The `Week` text must match the page's label **exactly** (`Grade 4 — Week 2`).
  - Fill answers as students submit them: numbers for free-text, the letter for multiple choice.
  - The `Submissions` tab is created automatically on the first submission — don't make it by hand.

## 2. Add the script
- In the Sheet: **Extensions → Apps Script**.
- Delete the starter code, paste **all** of `apps_script_backend.gs` (this folder), **Save** 💾.

## 3. Deploy as a Web App
- **Deploy → New deployment** → gear ⚙ → **Web app**.
- **Execute as:** *Me*  ·  **Who has access:** *Anyone*  (required: students aren't logged in).
- **Deploy** → authorize (your account → Advanced → "Go to … (unsafe)" → Allow — it's your own script).
- Copy the **Web app URL** (ends in `/exec`).
- Sanity check: open that URL in a browser — you should see `{"ok":true,...}`.

## 4. Wire the URL into the pages
Paste the `/exec` URL into the `ENDPOINT_URL = ""` line in **all three** places:
- `weeks/grade4/week2/grade4_week2.html`  (so submissions save)
- `weeks/grade4/week2/_build.py`           (so a rebuild keeps the URL)
- `weeks/grade4/leaderboard.html`          (so the board can read scores)

## 5. Test
- Open `grade4_week2.html`, submit a name + answers → a row appears in `Submissions`.
- Open `leaderboard.html` → your score shows (if you chose "show my name"); private names
  appear only via **Find my rank**.

## Updating the script later
**Deploy → Manage deployments → Edit ✏ → Version: New version** keeps the **same URL**.
A brand-new deployment makes a *new* URL (and you'd have to re-paste it everywhere).

## Notes
- **One URL for all weeks & the leaderboard.** Reuse it; the `Week` column separates weeks.
- **Privacy:** the form defaults to **Private**; private students are hidden from the public
  board but can self-check via "Find my rank". Latest submission sets a student's name + choice.
- **Scoring:** 1 point per correct answer, compared case/space-insensitively. A week with no
  `AnswerKey` row just scores 0 until you fill it in.
- **One submission per student:** not enforced — re-submits add rows; the leaderboard uses each
  student's **latest** submission per week.

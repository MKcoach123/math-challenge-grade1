#!/usr/bin/env python3
"""
Reusable weekly page generator for the Math Challenge.

Each week lives in   weeks/grade1/weekN/   with:
  - week.json                  ← the week's definition (label, due, problems[])
  - source_images/*.png        ← any problem images referenced by week.json
The generator embeds the images as base64 and writes  grade1_weekN.html.
It also rebuilds the week cards on the site's home page (index.html).

Usage:
  python3 build_week.py weeks/grade1/week3     # build that week, then refresh index
  python3 build_week.py --all                  # rebuild every week + index
  python3 build_week.py --index                # only rebuild index.html

week.json shape:
{
  "number": 3,
  "week_label": "Grade 1 — Week 3",     // MUST match the AnswerKey tab's Week cell
  "due": "Sunday night",
  "problems": [
    { "type": "number", "text": "....", "unit": "squares" },
    { "type": "text",   "text": "....", "label": "Triangle digit:", "image": "p3.png" },
    { "type": "choice", "text": "....", "image": "p2.png", "choices": ["A","B","C","D","E"] }
  ]
}
Problem types: "number"/"text" → free-text box; "choice" → A–E radio chips.
"image" is optional on any problem.
"""
import base64, json, pathlib, sys, html as _html

ENDPOINT_URL = ""  # TODO: paste the Grade 1 Apps Script Web App /exec URL after deploying (see SHEET_SETUP.md)
ACCENTS = ["#4f46e5", "#0891b2", "#7c3aed", "#db2777", "#ea580c", "#16a34a"]  # per-problem accents (up to 6)
WEEK_COLORS = ["#4f46e5", "#0891b2", "#7c3aed", "#db2777", "#ea580c", "#16a34a", "#0284c7", "#9333ea"]
EMOJI = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","⭐","🏁"]  # 1–10 keycaps; 11 = ⭐; 12 = 🏁 finish flag (final week)

GRADE_DIR = pathlib.Path(__file__).parent
REPO_ROOT = GRADE_DIR.parent.parent
INDEX = REPO_ROOT / "index.html"

# ── Scribble / scratchpad overlay (a draw-on-the-page canvas). Plain strings so their braces
# stay literal when dropped into the render_week f-string. ───────────────────────────────────
SCRIBBLE_CSS = """
#scribble-canvas, #scribble-live { position: absolute; top: 0; left: 0; pointer-events: none; }
#scribble-canvas { z-index: 50; }
#scribble-live { z-index: 51; opacity: 0.2; }
#scribble-canvas.active { pointer-events: auto; touch-action: none; cursor: crosshair; }
#scribble-bar { position: fixed; right: 16px; bottom: 16px; z-index: 100; display: flex; align-items: center; gap: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,.18); padding: 8px 10px; }
#scribble-bar button { border: none; background: #f1f5f9; border-radius: 8px; padding: 8px 11px; font-size: 16px; cursor: pointer; line-height: 1; }
#scribble-bar button:hover { background: #e2e8f0; }
#scribble-bar .sc-toggle { font-weight: 700; font-size: 14px; white-space: nowrap; }
#scribble-bar .sc-toggle.on { background: #4f46e5; color: #fff; }
#scribble-bar .sc-tools { display: none; align-items: center; gap: 6px; }
#scribble-bar.open .sc-tools { display: flex; }
#scribble-bar .sc-color { width: 22px; height: 22px; border-radius: 50%; padding: 0; box-shadow: 0 0 0 1px #cbd5e1; }
#scribble-bar .sc-color.sel { box-shadow: 0 0 0 2px #1e293b; }
#scribble-bar button.sel { outline: 2px solid #4f46e5; }
/* Keep answer controls clickable above the scribble canvas (so tapping them works & exits scribble) */
.name-box input, .answer-area input, .choice, .btn-submit, .vis-opt { position: relative; z-index: 60; }
@media print { #scribble-canvas, #scribble-live, #scribble-bar { display: none !important; } }
"""

SCRIBBLE_HTML = """
<canvas id="scribble-canvas"></canvas>
<canvas id="scribble-live"></canvas>
<div id="scribble-bar">
  <button class="sc-toggle" id="scToggle" title="Draw / scribble on the page">✏️ Scribble</button>
  <div class="sc-tools">
    <button class="sc-color sel" data-color="#2563eb" style="background:#2563eb" title="Blue"></button>
    <button class="sc-color" data-color="#111827" style="background:#111827" title="Black"></button>
    <button class="sc-color" data-color="#dc2626" style="background:#dc2626" title="Red"></button>
    <button class="sc-color" data-color="#16a34a" style="background:#16a34a" title="Green"></button>
    <button id="scHl" title="Highlighter">\U0001f58d️</button>
    <button id="scErase" title="Eraser">\U0001f9fd</button>
    <button id="scClear" title="Clear everything">\U0001f5d1️</button>
  </div>
</div>
"""

SCRIBBLE_JS = """
(function () {
  var canvas = document.getElementById('scribble-canvas');
  var ctx = canvas.getContext('2d');
  var live = document.getElementById('scribble-live');
  var lctx = live.getContext('2d');
  var bar = document.getElementById('scribble-bar');
  var toggle = document.getElementById('scToggle');
  var active = false, drawing = false, tool = 'pen', color = '#2563eb', last = null;
  var HL_ALPHA = 0.2;   // keep in sync with #scribble-live CSS opacity

  function sizeCanvas() {
    var w = Math.max(document.documentElement.scrollWidth, window.innerWidth);
    var h = Math.max(document.documentElement.scrollHeight, window.innerHeight);
    if (canvas.width === w && canvas.height === h) return;
    var prev = null;
    if (canvas.width && canvas.height) { try { prev = ctx.getImageData(0, 0, canvas.width, canvas.height); } catch (e) {} }
    canvas.width = w; canvas.height = h;
    live.width = w; live.height = h;
    if (prev) ctx.putImageData(prev, 0, 0);
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    lctx.lineCap = 'round'; lctx.lineJoin = 'round';
  }
  sizeCanvas();
  window.addEventListener('load', sizeCanvas);
  window.addEventListener('resize', sizeCanvas);

  function setActive(on) {
    active = on;
    canvas.classList.toggle('active', on);
    bar.classList.toggle('open', on);
    toggle.classList.toggle('on', on);
    toggle.textContent = on ? '✏️ Scribbling' : '✏️ Scribble';
  }
  toggle.addEventListener('click', function () { sizeCanvas(); setActive(!active); });

  var colorBtns = bar.querySelectorAll('.sc-color');
  var hlBtn = document.getElementById('scHl');
  var eraseBtn = document.getElementById('scErase');
  function clearSel() { colorBtns.forEach(function (x) { x.classList.remove('sel'); }); hlBtn.classList.remove('sel'); eraseBtn.classList.remove('sel'); }
  colorBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      tool = 'pen'; color = b.getAttribute('data-color');
      clearSel(); b.classList.add('sel');
    });
  });
  hlBtn.addEventListener('click', function () { tool = 'highlighter'; clearSel(); hlBtn.classList.add('sel'); });
  eraseBtn.addEventListener('click', function () { tool = 'eraser'; clearSel(); eraseBtn.classList.add('sel'); });
  document.getElementById('scClear').addEventListener('click', function () {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    lctx.clearRect(0, 0, live.width, live.height);
  });

  // Young students: tapping an answer box should turn scribbling OFF so they can type.
  document.addEventListener('focusin', function (e) {
    if (active && e.target && e.target.matches && e.target.matches('input, textarea')) setActive(false);
  });

  canvas.addEventListener('pointerdown', function (e) {
    if (!active) return;
    drawing = true; last = { x: e.pageX, y: e.pageY };
    try { canvas.setPointerCapture(e.pointerId); } catch (err) {}
  });
  canvas.addEventListener('pointermove', function (e) {
    if (!active || !drawing) return;
    var x = e.pageX, y = e.pageY;
    if (tool === 'highlighter') {
      // draw OPAQUE on the live layer; its CSS opacity gives a uniform highlight (no slow-draw build-up)
      lctx.globalCompositeOperation = 'source-over'; lctx.strokeStyle = 'rgb(250,204,21)'; lctx.lineWidth = 18;
      lctx.beginPath(); lctx.moveTo(last.x, last.y); lctx.lineTo(x, y); lctx.stroke();
    } else if (tool === 'eraser') {
      ctx.globalCompositeOperation = 'destination-out'; ctx.lineWidth = 26;
      ctx.beginPath(); ctx.moveTo(last.x, last.y); ctx.lineTo(x, y); ctx.stroke();
    } else {
      ctx.globalCompositeOperation = 'source-over'; ctx.strokeStyle = color; ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(last.x, last.y); ctx.lineTo(x, y); ctx.stroke();
    }
    last = { x: x, y: y };
  });
  function endStroke() {
    if (drawing && tool === 'highlighter') {
      // bake the uniform live stroke onto the main canvas at the same alpha, then clear the live layer
      ctx.globalCompositeOperation = 'source-over';
      ctx.globalAlpha = HL_ALPHA;
      ctx.drawImage(live, 0, 0);
      ctx.globalAlpha = 1;
      lctx.clearRect(0, 0, live.width, live.height);
    }
    drawing = false;
  }
  canvas.addEventListener('pointerup', endStroke);
  canvas.addEventListener('pointercancel', endStroke);
  canvas.addEventListener('pointerleave', endStroke);
})();
"""


def b64_img(week_dir, name):
    data = (week_dir / "source_images" / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


def esc(s):
    return _html.escape(str(s), quote=True)


# ── CSS (kept in sync with the look of week1/week2) ──────────────────────────
def css():
    accent_nth = "\n".join(
        f".problem:nth-child({i+1}) {{ border-left-color: {c}; }}\n"
        f".problem:nth-child({i+1}) .problem-num {{ color: {c}; }}\n"
        f".problem:nth-child({i+1}) .choice input:checked + span {{ background: {c}; border-color: {c}; }}"
        for i, c in enumerate(ACCENTS)
    )
    return f"""* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Segoe UI', system-ui, Arial, sans-serif; background: #f0f4ff; padding: 24px 16px 48px; color: #1e293b; }}
.page {{ max-width: 860px; margin: 0 auto; }}

.topnav {{ display: flex; gap: 10px; margin-bottom: 16px; flex-wrap: wrap; }}
.topnav a {{ display: inline-flex; align-items: center; gap: 6px; text-decoration: none; color: #4f46e5; font-weight: 700; font-size: 15px; padding: 8px 16px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,.06); transition: transform .15s, box-shadow .15s; }}
.topnav a:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,.1); }}
.topnav a.lb {{ color: #b45309; }}

.header {{ background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white; border-radius: 16px; padding: 28px 36px; margin-bottom: 28px; box-shadow: 0 6px 24px rgba(30,64,175,.3); }}
.header h1 {{ font-size: 32px; font-weight: 900; letter-spacing: -.5px; }}
.header .sub {{ font-size: 16px; opacity: .85; margin-top: 6px; }}
.header .week-info {{ display: flex; gap: 24px; margin-top: 14px; font-size: 14px; opacity: .9; }}
.header .week-info span {{ background: rgba(255,255,255,.18); border-radius: 8px; padding: 4px 12px; }}

.name-box {{ background: white; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 2px 10px rgba(0,0,0,.08); display: flex; align-items: center; gap: 16px; }}
.name-box label {{ font-weight: 700; font-size: 16px; white-space: nowrap; }}
.name-box input {{ flex: 1; border: 2px solid #c7d2fe; border-radius: 8px; padding: 10px 14px; font-size: 16px; outline: none; transition: border-color .2s; }}
.name-box input:focus {{ border-color: #4f46e5; }}

.problem {{ background: white; border-radius: 16px; padding: 28px 32px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,.08); border-left: 6px solid #4f46e5; }}
{accent_nth}
.problem-num {{ font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; color: #4f46e5; margin-bottom: 10px; }}
.problem-text {{ font-size: 17px; line-height: 1.5; margin: 6px 0 4px; }}
.hint-toggle {{ display: inline-block; cursor: pointer; font-size: 13px; font-weight: 700; color: #b45309; background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 2px 10px; user-select: none; white-space: nowrap; }}
.hint-toggle:hover {{ background: #fef3c7; }}
.hint-text {{ font-style: italic; color: #64748b; }}
.problem img {{ max-width: 100%; border-radius: 8px; margin: 16px 0; border: 1px solid #e2e8f0; }}

.answer-area {{ margin-top: 18px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }}
.answer-label {{ font-weight: 700; font-size: 16px; }}
.answer-area input[type=text] {{ width: 120px; border: 2.5px solid #c7d2fe; border-radius: 8px; padding: 10px 14px; font-size: 18px; font-weight: 700; text-align: center; outline: none; transition: border-color .2s; }}
.answer-area input[type=text]:focus {{ border-color: #4f46e5; }}
.unit {{ font-size: 14px; color: #64748b; }}

.choices {{ gap: 12px; }}
.choice {{ display: inline-flex; cursor: pointer; }}
.choice input {{ position: absolute; opacity: 0; width: 0; height: 0; }}
.choice span {{ display: inline-flex; align-items: center; justify-content: center; width: 46px; height: 46px; border-radius: 50%; border: 2.5px solid #c7d2fe; font-size: 19px; font-weight: 800; color: #475569; user-select: none; transition: background .15s, border-color .15s, color .15s, box-shadow .15s; }}
.choice.pill span {{ width: auto; height: auto; border-radius: 999px; padding: 11px 26px; font-size: 17px; }}
.choice:hover span {{ border-color: #94a3b8; }}
.choice input:checked + span {{ background: #4f46e5; border-color: #4f46e5; color: #fff; box-shadow: 0 3px 10px rgba(79,70,229,.4); }}
.choice input:focus-visible + span {{ outline: 2px solid #4f46e5; outline-offset: 2px; }}

.visibility-box {{ background: #fffbeb; border: 2px solid #fcd34d; border-radius: 14px; padding: 18px 22px; margin-bottom: 24px; }}
.visibility-box .vq {{ font-weight: 800; font-size: 17px; color: #92400e; margin-bottom: 12px; display: block; }}
.vis-options {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.vis-opt {{ flex: 1; min-width: 230px; display: flex; align-items: center; gap: 11px; background: #fff; border: 2px solid #e2e8f0; border-radius: 12px; padding: 12px 16px; cursor: pointer; transition: border-color .15s, box-shadow .15s, background .15s; }}
.vis-opt:hover {{ border-color: #cbd5e1; }}
.vis-opt input {{ width: 20px; height: 20px; accent-color: #f59e0b; cursor: pointer; flex: none; }}
.vis-opt .vo-emoji {{ font-size: 22px; line-height: 1; }}
.vis-opt .vo-title {{ font-weight: 700; font-size: 15px; }}
.vis-opt .vo-sub {{ font-size: 12.5px; color: #64748b; }}
.vis-opt:has(input:checked) {{ border-color: #f59e0b; background: #fffdf5; box-shadow: 0 2px 10px rgba(245,158,11,.3); }}

.submit-row {{ text-align: center; margin-top: 8px; }}
.btn-submit {{ background: linear-gradient(135deg, #1d4ed8, #4f46e5); color: white; border: none; border-radius: 12px; padding: 16px 48px; font-size: 18px; font-weight: 800; cursor: pointer; box-shadow: 0 4px 16px rgba(79,70,229,.4); transition: transform .15s, box-shadow .15s; }}
.btn-submit:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(79,70,229,.5); }}
.btn-submit:active {{ transform: translateY(0); }}
.btn-submit:disabled {{ opacity: .6; cursor: default; transform: none; box-shadow: none; }}

.print-btn {{ background: rgba(255,255,255,.16); border: 1.5px solid rgba(255,255,255,.65); border-radius: 8px; padding: 8px 18px; font-size: 14px; font-weight: 600; color: #fff; cursor: pointer; float: right; margin-top: 4px; transition: background .2s, border-color .2s; }}
.print-btn:hover {{ background: rgba(255,255,255,.30); border-color: #fff; }}

@media print {{
  @page {{ size: A4 portrait; margin: 12mm 14mm; }}
  html, body {{ background: white !important; padding: 0 !important; margin: 0 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  .page {{ max-width: 100%; margin: 0; }}
  input::placeholder {{ color: transparent !important; opacity: 0 !important; }}
  input::-webkit-input-placeholder {{ color: transparent !important; opacity: 0 !important; }}
  .topnav {{ display: none !important; }}
  .header {{ background: none !important; color: black !important; border-radius: 0 !important; box-shadow: none !important; padding: 0 0 7pt 0 !important; margin-bottom: 12pt !important; border-bottom: 2.5pt solid #1d4ed8; }}
  .header h1 {{ font-size: 19pt !important; letter-spacing: 0 !important; color: #1d4ed8 !important; }}
  .header .sub {{ font-size: 10.5pt !important; margin-top: 2pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info {{ display: flex !important; margin-top: 5pt !important; font-size: 10pt !important; gap: 18pt !important; opacity: 1 !important; color: #333 !important; }}
  .header .week-info span {{ background: none !important; padding: 0 !important; border-radius: 0 !important; }}
  .print-btn {{ display: none !important; }}
  .name-box {{ background: none !important; box-shadow: none !important; border-radius: 0 !important; border: none !important; padding: 0 !important; margin-bottom: 12pt !important; display: flex; align-items: baseline; gap: 8pt; }}
  .name-box label {{ font-size: 11pt !important; font-weight: 700 !important; white-space: nowrap; }}
  .name-box input {{ flex: 1; border: none !important; border-bottom: 1pt solid #444 !important; border-radius: 0 !important; font-size: 11pt !important; background: none !important; padding: 1pt 4pt !important; }}
  #quiz {{ display: block; }}
  .problem {{ background: none !important; box-shadow: none !important; border-radius: 0 !important; padding: 0 0 0 9pt !important; margin: 0 0 16pt 0 !important; border-left-width: 3.5pt !important; page-break-inside: avoid; break-inside: avoid; }}
  .problem:last-of-type {{ margin-bottom: 0 !important; }}
  .problem-num {{ font-size: 10pt !important; margin-bottom: 4pt !important; }}
  .problem-text {{ font-size: 11pt !important; line-height: 1.35 !important; margin: 2pt 0 4pt !important; }}
  .hint-toggle {{ display: none !important; }}
  .hint-text {{ display: inline !important; font-style: italic !important; color: #333 !important; }}
  .hint-text::before {{ content: "💡 Hint:"; font-style: normal; font-weight: 700; color: #000; }}
  .problem img {{ width: auto; max-width: var(--pw, var(--sw, 100%)) !important; max-height: 230pt !important; height: auto !important; margin: 4pt 0 6pt !important; border: none !important; display: block; }}
  .answer-area {{ margin-top: 6pt !important; gap: 12pt !important; }}
  .answer-label {{ font-size: 11pt !important; }}
  .answer-area input[type=text] {{ border: none !important; border-bottom: 1.5pt solid #333 !important; border-radius: 0 !important; font-size: 12pt !important; width: 90px !important; background: none !important; padding: 1pt 2pt !important; }}
  .unit {{ font-size: 10.5pt !important; }}
  .choices {{ gap: 14pt !important; }}
  .choice span {{ width: 22pt !important; height: 22pt !important; border: 1.25pt solid #333 !important; background: none !important; color: #000 !important; font-size: 12pt !important; box-shadow: none !important; }}
  .choice.pill span {{ width: auto !important; height: auto !important; border-radius: 4pt !important; padding: 4pt 12pt !important; }}
  .choice input:checked + span {{ background: none !important; color: #000 !important; border-color: #000 !important; }}
  .visibility-box {{ display: none !important; }}
  .submit-row {{ display: none !important; }}
}}"""


def render_problem(i, p, week_dir, img_max_width=None):
    n = i + 1
    parts = [f'    <div class="problem">', f'      <div class="problem-num">Problem {n}</div>']
    if p.get("html"):                         # raw HTML (e.g. inline SVG) — not escaped
        parts.append(f'      <p class="problem-text">{p["html"]}</p>')
    elif p.get("text"):
        parts.append(f'      <p class="problem-text">{esc(p["text"])}</p>')
    # One or more figures. Use "images": [{"file","width"}, …] for several; or a single "image".
    figs = p.get("images")
    if figs is None and p.get("image"):
        figs = [{"file": p["image"], "width": p.get("image_width"), "print_width": p.get("print_width")}]
    for fig in (figs or []):
        # screen width (--sw) overrides week-level "image_max_width"; optional print width (--pw).
        w = fig.get("width") or img_max_width
        pw = fig.get("print_width")
        sty = []
        if w: sty += [f"--sw:{esc(w)}", "max-width:var(--sw)"]
        if pw: sty.append(f"--pw:{esc(pw)}")
        style = f' style="{";".join(sty)}"' if sty else ""
        if fig.get("caption"):                # text rendered just before this figure
            parts.append(f'      <p class="problem-text">{esc(fig["caption"])}</p>')
        parts.append(f'      <img src="{b64_img(week_dir, fig["file"])}"{style} alt="Problem {n} figure">')

    ptype = p.get("type", "number")
    if ptype == "choice":
        choices = p.get("choices", ["A", "B", "C", "D", "E"])
        # Word choices (e.g. "Turns"/"Jammed") render as pills; single chars stay circles.
        cls = "choice pill" if any(len(str(c)) > 2 for c in choices) else "choice"
        chips = "\n".join(
            f'        <label class="{cls}"><input type="radio" name="a{n}" value="{esc(c)}"><span>{esc(c)}</span></label>'
            for c in choices
        )
        parts.append('      <div class="answer-area choices">')
        parts.append('        <span class="answer-label">My answer:</span>')
        parts.append(chips)
        parts.append('      </div>')
    else:
        label = p.get("label", "My answer:")
        unit = f'\n        <span class="unit">{esc(p["unit"])}</span>' if p.get("unit") else ""
        ml = p.get("maxlength", 6)
        parts.append('      <div class="answer-area">')
        parts.append(f'        <span class="answer-label">{esc(label)}</span>')
        parts.append(f'        <input type="text" id="a{n}" name="a{n}" placeholder="?" maxlength="{ml}" autocomplete="off">{unit}')
        parts.append('      </div>')

    parts.append('    </div>')
    return "\n".join(parts)


def render_week(week_dir, cfg):
    problems = cfg["problems"]
    num = len(problems)
    title = cfg.get("title", cfg["week_label"])
    due = cfg.get("due", "Sunday night")
    img_max_width = cfg.get("image_max_width")   # week-level default cap for figures, e.g. "280px"
    problems_html = "\n\n".join(render_problem(i, p, week_dir, img_max_width) for i, p in enumerate(problems))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<style>
{css()}
{SCRIBBLE_CSS}
</style>
</head>
<body>
<div class="page">

  <div class="topnav">
    <a href="../../../index.html">← Home</a>
    <a class="lb" href="../leaderboard.html">\U0001f3c6 Leaderboard</a>
  </div>

  <div class="header">
    <button class="print-btn" onclick="window.print()">\U0001f5a8 Print</button>
    <h1>{esc(title)}</h1>
    <div class="sub">Math Challenge Problems</div>
    <div class="week-info">
      <span>\U0001f4c5 Due: {esc(due)}</span>
      <span>\U0001f3c6 {num} problems · 1 point each</span>
    </div>
  </div>

  <div class="name-box">
    <label for="sname">Your name:</label>
    <input type="text" id="sname" placeholder="First name Last initial" autocomplete="off">
  </div>

  <form id="quiz">

{problems_html}

    <div class="visibility-box">
      <span class="vq">🏆 Show your name on the class leaderboard?</span>
      <div class="vis-options">
        <label class="vis-opt">
          <input type="radio" name="display" value="Private" checked>
          <span class="vo-emoji">🔒</span>
          <span><span class="vo-title">No, keep me private</span><br><span class="vo-sub">Hidden from classmates · find your own rank by name</span></span>
        </label>
        <label class="vis-opt">
          <input type="radio" name="display" value="Public">
          <span class="vo-emoji">✅</span>
          <span><span class="vo-title">Yes, show my name</span><br><span class="vo-sub">Classmates will see your name &amp; score</span></span>
        </label>
      </div>
    </div>

    <div class="submit-row">
      <button type="button" class="btn-submit" onclick="submitAnswers(this)">Submit Answers ✓</button>
    </div>

  </form>

</div>
{SCRIBBLE_HTML}
<script>
const ENDPOINT_URL = "{ENDPOINT_URL}";
const WEEK_LABEL = "{esc(cfg['week_label'])}";
const NUM_PROBLEMS = {num};

async function submitAnswers(btn) {{
  const name = document.getElementById('sname').value.trim();
  if (!name) {{ alert('Please enter your name first!'); return; }}

  const answers = {{}};
  for (let i = 1; i <= NUM_PROBLEMS; i++) {{
    const radio = document.querySelector('input[name="a' + i + '"]:checked');
    if (radio) {{ answers['a' + i] = radio.value; continue; }}
    const box = document.getElementById('a' + i);
    answers['a' + i] = box ? box.value.trim() : '';
  }}
  for (let i = 1; i <= NUM_PROBLEMS; i++) {{
    if (!answers['a' + i]) {{ alert('Please answer all ' + NUM_PROBLEMS + ' problems before submitting.'); return; }}
  }}

  const display = (document.querySelector('input[name="display"]:checked') || {{}}).value || 'Private';
  // Make the leaderboard-visibility choice an explicit, conscious decision before saving.
  const sure = (display === 'Public')
    ? confirm('You chose to SHOW YOUR NAME on the class leaderboard.\\nClassmates will see your name and score.\\n\\nSubmit your answers?')
    : confirm('You chose to stay PRIVATE.\\nYour name stays hidden from classmates (you can still look up your own rank by name).\\n\\nSubmit your answers?');
  if (!sure) return;

  const payload = Object.assign({{ week: WEEK_LABEL, name: name, display: display }}, answers);

  if (!ENDPOINT_URL) {{
    alert('Thanks ' + name + '! Your answers have been recorded.\\n\\n(No Sheet connected yet.)');
    return;
  }}

  const original = btn.textContent;
  btn.disabled = true; btn.textContent = 'Submitting…';
  try {{
    const res = await fetch(ENDPOINT_URL, {{ method: 'POST', headers: {{ 'Content-Type': 'text/plain;charset=utf-8' }}, body: JSON.stringify(payload) }});
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Save failed');
    alert('Thanks ' + name + '! Your answers have been recorded. ✓');
  }} catch (e) {{
    alert('Sorry — something went wrong saving your answers.\\nPlease tell your teacher.\\n\\n(' + e.message + ')');
  }} finally {{
    btn.disabled = false; btn.textContent = original;
  }}
}}
</script>
<script>{SCRIBBLE_JS}</script>
</body>
</html>
"""


def build_week(week_dir):
    week_dir = pathlib.Path(week_dir).resolve()
    cfg = json.loads((week_dir / "week.json").read_text())
    if not cfg.get("problems"):
        print(f"  (skip {week_dir.name}: metadata only, no problems[])")
        return cfg
    n = cfg.get("number") or int("".join(filter(str.isdigit, week_dir.name)))
    out = week_dir / f"grade1_week{n}.html"
    out.write_text(render_week(week_dir, cfg))
    try:
        shown = out.relative_to(REPO_ROOT)
    except ValueError:
        shown = out
    print(f"  built {shown} ({len(cfg['problems'])} problems)")
    return cfg


def all_weeks():
    dirs = sorted([d for d in GRADE_DIR.glob("week*") if (d / "week.json").exists()],
                  key=lambda d: int("".join(filter(str.isdigit, d.name)) or 0))
    return dirs


def rebuild_index():
    cards = []
    for d in all_weeks():
        cfg = json.loads((d / "week.json").read_text())
        n = cfg.get("number") or int("".join(filter(str.isdigit, d.name)))
        html_name = cfg.get("html", f"grade1_week{n}.html")
        nprob = len(cfg.get("problems", [])) or cfg.get("num_problems", 3)
        color = WEEK_COLORS[(n - 1) % len(WEEK_COLORS)]
        emoji = EMOJI[(n - 1) % len(EMOJI)]

        # Optional Solutions button. Gated: shown disabled until "solutions_available" is true
        # (flip it to true after the week's deadline, then rebuild + push).
        sol = cfg.get("solutions")
        sol_btn = ""
        if sol:
            href = f"weeks/grade1/week{n}/{sol}"
            # Both states link to the page; when not yet available it shows a passcode gate.
            if cfg.get("solutions_available"):
                sol_btn = f'\n    <a class="sol-btn" href="{href}">📖 Solutions</a>'
            else:
                sol_btn = f'\n    <a class="sol-btn" href="{href}" title="Teacher/developer passcode required">🔒 Solutions</a>'

        cards.append(
            f'  <div class="week-card" style="border-left-color:{color}">\n'
            f'    <a class="week-link" href="weeks/grade1/week{n}/{html_name}">\n'
            f'      <span class="emoji">{emoji}</span>\n'
            f'      <span class="text">\n'
            f'        <span class="title">Week {n}</span>\n'
            f'        <span class="desc">Grade 1 · {nprob} problems</span>\n'
            f'      </span>\n'
            f'    </a>{sol_btn}\n'
            f'  </div>'
        )
    text = INDEX.read_text()
    start = "<!-- WEEKS:START (auto-generated by build_week.py — do not edit between these markers) -->"
    end = "<!-- WEEKS:END -->"
    a, b = text.index(start), text.index(end)
    new = text[:a] + start + "\n" + "\n".join(cards) + "\n  " + text[b:]
    INDEX.write_text(new)
    print(f"  index.html: {len(cards)} week cards")


def update_leaderboard_weeks():
    """Keep leaderboard.html's ALL_WEEKS list in sync with the weeks that exist."""
    lb = GRADE_DIR / "leaderboard.html"
    labels = [json.loads((d / "week.json").read_text())["week_label"] for d in all_weeks()]
    text = lb.read_text()
    start, end = "/* WEEKS:START */", "/* WEEKS:END */"
    a, b = text.index(start) + len(start), text.index(end)
    js = "\n  " + ", ".join(json.dumps(l, ensure_ascii=False) for l in labels) + "\n  "
    lb.write_text(text[:a] + js + text[b:])
    print(f"  leaderboard.html: {len(labels)} weeks listed")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return
    if argv[0] == "--index":
        rebuild_index(); update_leaderboard_weeks(); return
    if argv[0] == "--all":
        for d in all_weeks():
            build_week(d)
        rebuild_index(); update_leaderboard_weeks(); return
    build_week(argv[0])
    rebuild_index(); update_leaderboard_weeks()


if __name__ == "__main__":
    main(sys.argv[1:])

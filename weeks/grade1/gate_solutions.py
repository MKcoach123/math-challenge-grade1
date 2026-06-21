#!/usr/bin/env python3
"""
Put a lightweight passcode gate on each solution page.

Usage:  python3 gate_solutions.py <PASSCODE_DEV> <PASSCODE_TEACHER>

On every visit the page shows a passcode screen; entering either passcode reveals
the solutions for that one viewing (going back + clicking again re-asks). Whether a
week is gated is taken from its week.json "solutions_available" flag: false → gated,
true → revealed (no passcode, e.g. after the deadline).

Only the SHA-256 hashes of the passcodes are written into the pages — not the
passcodes themselves. Re-run this after editing a solution page (it strips and
re-injects its own markers, so it's safe to run repeatedly).
"""
import sys, re, json, hashlib, pathlib

GRADE_DIR = pathlib.Path(__file__).parent

CSS = (
  '<style id="sol-gate-css">'
  '#sol-gate{position:fixed;inset:0;background:#f0f4ff;display:flex;align-items:center;justify-content:center;'
  'padding:24px;z-index:99999;font-family:\'Segoe UI\',system-ui,Arial,sans-serif}'
  '#sol-gate .box{background:#fff;border-radius:18px;box-shadow:0 8px 30px rgba(30,64,175,.18);padding:34px 32px;max-width:400px;width:100%;text-align:center}'
  '#sol-gate input{flex:1;border:2px solid #c7d2fe;border-radius:10px;padding:11px 14px;font-size:18px;text-align:center;letter-spacing:.15em;outline:none}'
  '#sol-gate input:focus{border-color:#4f46e5}'
  '#sol-gate button{border:none;background:linear-gradient(135deg,#1d4ed8,#4f46e5);color:#fff;font-weight:800;font-size:15px;border-radius:10px;padding:11px 20px;cursor:pointer}'
  'body.sol-locked .page{display:none!important}'
  '@media print{#sol-gate{display:none!important}}'
  '</style>'
)

GATE_HTML = (
  '<!--SOLGATE--><div id="sol-gate"><div class="box">'
  '<div style="font-size:44px">&#128274;</div>'
  '<h2 style="font-size:21px;font-weight:900;margin:6px 0 4px">Solutions are locked</h2>'
  '<p style="font-size:14px;color:#64748b;margin-bottom:18px">Enter the teacher or developer passcode.</p>'
  '<form onsubmit="return solUnlock(event)"><div style="display:flex;gap:10px">'
  '<input id="sol-pc" type="password" inputmode="numeric" placeholder="Passcode" autocomplete="off" autofocus>'
  '<button type="submit">Open</button></div>'
  '<div id="sol-err" style="color:#b91c1c;font-size:13px;font-weight:600;margin-top:12px;min-height:16px"></div></form>'
  '<a href="../../../index.html" style="display:inline-block;margin-top:14px;font-size:13px;color:#94a3b8;text-decoration:none">&larr; Back to home</a>'
  '</div></div><!--/SOLGATE-->'
)

def script(revealed, hashes):
    return (
      '<script id="sol-gate-js">'
      'const SOL_REVEALED=' + ('true' if revealed else 'false') + ';'
      'const SOL_HASHES=' + json.dumps(hashes) + ';'
      'async function solSha(s){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));'
      'return Array.from(new Uint8Array(b)).map(x=>x.toString(16).padStart(2,"0")).join("")}'
      'function solReveal(){document.body.classList.remove("sol-locked");var g=document.getElementById("sol-gate");if(g)g.style.display="none";}'
      'async function solUnlock(e){e.preventDefault();var err=document.getElementById("sol-err");err.textContent="";'
      'var h=await solSha(document.getElementById("sol-pc").value.trim());'
      'if(SOL_HASHES.indexOf(h)>=0){solReveal();}else{err.textContent="Wrong passcode — try again.";'
      'var i=document.getElementById("sol-pc");i.value="";i.focus();}return false;}'
      'if(SOL_REVEALED){solReveal();}'
      '</script>'
    )

def strip(html):
    html = re.sub(r'<style id="sol-gate-css">.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<!--SOLGATE-->.*?<!--/SOLGATE-->', '', html, flags=re.S)
    html = re.sub(r'<script id="sol-gate-js">.*?</script>', '', html, flags=re.S)
    html = html.replace('<body class="sol-locked">', '<body>')
    return html

def inject(html, revealed, hashes):
    html = strip(html)
    html = html.replace('</head>', CSS + '\n</head>', 1)
    html = html.replace('<body>', '<body class="sol-locked">\n' + GATE_HTML, 1)
    html = html.replace('</body>', script(revealed, hashes) + '\n</body>', 1)
    return html

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    hashes = [hashlib.sha256(p.encode()).hexdigest() for p in sys.argv[1:3]]
    for wd in sorted(GRADE_DIR.glob("week*")):
        sols = list(wd.glob("solutions_week*.html"))
        if not sols:
            continue
        cfg = json.loads((wd / "week.json").read_text()) if (wd / "week.json").exists() else {}
        revealed = bool(cfg.get("solutions_available"))
        f = sols[0]
        f.write_text(inject(f.read_text(), revealed, hashes))
        print(f"gated {wd.name}/{f.name}  (revealed={revealed})")

if __name__ == "__main__":
    main()

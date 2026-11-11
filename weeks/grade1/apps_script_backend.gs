/**
 * Math Challenge — backend (Google Apps Script Web App)
 *
 * One script + one Sheet powers everything:
 *   • doPost  — receives a student's answers, appends a row to "Submissions"
 *   • doGet   — grades submissions against "AnswerKey" and returns ranked JSON
 *               for the leaderboard page (cumulative, per-week, and self-lookup)
 *
 * Sheet tabs (see SHEET_SETUP.md):
 *   Submissions : Timestamp | Week | Name | Display | Answer 1 | Answer 2 | Answer 3
 *   AnswerKey   : Week | Answer 1 | Answer 2 | Answer 3
 *
 * The answer key stays server-side — it is never sent to a browser.
 */

var SUBMISSIONS = 'Submissions';
var ANSWER_KEY  = 'AnswerKey';
var MAX_PROBLEMS = 6;   // supports 3–6 problems/week; AnswerKey/Submissions use Answer 1..6
var SUB_HEADER  = ['Timestamp', 'Week', 'Name', 'Display']
  .concat(answerCols());  // -> ... 'Answer 1' .. 'Answer 6'

function answerCols() {
  var cols = [];
  for (var i = 1; i <= MAX_PROBLEMS; i++) cols.push('Answer ' + i);
  return cols;
}

/* ───────────────────────── Name filter (copied from name_filter.js by build_week.py) ───────────────────────── */

/* NAME_FILTER:START */
// Blocks rude or unkind words in student names. The same code runs on the page (instant
// message) and in the backend (can't be bypassed). Lists are rot13 so they don't read
// plainly in the page source. Edit name_filter.js, then run build_week.py --all.
var BLOCKED_WORDS = 'nefr nefrubyr nff nffubyr onfgneq ovgpu ovgpurf ovgpul obyybpxf obbo obbof ohyyfuvg ohgg ohggsnpr ohggurnq ohggubyr pbpx penc pencsnpr penccl phag qnzzvg qnza qvpx qvpxurnq qvyqb qbhpur qbhpuront qhzo qhzonff qhzob snt sntf sneg snegf shpx shpxre shpxsnpr shpxvat uryy vqvbg vqvbgf wnpxnff wrex xvyy xvyyre ybfre ybfref zbeba anmv avttn avttre cravf cvff cvffrq cbbc cbbcurnq cbbcl cbea chffl ergneq ergneqrq frk frkl fuvg fuvgurnq fuvgf fuvggl fyhg fyhgf fgsh fgvaxl fghcvq fgbbcvq fhpx fhpxf gjng intvan jnaxre juber jgs';
var BLOCKED_INSIDE = 'nffubyr ovgpu phag qvpxurnq snttbg shpx avttn avttre fuvgurnq juber';

function isRudeName(name) {
  function rot13(s) { return s.replace(/[a-z]/g, function (c) { return String.fromCharCode((c.charCodeAt(0) - 84) % 26 + 97); }); }
  var words = rot13(BLOCKED_WORDS).split(' '), inside = rot13(BLOCKED_INSIDE).split(' ');
  var s = String(name || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/[0]/g, 'o').replace(/[1!|]/g, 'i').replace(/3/g, 'e').replace(/[4@]/g, 'a')
    .replace(/[5$]/g, 's').replace(/7/g, 't');
  var tokens = s.split(/[^a-z]+/).filter(Boolean);
  // Spelled out with gaps ("b a d") — join runs of single letters into one word.
  var joined = s.replace(/\b([a-z])[^a-z]+(?=[a-z]\b)/g, '$1').split(/[^a-z]+/).filter(Boolean);
  var all = tokens.concat(joined);
  for (var i = 0; i < all.length; i++) {
    var t = all[i], forms = [t, t.replace(/(.)\1\1+/g, '$1$1'), t.replace(/(.)\1+/g, '$1')];
    forms.push(forms[1].replace(/e?s$/, ''));
    for (var j = 0; j < forms.length; j++) {
      if (words.indexOf(forms[j]) >= 0) return true;
      for (var k = 0; k < inside.length; k++) if (forms[j].indexOf(inside[k]) >= 0) return true;
    }
  }
  return false;
}
/* NAME_FILTER:END */

/* ───────────────────────── Write: receive a submission ───────────────────────── */

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.tryLock(10000); // serialize writes so rows don't collide
  try {
    var data = JSON.parse(e.postData.contents);
    if (isRudeName(data.name)) return json({ ok: false, rude: true });

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SUBMISSIONS) || ss.insertSheet(SUBMISSIONS);
    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, SUB_HEADER.length).setValues([SUB_HEADER]);
      sheet.setFrozenRows(1);
    } else if (sheet.getLastColumn() < SUB_HEADER.length) {
      // Widen an older 3-answer sheet to Answer 1..6 (existing rows keep blanks).
      sheet.getRange(1, 1, 1, SUB_HEADER.length).setValues([SUB_HEADER]);
    }

    // Default to Private unless the student explicitly chose Public.
    var display = (norm(data.display) === 'public') ? 'Public' : 'Private';

    var row = [new Date(), data.week || '', data.name || '', display];
    for (var i = 1; i <= MAX_PROBLEMS; i++) row.push(data['a' + i] || '');
    sheet.appendRow(row);

    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/* ───────────────────────── Read: leaderboard / self-lookup ───────────────────────── */

function doGet(e) {
  try {
    var p = (e && e.parameter) || {};
    var view = p.view || 'leaderboard';

    if (view === 'findme') {
      return json(findRank(p.name, p.week));        // public students only — see findRank
    }
    if (view === 'debug') {
      return json(debugInfo());                     // inspect what the sheet parsing sees
    }
    // view === 'leaderboard'  (optionally scoped to ?week=...)
    return json(leaderboard(p.week));
  } catch (err) {
    return json({ ok: false, error: String(err) });
  }
}

/** Public leaderboard. weekLabel omitted/blank ⇒ cumulative across all weeks. */
function leaderboard(weekLabel) {
  var s = computeStandings(weekLabel);
  var rows = s.standings
    .filter(function (x) { return x.display === 'Public'; })
    .map(function (x) {
      return { rank: x.rank, name: x.name, points: x.points, weeksPlayed: x.weeksPlayed };
    });
  var hidden = s.standings.length - rows.length;
  return {
    ok: true,
    scope: weekLabel ? 'week' : 'cumulative',
    week: weekLabel || '',
    weeks: s.weeks,
    rows: rows,
    hiddenCount: hidden,
    totalStudents: s.standings.length
  };
}

/**
 * A single student's standing, for students who chose Public only. This endpoint
 * is open to anyone, so a name alone must never reveal a Private student's score;
 * they get the same "not found" as a name that never submitted.
 */
function findRank(name, weekLabel) {
  if (!name || !nameKey(name)) return { ok: true, found: false };
  var s = computeStandings(weekLabel);
  var key = nameKey(name);
  for (var i = 0; i < s.standings.length; i++) {
    if (s.standings[i].key === key && s.standings[i].display === 'Public') {
      var x = s.standings[i];
      return {
        ok: true, found: true, name: x.name, rank: x.rank,
        points: x.points, weeksPlayed: x.weeksPlayed,
        totalStudents: s.standings.length,
        scope: weekLabel ? 'week' : 'cumulative', week: weekLabel || ''
      };
    }
  }
  return { ok: true, found: false, totalStudents: s.standings.length };
}

/**
 * Core scoring. Returns { standings:[{key,name,points,weeksPlayed,display,rank}], weeks:[...] }
 * sorted by points desc then name, with competition ranks (ties share a rank).
 */
function computeStandings(weekLabel) {
  var key = getAnswerKey();                 // { normWeek: [a1,a2,a3] (normalized) }
  var subs = getRows(SUBMISSIONS);
  var wf = weekLabel ? norm(weekLabel) : null;

  // Latest submission per (student, week) wins.
  var latest = {};                          // "studentKey|weekKey" -> row
  var weeksSet = {};
  subs.forEach(function (r) {
    var wk = norm(r['Week']);
    if (!wk || !nameKey(r['Name'])) return;
    weeksSet[r['Week']] = true;          // record every week, independent of the filter
    if (wf && wk !== wf) return;
    var k = nameKey(r['Name']) + '|' + wk;
    var ts = new Date(r['Timestamp']).getTime() || 0;
    if (!latest[k] || ts >= latest[k]._ts) { r._ts = ts; r._wk = wk; latest[k] = r; }
  });

  // Aggregate per student.
  var byStudent = {};
  Object.keys(latest).forEach(function (k) {
    var r = latest[k];
    var sk = nameKey(r['Name']);
    var rec = byStudent[sk] || (byStudent[sk] = {
      key: sk, name: r['Name'], points: 0, weeksPlayed: 0, display: 'Private', _ts: -1
    });
    rec.weeksPlayed += 1;
    rec.points += scoreOne(r, key[r._wk]);
    if (r._ts >= rec._ts) {                 // newest submission sets the display name + privacy
      rec._ts = r._ts; rec.name = r['Name'];
      rec.display = (norm(r['Display']) === 'public') ? 'Public' : 'Private';
    }
  });

  var standings = Object.keys(byStudent).map(function (k) { return byStudent[k]; });
  standings.sort(function (a, b) {
    return b.points - a.points || a.name.localeCompare(b.name);
  });
  // Competition ranking (1,2,2,4,…)
  for (var i = 0; i < standings.length; i++) {
    standings[i].rank = (i > 0 && standings[i].points === standings[i - 1].points)
      ? standings[i - 1].rank : i + 1;
  }

  return { standings: standings, weeks: Object.keys(weeksSet).sort() };
}

/** Points for one submission vs the week's key (array of Answer 1..N). 1 point per correct answer. */
function scoreOne(row, keyArr) {
  if (!keyArr) return 0;                     // no key entered for this week yet
  var pts = 0;
  for (var i = 0; i < keyArr.length; i++) {
    if (keyArr[i] !== '' && norm(row['Answer ' + (i + 1)]) === keyArr[i]) pts++;
  }
  return pts;
}

/* ───────────────────────── helpers ───────────────────────── */

/**
 * Diagnostic: shows the tabs found, how many answers each week has, and distinct
 * submission weeks. This endpoint is public, so it must never return the answers.
 */
function debugInfo() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var tabs = ss.getSheets().map(function (s) { return s.getName(); });
  var keyMap = getAnswerKey();
  var subWeeks = {};
  getRows(SUBMISSIONS).forEach(function (r) { if (r['Week']) subWeeks[r['Week']] = (subWeeks[r['Week']] || 0) + 1; });
  return {
    ok: true,
    tabs: tabs,
    answerKeyHeaders: (getRows(ANSWER_KEY)[0] ? Object.keys(getRows(ANSWER_KEY)[0]) : []),
    answerCounts: Object.keys(keyMap).reduce(function (acc, w) { acc[w] = keyMap[w].length; return acc; }, {}),
    submissionWeeks: subWeeks,               // exact Week text -> count
    weekMatch: Object.keys(subWeeks).reduce(function (acc, w) { acc[w] = !!keyMap[norm(w)]; return acc; }, {})
  };
}

function getAnswerKey() {
  var map = {};
  getRows(ANSWER_KEY).forEach(function (r) {
    var wk = norm(r['Week']);
    if (!wk) return;
    var arr = [];
    for (var i = 1; i <= MAX_PROBLEMS; i++) arr.push(norm(r['Answer ' + i]));
    while (arr.length && arr[arr.length - 1] === '') arr.pop();  // trim unused trailing answers
    map[wk] = arr;
  });
  return map;
}

function getRows(sheetName) {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sh || sh.getLastRow() < 2) return [];
  var values = sh.getDataRange().getValues();
  var header = values.shift().map(function (h) { return String(h).trim(); });
  return values.map(function (row) {
    var o = {};
    header.forEach(function (h, i) { o[h] = row[i]; });
    return o;
  });
}

function norm(v) {
  return String(v == null ? '' : v)
    .replace(/[‒-―−]/g, '-')   // en/em dashes & minus → plain hyphen
    .trim().toLowerCase().replace(/\s+/g, ' ');
}

/**
 * Identity key for a student NAME (used only to group submissions into one person).
 * On top of norm() it drops periods/commas, so "John S", "john s." and "John S."
 * all collapse to the same student. Display still uses the raw, latest-typed name.
 * (Kept separate from norm() so answer matching is unaffected — e.g. a "2.5" answer.)
 */
function nameKey(v) {
  return norm(v).replace(/[.,]/g, '').replace(/\s+/g, ' ').trim();
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

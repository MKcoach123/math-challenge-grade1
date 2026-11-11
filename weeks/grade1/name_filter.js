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

(function () {
  var btn = document.querySelector('.mobile-menu-btn'), links = document.querySelector('.nav-links');
  if (btn && links) btn.addEventListener('click', function () { links.classList.toggle('open'); });
  var search = document.getElementById('tool-search'), grid = document.getElementById('filtered-tools');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.tool-card'));
  var noRes = document.getElementById('no-results'), state = { category: 'all', pricing: 'all', q: '', usage: 'medium', budget: 'any', commercial: 'all', format: 'all', platform: 'all' };
  var countEl = document.getElementById('results-count'), total = cards.length;
  var DEFAULTS = { category: 'all', pricing: 'all', usage: 'medium', budget: 'any', commercial: 'all', format: 'all', platform: 'all' };
  var browse = document.querySelectorAll('.section.browse');
  var FILTER_PARAMS = ['cat', 'q', 'pricing', 'weight', 'price', 'licence', 'format', 'platform'];
  var BUDGET_TO_PARAM = { '0': 'free', '10': 'under-10', '25': 'under-25', '50': 'under-50' };
  var PARAM_TO_BUDGET = { 'free': '0', 'under-10': '10', 'under-25': '25', 'under-50': '50', '0': '0', '10': '10', '25': '25', '50': '50' };
  var syncing = false;

  function slugify(v) {
    return String(v).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
  }
  function withinBudget(c) {
    if (state.budget === 'any') return true;
    var raw = c.getAttribute('data-spend-' + state.usage);
    if (raw === null || raw === '') return false;
    var v = parseFloat(raw), b = parseFloat(state.budget);
    return b === 0 ? v === 0 : v < b;
  }
  function hasFormat(c) {
    if (state.format === 'all') return true;
    var have = (c.getAttribute('data-formats') || '').split('|'), want = state.format.split(',');
    for (var i = 0; i < want.length; i++) if (have.indexOf(want[i]) !== -1) return true;
    return false;
  }
  function hasPlatform(c) {
    if (state.platform === 'all') return true;
    return (c.getAttribute('data-platforms') || 'unknown').split('|').indexOf(state.platform) !== -1;
  }
  function updateCount(shown, filtering) {
    if (!countEl) return;
    var noun = total === 1 ? 'tool' : 'tools';
    if (!filtering) countEl.textContent = 'Showing all ' + total + ' ' + noun;
    else if (shown === 0) countEl.textContent = 'No tools match (0 of ' + total + ')';
    else countEl.textContent = 'Showing ' + shown + ' of ' + total + ' ' + noun;
  }
  function setPill(type, value) {
    var pills = document.querySelectorAll('.filter-pill[data-filter-type="' + type + '"]');
    if (!pills.length) return false;
    var ok = false;
    pills.forEach(function (o) {
      var on = o.dataset.filterValue === value;
      o.classList.toggle('active', on);
      o.setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on) ok = true;
    });
    if (ok) state[type] = value;
    return ok;
  }
  function resolvePill(type, raw) {
    if (raw == null || raw === '') return null;
    if (type === 'budget') {
      raw = PARAM_TO_BUDGET[String(raw).toLowerCase()] || raw;
    }
    var want = String(raw).toLowerCase();
    var wantSlug = slugify(raw);
    var pills = document.querySelectorAll('.filter-pill[data-filter-type="' + type + '"]');
    for (var i = 0; i < pills.length; i++) {
      var v = pills[i].dataset.filterValue;
      if (v === raw || v.toLowerCase() === want || slugify(v) === wantSlug) return v;
    }
    return null;
  }
  function syncUrl() {
    if (syncing) return;
    var params = new URLSearchParams(location.search);
    FILTER_PARAMS.forEach(function (k) { params.delete(k); });
    if (state.category !== 'all') params.set('cat', slugify(state.category));
    if (state.q) params.set('q', search ? search.value.trim() : state.q);
    if (state.pricing !== 'all') params.set('pricing', state.pricing);
    if (state.usage !== 'medium') params.set('weight', state.usage);
    if (state.budget !== 'any') params.set('price', BUDGET_TO_PARAM[state.budget] || state.budget);
    if (state.commercial !== 'all') params.set('licence', state.commercial);
    if (state.format !== 'all') params.set('format', slugify(state.format));
    if (state.platform !== 'all') params.set('platform', slugify(state.platform));
    var qs = params.toString();
    var next = location.pathname + (qs ? '?' + qs : '') + location.hash;
    var cur = location.pathname + location.search + location.hash;
    if (next !== cur) history.replaceState(null, '', next);
  }
  function apply() {
    var shown = 0, filtering = !!state.q || state.category !== 'all' || state.pricing !== 'all' || state.budget !== 'any' || state.commercial !== 'all' || state.format !== 'all' || state.platform !== 'all';
    cards.forEach(function (c) {
      var hay = (c.dataset.name + ' ' + c.dataset.description + ' ' + c.dataset.categories + ' ' + c.dataset.tags).toLowerCase();
      var ok = (!state.q || hay.indexOf(state.q) !== -1) &&
        (state.category === 'all' || c.dataset.categories.split('|').indexOf(state.category) !== -1) &&
        (state.pricing === 'all' || c.dataset.pricing === state.pricing) &&
        withinBudget(c) &&
        (state.commercial === 'all' || (c.getAttribute('data-commercial') || 'unknown') === state.commercial) &&
        hasFormat(c) && hasPlatform(c);
      c.style.display = ok ? '' : 'none'; if (ok) shown++;
    });
    if (noRes) noRes.style.display = shown ? 'none' : 'block';
    updateCount(shown, filtering);
    browse.forEach(function (s) { s.style.display = filtering ? 'none' : ''; });
    syncUrl();
  }
  function loadFromUrl() {
    syncing = true;
    Object.keys(DEFAULTS).forEach(function (type) { setPill(type, DEFAULTS[type]); });
    state.q = '';
    if (search) search.value = '';
    var params = new URLSearchParams(location.search);
    var pairs = [
      ['cat', 'category'],
      ['pricing', 'pricing'],
      ['weight', 'usage'],
      ['price', 'budget'],
      ['licence', 'commercial'],
      ['format', 'format'],
      ['platform', 'platform']
    ];
    pairs.forEach(function (pair) {
      var raw = params.get(pair[0]);
      if (!raw) return;
      var v = resolvePill(pair[1], raw);
      if (v) setPill(pair[1], v);
    });
    var q = params.get('q');
    if (q && search) { search.value = q; state.q = q.trim().toLowerCase(); }
    else if (q) state.q = q.trim().toLowerCase();
    syncing = false;
    apply();
  }
  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); apply(); });
  document.querySelectorAll('.filter-pill').forEach(function (p) { p.setAttribute('aria-pressed', p.classList.contains('active') ? 'true' : 'false'); });
  document.querySelectorAll('.filter-pill').forEach(function (p) {
    p.addEventListener('click', function () {
      var type = p.dataset.filterType;
      document.querySelectorAll('.filter-pill[data-filter-type="' + type + '"]').forEach(function (o) { o.classList.remove('active'); o.setAttribute('aria-pressed', 'false'); });
      p.classList.add('active'); p.setAttribute('aria-pressed', 'true'); state[type] = p.dataset.filterValue; apply();
      try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path: 'filter/' + type + '/' + p.dataset.filterValue, title: 'Filter: ' + type + ' = ' + p.textContent.trim() + ' (' + location.pathname + ')', event: true }); } catch (e) {}
    });
  });
  var clear = document.getElementById('clear-filters');
  if (clear) clear.addEventListener('click', function () {
    Object.keys(DEFAULTS).forEach(function (type) { setPill(type, DEFAULTS[type]); });
    state.q = ''; if (search) search.value = '';
    apply();
  });
  if (countEl) {
    var wrap = document.createElement('div');
    wrap.className = 'results-bar';
    countEl.parentNode.insertBefore(wrap, countEl);
    wrap.appendChild(countEl);
    var copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'btn btn-secondary copy-link-btn';
    copyBtn.textContent = 'Copy link';
    copyBtn.setAttribute('aria-label', 'Copy a shareable link to these filters');
    wrap.appendChild(copyBtn);
    var copiedTimer;
    function copied() {
      copyBtn.textContent = 'Copied!';
      clearTimeout(copiedTimer);
      copiedTimer = setTimeout(function () { copyBtn.textContent = 'Copy link'; }, 2000);
    }
    function fallbackCopy(text, ok) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      try { if (document.execCommand('copy')) ok(); } catch (err) {}
      document.body.removeChild(ta);
    }
    copyBtn.addEventListener('click', function () {
      syncUrl();
      var url = location.href;
      if (navigator.clipboard && window.isSecureContext && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(copied, function () { fallbackCopy(url, copied); });
      } else fallbackCopy(url, copied);
    });
  }
  loadFromUrl();
  window.addEventListener('popstate', loadFromUrl);
})();

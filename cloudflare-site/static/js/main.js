(function () {
  var btn = document.querySelector('.mobile-menu-btn'), links = document.querySelector('.nav-links');
  if (btn && links) btn.addEventListener('click', function () { links.classList.toggle('open'); });
  var search = document.getElementById('tool-search'), grid = document.getElementById('filtered-tools');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.tool-card'));
  var noRes = document.getElementById('no-results'), state = { category: 'all', pricing: 'all', q: '', usage: 'medium', budget: 'any', commercial: 'all', format: 'all', platform: 'all' };
  var countEl = document.getElementById('results-count'), total = cards.length;
  var DEFAULTS = { category: 'all', pricing: 'all', budget: 'any', commercial: 'all', format: 'all', platform: 'all' };
  var browse = document.querySelectorAll('.section.browse');
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
    Object.keys(DEFAULTS).forEach(function (type) {
      state[type] = DEFAULTS[type];
      document.querySelectorAll('.filter-pill[data-filter-type="' + type + '"]').forEach(function (o) {
        var on = o.dataset.filterValue === DEFAULTS[type]; o.classList.toggle('active', on); o.setAttribute('aria-pressed', on ? 'true' : 'false');
      });
    });
    state.q = ''; if (search) search.value = '';
    apply();
  });
  var q = new URLSearchParams(location.search).get('q');
  if (q && search) { search.value = q; state.q = q.toLowerCase(); apply(); }
})();

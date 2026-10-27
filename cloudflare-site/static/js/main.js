(function () {
  var btn = document.querySelector('.mobile-menu-btn'), links = document.querySelector('.nav-links');
  if (btn && links) btn.addEventListener('click', function () { links.classList.toggle('open'); });
  var search = document.getElementById('tool-search'), grid = document.getElementById('filtered-tools');
  if (!grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.tool-card'));
  var noRes = document.getElementById('no-results'), state = { category: 'all', pricing: 'all', q: '', usage: 'medium', budget: 'any' };
  var browse = document.querySelectorAll('.section.browse');
  function withinBudget(c) {
    if (state.budget === 'any') return true;
    var raw = c.getAttribute('data-spend-' + state.usage);
    if (raw === null || raw === '') return false;
    var v = parseFloat(raw), b = parseFloat(state.budget);
    return b === 0 ? v === 0 : v < b;
  }
  function apply() {
    var shown = 0, filtering = state.q || state.category !== 'all' || state.pricing !== 'all' || state.budget !== 'any';
    cards.forEach(function (c) {
      var hay = (c.dataset.name + ' ' + c.dataset.description + ' ' + c.dataset.categories + ' ' + c.dataset.tags).toLowerCase();
      var ok = (!state.q || hay.indexOf(state.q) !== -1) &&
        (state.category === 'all' || c.dataset.categories.split('|').indexOf(state.category) !== -1) &&
        (state.pricing === 'all' || c.dataset.pricing === state.pricing) &&
        withinBudget(c);
      c.style.display = ok ? '' : 'none'; if (ok) shown++;
    });
    if (noRes) noRes.style.display = shown ? 'none' : 'block';
    browse.forEach(function (s) { s.style.display = filtering ? 'none' : ''; });
  }
  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); apply(); });
  document.querySelectorAll('.filter-pill').forEach(function (p) {
    p.addEventListener('click', function () {
      var type = p.dataset.filterType;
      document.querySelectorAll('.filter-pill[data-filter-type="' + type + '"]').forEach(function (o) { o.classList.remove('active'); });
      p.classList.add('active'); state[type] = p.dataset.filterValue; apply();
    });
  });
  var q = new URLSearchParams(location.search).get('q');
  if (q && search) { search.value = q; state.q = q.toLowerCase(); apply(); }
})();

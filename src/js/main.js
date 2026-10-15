// Mobile menu toggle
document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.querySelector('.mobile-menu-btn');
  const navLinks = document.querySelector('.nav-links');

  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }

  // Search and filter functionality
  initSearch();
  initFilters();
});

// Search functionality
function initSearch() {
  const searchBox = document.getElementById('tool-search');
  if (!searchBox) return;

  searchBox.addEventListener('input', debounce((e) => {
    const query = e.target.value.toLowerCase().trim();
    filterTools();
  }, 200));
}

// Filter functionality
function initFilters() {
  const filterPills = document.querySelectorAll('.filter-pill');
  
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      const filterType = pill.dataset.filterType;
      const filterValue = pill.dataset.filterValue;

      // Handle "all" selections
      if (filterValue === 'all') {
        document.querySelectorAll(`.filter-pill[data-filter-type="${filterType}"]`).forEach(p => {
          p.classList.remove('active');
        });
        pill.classList.add('active');
      } else {
        // Remove "all" selection when specific filter is clicked
        const allPill = document.querySelector(`.filter-pill[data-filter-type="${filterType}"][data-filter-value="all"]`);
        if (allPill) allPill.classList.remove('active');

        // Toggle current pill
        pill.classList.toggle('active');

        // If no pills active, activate "all"
        const activeInGroup = document.querySelectorAll(`.filter-pill[data-filter-type="${filterType}"].active`);
        if (activeInGroup.length === 0 && allPill) {
          allPill.classList.add('active');
        }
      }

      filterTools();
    });
  });
}

// Filter tools based on search and active filters
function filterTools() {
  const searchBox = document.getElementById('tool-search');
  const query = searchBox ? searchBox.value.toLowerCase().trim() : '';
  
  // Get active category filters
  const activeCategories = Array.from(
    document.querySelectorAll('.filter-pill[data-filter-type="category"].active')
  ).map(p => p.dataset.filterValue).filter(v => v !== 'all');

  // Get active pricing filters
  const activePricing = Array.from(
    document.querySelectorAll('.filter-pill[data-filter-type="pricing"].active')
  ).map(p => p.dataset.filterValue).filter(v => v !== 'all');

  const toolCards = document.querySelectorAll('.tool-card[data-tool]');
  let visibleCount = 0;

  toolCards.forEach(card => {
    const name = (card.dataset.name || '').toLowerCase();
    const description = (card.dataset.description || '').toLowerCase();
    const categories = (card.dataset.categories || '').toLowerCase().split(',');
    const pricing = (card.dataset.pricing || '').toLowerCase();
    const tags = (card.dataset.tags || '').toLowerCase();

    // Check search query
    const matchesSearch = !query || 
      name.includes(query) || 
      description.includes(query) ||
      tags.includes(query);

    // Check category filter
    const matchesCategory = activeCategories.length === 0 || 
      categories.some(cat => activeCategories.includes(cat.trim()));

    // Check pricing filter
    const matchesPricing = activePricing.length === 0 || 
      activePricing.includes(pricing);

    if (matchesSearch && matchesCategory && matchesPricing) {
      card.style.display = '';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  // Show/hide no results message
  const noResults = document.getElementById('no-results');
  if (noResults) {
    noResults.style.display = visibleCount === 0 ? 'block' : 'none';
  }
}

// Debounce helper
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

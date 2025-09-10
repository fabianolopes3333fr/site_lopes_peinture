// Toggle filtres mobile
function toggleFilters() {
  const modal = document.getElementById('mobile-filter-modal');
  const sidebar = modal.querySelector('.transform');

  if (modal.classList.contains('hidden')) {
    modal.classList.remove('hidden');
    setTimeout(() => {
      sidebar.classList.remove('-translate-x-full');
    }, 10);
  } else {
    sidebar.classList.add('-translate-x-full');
    setTimeout(() => {
      modal.classList.add('hidden');
    }, 300);
  }
}

// Função para alternar entre vista grid e lista
function setView(viewType) {
  const gridBtn = document.getElementById('grid-view-btn');
  const listBtn = document.getElementById('list-view-btn');
  const projectsContainer = document.getElementById('projects-container');

  if (!gridBtn || !listBtn || !projectsContainer) return;

  // Reset classes dos botões
  gridBtn.className = 'btn btn-sm transition-all duration-200 flex-1 sm:flex-initial';
  listBtn.className = 'btn btn-sm transition-all duration-200 flex-1 sm:flex-initial';

  if (viewType === 'grid') {
    // Ativar botão grid
    gridBtn.classList.add('bg-white', 'text-brand-600', 'shadow-sm');
    listBtn.classList.add('btn-ghost', 'text-gray-600');

    // Aplicar layout grid
    projectsContainer.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6';

    // Salvar preferência
    localStorage.setItem('projects_view', 'grid');
  } else if (viewType === 'list') {
    // Ativar botão list
    listBtn.classList.add('bg-white', 'text-brand-600', 'shadow-sm');
    gridBtn.classList.add('btn-ghost', 'text-gray-600');

    // Aplicar layout lista
    projectsContainer.className = 'space-y-4';

    // Modificar cards para layout lista
    const cards = projectsContainer.querySelectorAll('.card');
    cards.forEach((card) => {
      card.classList.add('flex', 'flex-row', 'items-center');
      // Adicionar classes específicas para vista lista se necessário
    });

    // Salvar preferência
    localStorage.setItem('projects_view', 'list');
  }
}
// Função para carregar a vista salva
function loadSavedView() {
  const savedView = localStorage.getItem('projects_view') || 'grid';
  setView(savedView);
}

// Mudança de ordenação
function changeSorting(value) {
  const url = new URL(window.location);
  url.searchParams.set('ordering', value);
  url.searchParams.delete('page'); // Reset pagination
  window.location.href = url.toString();
}

// Exportar projetos
function exportProjects() {
  showNotification('Export en cours...', 'info');

  const url = new URL(window.location);
  url.searchParams.set('export', 'csv');

  // Criar um link temporário para download
  const link = document.createElement('a');
  link.href = url.toString();
  link.download = `projets_${new Date().getTime()}.csv`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  setTimeout(() => {
    showNotification('Export terminé avec succès!', 'success');
  }, 2000);
}

// Solicitar orçamento
function requestQuote(projectId) {
  if (confirm('Voulez-vous demander un devis pour ce projet ?')) {
    showNotification('Demande de devis envoyée...', 'info');

    fetch(`/projects/${projectId}/request-quote/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCsrfToken(),
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showNotification('Demande de devis envoyée avec succès!', 'success');
          setTimeout(() => {
            window.location.reload();
          }, 2000);
        } else {
          showNotification(data.message || 'Erreur lors de la demande de devis', 'error');
        }
      })
      .catch((error) => {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion', 'error');
      });
  }
}

// Marcar como favorito
function toggleFavorite(projectId) {
  const icon = document.querySelector(`[data-project-id="${projectId}"] .favorite-icon`);

  fetch(`/projects/${projectId}/toggle-favorite/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'Content-Type': 'application/json',
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        if (icon) {
          if (data.is_favorite) {
            icon.classList.remove('text-gray-400');
            icon.classList.add('text-yellow-500');
            showNotification('Ajouté aux favoris', 'success');
          } else {
            icon.classList.remove('text-yellow-500');
            icon.classList.add('text-gray-400');
            showNotification('Retiré des favoris', 'info');
          }
        }
      }
    })
    .catch((error) => {
      console.error('Erreur:', error);
      showNotification('Erreur lors de la mise à jour', 'error');
    });
}

// Compartilhar projeto
function shareProject(projectId, title) {
  const url = `${window.location.origin}/projects/${projectId}/`;

  if (navigator.share) {
    navigator
      .share({
        title: `Projet: ${title}`,
        text: `Consultez ce projet de peinture`,
        url: url,
      })
      .catch((err) => console.log('Erreur de partage:', err));
  } else {
    // Fallback: copiar para clipboard
    navigator.clipboard
      .writeText(url)
      .then(() => {
        showNotification('Lien copié dans le presse-papiers!', 'success');
      })
      .catch(() => {
        // Fallback do fallback
        const textArea = document.createElement('textarea');
        textArea.value = url;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Lien copié!', 'success');
      });
  }
}

// Mostrar notificação
function showNotification(message, type = 'info') {
  // Remover notificações existentes
  const existingNotifications = document.querySelectorAll('.notification');
  existingNotifications.forEach((n) => n.remove());

  const notification = document.createElement('div');
  notification.className = `notification ${getNotificationClasses(type)}`;

  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle',
  };

  notification.innerHTML = `
    <div class="flex items-center gap-3">
      <i class="fas ${icons[type]} text-lg"></i>
      <span class="font-medium">${message}</span>
    </div>
  `;

  document.body.appendChild(notification);

  // Mostrar notificação
  setTimeout(() => {
    notification.classList.add('show');
  }, 100);

  // Remover após 4 segundos
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => {
      if (notification.parentNode) {
        document.body.removeChild(notification);
      }
    }, 300);
  }, 4000);
}

// Obter classes da notificação por tipo
function getNotificationClasses(type) {
  const classes = {
    success: 'bg-success-500 text-white',
    error: 'bg-danger-500 text-white',
    warning: 'bg-warning-500 text-white',
    info: 'bg-brand-500 text-white',
  };
  return classes[type] || classes.info;
}

// Obter CSRF token
function getCsrfToken() {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
  return csrfToken ? csrfToken.value : '';
}

// Gerar chips de filtros ativos
function generateFilterChips() {
  const chipsContainer = document.getElementById('filter-chips');
  if (!chipsContainer) return;

  const urlParams = new URLSearchParams(window.location.search);
  const chips = [];

  // Mapear parâmetros para labels
  const filterLabels = {
    search: 'Recherche',
    status: 'Statut',
    type_projet: 'Type',
    priority: 'Priorité',
    ville: 'Ville',
    surface_min: 'Surface min',
    surface_max: 'Surface max',
    date_from: 'Depuis',
    date_to: "Jusqu'au",
  };

  urlParams.forEach((value, key) => {
    if (value && filterLabels[key] && key !== 'page' && key !== 'ordering') {
      chips.push(`
        <span class="badge badge-primary flex items-center gap-2">
          ${filterLabels[key]}: ${value}
          <button onclick="removeFilter('${key}')" class="text-white hover:text-gray-200">
            <i class="fas fa-times text-xs"></i>
          </button>
        </span>
      `);
    }
  });

  if (chips.length > 0) {
    chipsContainer.innerHTML = `
      <div class="card p-4">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-sm font-medium text-gray-600">Filtres actifs:</span>
          ${chips.join('')}
          <button onclick="clearAllFilters()" class="btn btn-sm btn-ghost text-danger-600">
            <i class="fas fa-times mr-1"></i>
            Tout supprimer
          </button>
        </div>
      </div>
    `;
    chipsContainer.classList.remove('hidden');
  } else {
    chipsContainer.classList.add('hidden');
  }
}
// Inicialização quando DOM carrega
document.addEventListener('DOMContentLoaded', function () {
  // Restaurar vista salva
  const savedView = localStorage.getItem('projectsView') || 'grid';
  setView(savedView);

  // Animar cards ao entrar na viewport
  const cards = document.querySelectorAll('.card-animate');
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add('animate-fade-in-up');
          }, index * 100);
        }
      });
    },
    {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px',
    }
  );

  cards.forEach((card) => observer.observe(card));

  // Gerar chips de filtros ativos
  generateFilterChips();

  // Auto-submit do formulário de filtros com debounce
  const filterInputs = document.querySelectorAll('#filter-form input, #filter-form select');
  let debounceTimer;

  filterInputs.forEach((input) => {
    input.addEventListener('input', function () {
      if (this.type === 'text') {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          document.getElementById('filter-form').submit();
        }, 800); // Debounce de 800ms para texto
      } else {
        // Submit imediato para selects
        document.getElementById('filter-form').submit();
      }
    });
  });

  // Fechar modal mobile ao clicar fora
  const modal = document.getElementById('mobile-filters-modal');
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === this) {
        toggleMobileFilters();
      }
    });
  }

  // Fechar modal com ESC
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      const modal = document.getElementById('mobile-filters-modal');
      if (modal && !modal.classList.contains('hidden')) {
        toggleMobileFilters();
      }
    }
  });

  // Responsividade para sidebar
  window.addEventListener('resize', function () {
    const isMobile = window.innerWidth < 1024;
    const sidebar = document.getElementById('filters-sidebar');

    if (!isMobile && sidebar.classList.contains('hidden')) {
      sidebar.classList.remove('hidden');
    }
  });
});
// Gerar chips de filtros ativos
function generateFilterChips() {
  const chipsContainer = document.getElementById('filter-chips');
  if (!chipsContainer) return;

  const urlParams = new URLSearchParams(window.location.search);
  const chips = [];

  // Mapear parâmetros para labels
  const filterLabels = {
    search: 'Recherche',
    status: 'Statut',
    type_projet: 'Type',
    priority: 'Priorité',
    ville: 'Ville',
    surface_min: 'Surface min',
    surface_max: 'Surface max',
    date_from: 'Depuis',
    date_to: "Jusqu'au",
  };

  urlParams.forEach((value, key) => {
    if (value && filterLabels[key] && key !== 'page' && key !== 'ordering') {
      chips.push(`
        <span class="filter-chip">
          ${filterLabels[key]}: ${value}
          <button onclick="removeFilter('${key}')" class="ml-2 text-blue-600 hover:text-blue-800">
            <i class="fas fa-times text-xs"></i>
          </button>
        </span>
      `);
    }
  });

  if (chips.length > 0) {
    chipsContainer.innerHTML = `
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-sm font-medium text-gray-600">Filtres actifs:</span>
        ${chips.join('')}
        <button onclick="clearAllFilters()" class="text-xs text-red-600 hover:text-red-800 font-medium underline">
          Tout supprimer
        </button>
      </div>
    `;
    chipsContainer.classList.remove('hidden');
  } else {
    chipsContainer.classList.add('hidden');
  }
}

// Remover filtro específico
function removeFilter(filterKey) {
  const url = new URL(window.location);
  url.searchParams.delete(filterKey);
  url.searchParams.delete('page'); // Reset pagination
  window.location.href = url.toString();
}

// Limpar todos os filtros
function clearAllFilters() {
  const url = new URL(window.location);
  // Manter apenas ordering se existir
  const ordering = url.searchParams.get('ordering');
  url.search = '';
  if (ordering) {
    url.searchParams.set('ordering', ordering);
  }
  window.location.href = url.toString();
}

// Função para atualizar contadores em tempo real (opcional)
function updateProjectCounts() {
  fetch('/projects/api/counts/', {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // Atualizar contadores na sidebar
      document.querySelector('.stats-item:nth-child(1) span:last-child').textContent = data.total;
      document.querySelector('.stats-item:nth-child(2) span:last-child').textContent = data.active;
      document.querySelector('.stats-item:nth-child(3) span:last-child').textContent = data.pending;
      document.querySelector('.stats-item:nth-child(4) span:last-child').textContent =
        data.completed;
    })
    .catch((error) => console.log('Erro ao atualizar contadores:', error));
}

// Função de busca instantânea (opcional)
function setupInstantSearch() {
  const searchInput = document.querySelector('input[name="search"]');
  if (!searchInput) return;

  let searchTimeout;
  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimeout);
    const query = this.value.trim();

    if (query.length >= 2) {
      searchTimeout = setTimeout(() => {
        // Aqui você pode implementar busca AJAX se necessário
        showNotification(`Recherche: ${query}`, 'info');
      }, 500);
    }
  });
}

// Atualizar contadores em tempo real (opcional)
function updateProjectCounts() {
  fetch('/projects/api/counts/', {
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Atualizar contadores
        const counters = document.querySelectorAll('.card .text-xl, .card .text-2xl');
        if (counters[0]) counters[0].textContent = data.total || 0;
        if (counters[1]) counters[1].textContent = data.active || 0;
        if (counters[2]) counters[2].textContent = data.pending || 0;
        if (counters[3]) counters[3].textContent = data.completed || 0;
      }
    })
    .catch((error) => console.log('Erro ao atualizar contadores:', error));
}

// Função para destacar texto da busca
function highlightSearchTerms() {
  const searchTerm = new URLSearchParams(window.location.search).get('search');
  if (!searchTerm) return;

  const cards = document.querySelectorAll('.card');
  cards.forEach((card) => {
    const textNodes = card.querySelectorAll('h3, p, span');
    textNodes.forEach((node) => {
      if (node.textContent.toLowerCase().includes(searchTerm.toLowerCase())) {
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        node.innerHTML = node.innerHTML.replace(
          regex,
          '<mark class="bg-yellow-200 px-1 rounded">$1</mark>'
        );
      }
    });
  });
}
function performInstantSearch(query) {
  // Implementar busca instantânea via AJAX se necessário
  console.log('Busca instantânea:', query);
}

// Função para salvar estado dos filtros
function saveFilterState() {
  const formData = new FormData(document.getElementById('filter-form'));
  const filterState = {};

  for (let [key, value] of formData.entries()) {
    if (value) filterState[key] = value;
  }

  localStorage.setItem('projectFilters', JSON.stringify(filterState));
}

// Função para restaurar estado dos filtros
function restoreFilterState() {
  const savedFilters = localStorage.getItem('projectFilters');
  if (!savedFilters) return;

  try {
    const filters = JSON.parse(savedFilters);
    Object.entries(filters).forEach(([key, value]) => {
      const input = document.querySelector(`[name="${key}"]`);
      if (input) input.value = value;
    });
  } catch (error) {
    console.log('Erro ao restaurar filtros:', error);
  }
}

// Função para scroll suave até os resultados
function scrollToResults() {
  const resultsSection = document.querySelector('.results-info');
  if (resultsSection) {
    resultsSection.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  }
}

// Função para preview de projeto (modal rápido)
function quickPreview(projectId) {
  // Implementar modal de preview rápido se necessário
  console.log('Preview rápido do projeto:', projectId);
}

// Função para marcar projetos como favoritos
function toggleFavorite(projectId) {
  fetch(`/projects/${projectId}/toggle-favorite/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      'Content-Type': 'application/json',
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        const icon = document.querySelector(`[data-project-id="${projectId}"] .favorite-icon`);
        if (icon) {
          icon.classList.toggle('text-yellow-500');
          icon.classList.toggle('text-gray-400');
        }
      }
    })
    .catch((error) => console.log('Erro ao marcar favorito:', error));
}

// Função para compartilhar projeto
function shareProject(projectId, title) {
  if (navigator.share) {
    navigator.share({
      title: `Projet: ${title}`,
      text: `Consultez ce projet de peinture`,
      url: `/projects/${projectId}/`,
    });
  } else {
    // Fallback para navegadores sem suporte
    const url = `${window.location.origin}/projects/${projectId}/`;
    navigator.clipboard.writeText(url).then(() => {
      alert('Lien copié dans le presse-papiers!');
    });
  }
}

// Função para imprimir lista de projetos
function printProjectList() {
  window.print();
}

// Media queries para responsividade adicional
window.addEventListener('resize', function () {
  const isMobile = window.innerWidth < 1024;
  const sidebar = document.getElementById('filters-sidebar');

  if (!isMobile && sidebar.classList.contains('hidden')) {
    sidebar.classList.remove('hidden');
  }
});

// Inicialização adicional
document.addEventListener('DOMContentLoaded', function () {
  loadSavedView();
  // Configurar busca instantânea se habilitada
  setupInstantSearch();
  // Restaurar estado dos filtros se necessário
  restoreFilterState();
  // Atualizar contadores periodicamente se necessário
  setInterval(updateProjectCounts, 30000); // A cada 30 segundos
});

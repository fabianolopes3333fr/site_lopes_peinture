// Variáveis globais
let allColors = [];
let filteredColors = [];
let currentFilter = 'all';

// Dados de exemplo (substitua pela chamada da API real)

// Inicialização
document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM carregado, inicializando...');
  loadColors();
  setupEventListeners();
});

// Carregar cores da API
async function loadColors() {
  try {
    showLoading(true);

    // Simular carregamento da API
    // Em produção, substitua por: const response = await fetch('/api/couleurs/');
    const response = await fetch('/api/couleurs/');
    const data = await response.json(); // Simular delay

    // Usar dados mock por enquanto
    allColors = data.couleurs;
    filteredColors = [...allColors];

    console.log('Cores carregadas:', allColors);
    renderColors();
    showLoading(false);
  } catch (error) {
    console.error('Erro ao carregar cores:', error);
    showLoading(false);
    showNoResults(true);
  }
}

// Configurar event listeners
function setupEventListeners() {
  console.log('Configurando event listeners...');

  // Dropdown de filtros
  const dropdownBtn = document.getElementById('filterDropdownBtn');
  const dropdown = document.getElementById('filterDropdown');
  const dropdownIcon = document.getElementById('dropdownIcon');

  if (dropdownBtn && dropdown && dropdownIcon) {
    dropdownBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropdown.classList.toggle('hidden');
      dropdownIcon.style.transform = dropdown.classList.contains('hidden')
        ? 'rotate(0deg)'
        : 'rotate(180deg)';
    });

    // Fechar dropdown ao clicar fora
    document.addEventListener('click', function (e) {
      if (!dropdownBtn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
        dropdownIcon.style.transform = 'rotate(0deg)';
      }
    });

    // Opções de filtro
    document.querySelectorAll('.filter-option').forEach((option) => {
      option.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        const filter = this.dataset.filter;
        const text = this.textContent.trim();

        console.log('Filtro selecionado:', filter);

        // Atualizar UI
        document
          .querySelectorAll('.filter-option')
          .forEach((opt) => opt.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('selectedFilterText').textContent = text;
        dropdown.classList.add('hidden');
        dropdownIcon.style.transform = 'rotate(0deg)';

        // Aplicar filtro
        currentFilter = filter;
        applyFilters();
      });
    });
  }

  // Busca
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener(
      'input',
      debounce(function () {
        console.log('Busca:', this.value);
        applyFilters();
      }, 300)
    );
  }

  // Modal
  setupModal();
}

// Aplicar filtros
function applyFilters() {
  const searchInput = document.getElementById('searchInput');
  const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

  console.log('Aplicando filtros - Categoria:', currentFilter, 'Busca:', searchTerm);

  filteredColors = allColors.filter((color) => {
    // Filtro por categoria
    const categoryMatch =
      currentFilter === 'all' || color.category.toLowerCase().includes(currentFilter);

    // Filtro por busca
    const searchMatch =
      !searchTerm ||
      color.name.toLowerCase().includes(searchTerm) ||
      color.code.toLowerCase().includes(searchTerm) ||
      color.category.toLowerCase().includes(searchTerm);

    return categoryMatch && searchMatch;
  });

  console.log('Cores filtradas:', filteredColors.length);
  renderColors();
}

// Renderizar cores
function renderColors() {
  const grid = document.getElementById('colorsGrid');

  if (!grid) {
    console.error('Grid não encontrado');
    return;
  }

  if (filteredColors.length === 0) {
    showNoResults(true);
    grid.innerHTML = '';
    return;
  }

  showNoResults(false);

  grid.innerHTML = filteredColors
    .map(
      (color) => `
    <div class="color-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-all duration-300" 
         data-color='${JSON.stringify(color)}'>
      <div class="color-sample" style="background-color: ${color.rgb};"></div>
      <div class="p-3">
        <h3 class="font-semibold text-sm text-gray-900 mb-1 truncate" title="${color.name}">
          ${color.name}
        </h3>
        <p class="text-xs text-gray-600 font-mono">${color.code}</p>
        ${
          color.popular
            ? '<span class="inline-block mt-1 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">★ Populaire</span>'
            : ''
        }
      </div>
    </div>
  `
    )
    .join('');

  console.log('Cores renderizadas:', filteredColors.length);

  // Adicionar event listeners aos cards
  document.querySelectorAll('.color-card').forEach((card) => {
    card.addEventListener('click', function () {
      const colorData = JSON.parse(this.dataset.color);
      console.log('Cor clicada:', colorData);
      openModal(colorData);
    });
  });
}

// Modal
function setupModal() {
  const modal = document.getElementById('colorModal');
  const closeBtn = document.getElementById('closeModal');

  if (!modal || !closeBtn) {
    console.error('Elementos do modal não encontrados');
    return;
  }

  closeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    console.log('Fechando modal via botão');
    closeModal();
  });

  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      console.log('Fechando modal via clique fora');
      closeModal();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      console.log('Fechando modal via ESC');
      closeModal();
    }
  });
}

function openModal(color) {
  console.log('Abrindo modal para:', color);

  const modal = document.getElementById('colorModal');

  if (!modal) {
    console.error('Modal não encontrado');
    return;
  }

  // Preencher dados
  const elements = {
    modalColorSample: document.getElementById('modalColorSample'),
    modalColorName: document.getElementById('modalColorName'),
    modalColorCode: document.getElementById('modalColorCode'),
    modalColorCategory: document.getElementById('modalColorCategory'),
    modalColorRGB: document.getElementById('modalColorRGB'),
  };

  // Verificar se todos os elementos existem
  for (const [key, element] of Object.entries(elements)) {
    if (!element) {
      console.error(`Elemento ${key} não encontrado`);
      return;
    }
  }

  // Preencher os dados
  elements.modalColorSample.style.backgroundColor = color.rgb;
  elements.modalColorName.textContent = color.name;
  elements.modalColorCode.textContent = color.code;
  elements.modalColorCategory.textContent = color.category;
  elements.modalColorRGB.textContent = color.rgb;

  // Mostrar modal
  modal.classList.add('active');
  document.body.style.overflow = 'hidden'; // Prevenir scroll

  console.log('Modal aberto com sucesso');
}

function closeModal() {
  const modal = document.getElementById('colorModal');

  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restaurar scroll
    console.log('Modal fechado');
  }
}

// Utilitários
function showLoading(show) {
  const loading = document.getElementById('loading');
  if (loading) {
    loading.style.display = show ? 'block' : 'none';
  }
}

function showNoResults(show) {
  const noResults = document.getElementById('noResults');
  if (noResults) {
    noResults.classList.toggle('hidden', !show);
  }
}

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

// Função para converter hex para RGB (caso necessário)
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

// Função para gerar mais cores de exemplo (para teste)
function generateMoreColors() {
  const colors = [
    { name: 'Noir Profond', code: 'RAL-9005', category: 'RAL', rgb: 'rgb(14, 14, 16)' },
    { name: 'Beige Sable', code: 'RAL-1001', category: 'RAL', rgb: 'rgb(194, 178, 128)' },
    { name: 'Orange Vif', code: 'RAL-2004', category: 'RAL', rgb: 'rgb(244, 125, 35)' },
    { name: 'Violet Royal', code: 'RAL-4008', category: 'RAL', rgb: 'rgb(146, 39, 143)' },
    { name: 'Turquoise', code: 'RAL-5018', category: 'RAL', rgb: 'rgb(61, 177, 222)' },
    { name: 'Vert Pomme', code: 'RAL-6018', category: 'RAL', rgb: 'rgb(87, 160, 66)' },
    { name: 'Marron Chocolat', code: 'RAL-8017', category: 'RAL', rgb: 'rgb(69, 53, 47)' },
    { name: 'Rose Poudré', code: 'RAL-3015', category: 'RAL', rgb: 'rgb(234, 170, 170)' },
    { name: 'Bleu Marine', code: 'RAL-5003', category: 'RAL', rgb: 'rgb(22, 41, 69)' },
    { name: 'Vert Olive', code: 'RAL-6003', category: 'RAL', rgb: 'rgb(79, 102, 40)' },
  ];

  return colors;
}

// Variável global para armazenar a cor atual do modal
let currentModalColor = null;

// Função para gerar e baixar amostra de cor
function downloadColorSample(color) {
  console.log('Gerando amostra para download:', color);

  // Criar canvas
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  // Definir dimensões (formato A4 em pixels para impressão)
  canvas.width = 800;
  canvas.height = 600;

  // Fundo branco
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Cor principal (grande retângulo)
  ctx.fillStyle = color.rgb;
  ctx.fillRect(50, 100, 700, 300);

  // Borda da cor
  ctx.strokeStyle = '#333333';
  ctx.lineWidth = 2;
  ctx.strokeRect(50, 100, 700, 300);

  // Configurar fonte
  ctx.fillStyle = '#333333';
  ctx.font = 'bold 32px Arial, sans-serif';
  ctx.textAlign = 'center';

  // Título
  ctx.fillText('ÉCHANTILLON DE COULEUR', canvas.width / 2, 60);

  // Nome da cor
  ctx.font = 'bold 28px Arial, sans-serif';
  ctx.fillText(color.name, canvas.width / 2, 460);

  // Código da cor
  ctx.font = '24px Arial, sans-serif';
  ctx.fillText(`Code: ${color.code}`, canvas.width / 2, 500);

  // Catégorie
  ctx.fillText(`Catégorie: ${color.category}`, canvas.width / 2, 530);

  // Valeur RGB
  ctx.font = '20px monospace';
  ctx.fillText(`RGB: ${color.rgb}`, canvas.width / 2, 560);

  // Logo/Marque (optionnel)
  ctx.font = 'italic 18px Arial, sans-serif';
  ctx.fillStyle = '#666666';
  ctx.textAlign = 'right';
  ctx.fillText('LOPES PEINTURE', canvas.width - 20, canvas.height - 20);

  // Convertir para blob e fazer download
  canvas.toBlob(
    function (blob) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `echantillon-${color.code.replace(/[^a-zA-Z0-9]/g, '-')}-${color.name.replace(
        /[^a-zA-Z0-9]/g,
        '-'
      )}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      console.log('Download iniciado para:', a.download);
    },
    'image/png',
    1.0
  );
}

// Função para solicitar orçamento
function requestQuote(color) {
  console.log('Solicitando orçamento para:', color);

  // Criar URL com parâmetros da cor
  const params = new URLSearchParams({
    couleur_nom: color.name,
    couleur_code: color.code,
    couleur_rgb: color.rgb,
    couleur_categorie: color.category,
  });

  // Redirecionar para página de contato com parâmetros
  window.location.href = `/contact/?${params.toString()}`;
}

// Atualizar a função openModal para armazenar a cor atual
function openModal(color) {
  console.log('Abrindo modal para:', color);

  // Armazenar cor atual
  currentModalColor = color;

  const modal = document.getElementById('colorModal');

  if (!modal) {
    console.error('Modal não encontrado');
    return;
  }

  // Preencher dados
  const elements = {
    modalColorSample: document.getElementById('modalColorSample'),
    modalColorName: document.getElementById('modalColorName'),
    modalColorCode: document.getElementById('modalColorCode'),
    modalColorCategory: document.getElementById('modalColorCategory'),
    modalColorRGB: document.getElementById('modalColorRGB'),
  };

  // Verificar se todos os elementos existem
  for (const [key, element] of Object.entries(elements)) {
    if (!element) {
      console.error(`Elemento ${key} não encontrado`);
      return;
    }
  }

  // Preencher os dados
  elements.modalColorSample.style.backgroundColor = color.rgb;
  elements.modalColorName.textContent = color.name;
  elements.modalColorCode.textContent = color.code;
  elements.modalColorCategory.textContent = color.category;
  elements.modalColorRGB.textContent = color.rgb;

  // Mostrar modal
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';

  console.log('Modal aberto com sucesso');
}

// Atualizar a função setupModal para incluir os event listeners dos botões
function setupModal() {
  const modal = document.getElementById('colorModal');
  const closeBtn = document.getElementById('closeModal');
  const downloadBtn = document.getElementById('downloadSampleBtn');
  const quoteBtn = document.getElementById('requestQuoteBtn');

  if (!modal || !closeBtn) {
    console.error('Elementos do modal não encontrados');
    return;
  }

  closeBtn.addEventListener('click', function (e) {
    e.preventDefault();
    console.log('Fechando modal via botão');
    closeModal();
  });

  // Event listener para download
  if (downloadBtn) {
    downloadBtn.addEventListener('click', function (e) {
      e.preventDefault();
      if (currentModalColor) {
        downloadColorSample(currentModalColor);
      } else {
        console.error('Nenhuma cor selecionada');
      }
    });
  }

  // Event listener para solicitar orçamento
  if (quoteBtn) {
    quoteBtn.addEventListener('click', function (e) {
      e.preventDefault();
      if (currentModalColor) {
        requestQuote(currentModalColor);
      } else {
        console.error('Nenhuma cor selecionada');
      }
    });
  }

  modal.addEventListener('click', function (e) {
    if (e.target === modal) {
      console.log('Fechando modal via clique fora');
      closeModal();
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      console.log('Fechando modal via ESC');
      closeModal();
    }
  });
}

// Atualizar a função closeModal para limpar a cor atual
function closeModal() {
  const modal = document.getElementById('colorModal');

  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
    currentModalColor = null; // Limpar cor atual
    console.log('Modal fechado');
  }
}

// Adicionar mais cores aos dados mock para teste
if (typeof mockColors !== 'undefined') {
  mockColors.push(...generateMoreColors());
}

console.log('Script carregado com sucesso');

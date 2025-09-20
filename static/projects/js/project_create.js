/**
 * PROJECT CREATE - Controller JavaScript
 * Sistema de criação de projetos em 3 etapas
 */

class ProjectCreateController {
  constructor() {
    // Configurações básicas
    this.currentSection = 1;
    this.totalSections = 3;
    this.form = document.getElementById('project-form');
    this.formData = new Map();
    this.isSubmitting = false;
    this.autoSaveInterval = null;
    this.validationErrors = new Map();

    // Verificar se elementos existem
    if (!this.form) {
      console.error('Formulário não encontrado!');
      return;
    }

    this.init();
  }

  /**
   * Inicialização do controller
   */
  init() {
    console.log('Inicializando ProjectCreateController');

    // Configurar componentes
    this.setupEventListeners();
    this.updateUI();
    this.loadFormData();
    this.setupAutoSave();
    this.focusFirstField();

    // Funções globais para uso inline no HTML
    window.nextSection = (num) => this.nextSection(num);
    window.prevSection = (num) => this.prevSection(num);
    window.showHelp = () => this.showHelp();
    window.closeHelp = () => this.closeHelp();
    window.calculateSurface = () => this.calculateSurface();
    window.applySurfaceCalculation = () => this.applySurfaceCalculation();

    console.log('ProjectCreateController inicializado com sucesso');
  }

  /**
   * Configurar event listeners
   */
  setupEventListeners() {
    console.log('Configurando event listeners');

    // Event listener para submit do formulário
    if (this.form) {
      this.form.addEventListener('submit', (e) => {
        console.log('🚀 Submit event triggered');
        return this.handleSubmit(e);
      });
    }

    // Event listeners para navegação entre seções
    this.setupNavigationListeners();

    // Event listeners para inputs (auto-save e validação)
    this.setupInputListeners();

    // Event listeners para calculadora
    this.setupCalculatorListeners();

    // Event listeners para modal de ajuda
    this.setupHelpModalListeners();

    console.log('Event listeners configurados');
  }

  /**
   * Configurar listeners de navegação
   */
  setupNavigationListeners() {
    // Botões next com data-next-section
    document.querySelectorAll('[data-next-section]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const nextSection = parseInt(btn.dataset.nextSection);
        console.log(`Navegando para seção ${nextSection}`);
        this.nextSection(nextSection);
      });
    });

    // Botões com onclick inline (fallback)
    document.addEventListener('click', (e) => {
      if (e.target.matches('[onclick*="nextSection"]')) {
        e.preventDefault();
        const match = e.target.onclick.toString().match(/nextSection\((\d+)\)/);
        if (match) {
          const section = parseInt(match[1]);
          this.nextSection(section);
        }
      }

      if (e.target.matches('[onclick*="prevSection"]')) {
        e.preventDefault();
        const match = e.target.onclick.toString().match(/prevSection\((\d+)\)/);
        if (match) {
          const section = parseInt(match[1]);
          this.prevSection(section);
        }
      }
    });
  }

  /**
   * Configurar listeners para inputs
   */
  setupInputListeners() {
    if (!this.form) return;

    let debounceTimer;
    let isCollecting = false;

    // Função debounced para evitar múltiplas execuções
    const debouncedCollect = () => {
      if (isCollecting) return; // Evitar execução simultânea

      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        isCollecting = true;

        try {
          this.collectSectionData();
          this.clearAutoSave();
          this.scheduleAutoSave();

          // Atualizar resumo se estivermos na seção 3
          if (this.currentSection === 3) {
            this.updateSummary();
          }
        } catch (error) {
          console.error('Erro ao coletar dados:', error);
        } finally {
          isCollecting = false;
        }
      }, 500); // Aumentar para 500ms
    };

    // Auto-save on input change (debounced) - apenas uma vez
    this.form.addEventListener('input', debouncedCollect, { once: false, passive: true });
    this.form.addEventListener('change', debouncedCollect, { once: false, passive: true });

    console.log('Input listeners configurados com debounce');
  }

  /**
   * Configurar listeners da calculadora
   */
  setupCalculatorListeners() {
    // Inputs da calculadora
    ['calc-longueur', 'calc-largeur', 'calc-hauteur'].forEach((id) => {
      const input = document.getElementById(id);
      if (input) {
        input.addEventListener('input', () => {
          this.calculateAutoPreview();
        });
      }
    });
  }

  /**
   * Configurar listeners do modal de ajuda
   */
  setupHelpModalListeners() {
    // Botões de fechar modal
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-close-help]') || e.target.closest('[data-close-help]')) {
        this.closeHelp();
      }
    });

    // Fechar modal ao clicar fora
    document.addEventListener('click', (e) => {
      const modal = document.getElementById('help-modal');
      if (e.target === modal) {
        this.closeHelp();
      }
    });
  }

  /**
   * Navegar para próxima seção
   */
  nextSection(targetSection) {
    console.log(`nextSection called: ${this.currentSection} -> ${targetSection}`);

    // Coletar dados da seção atual
    this.collectSectionData();

    // Validar seção atual
    if (!this.validateCurrentSection()) {
      console.log('Validação falhou, permanecendo na seção atual');
      return false;
    }

    // Avançar para próxima seção
    this.currentSection = targetSection;
    this.showSection(targetSection);
    this.updateUI();
    this.focusFirstField();

    return true;
  }

  /**
   * Navegar para seção anterior
   */
  prevSection(targetSection) {
    console.log(`prevSection called: ${this.currentSection} -> ${targetSection}`);

    // Coletar dados antes de voltar
    this.collectSectionData();

    // Voltar para seção anterior
    this.currentSection = targetSection;
    this.showSection(targetSection);
    this.updateUI();
    this.focusFirstField();

    return true;
  }

  /**
   * Mostrar seção específica
   */
  showSection(sectionNum) {
    console.log(`Mostrando seção ${sectionNum}`);

    // Esconder todas as seções
    for (let i = 1; i <= this.totalSections; i++) {
      const section = document.getElementById(`section-${i}`);
      if (section) {
        section.classList.add('hidden');
      }
    }

    // Mostrar seção alvo
    const targetSection = document.getElementById(`section-${sectionNum}`);
    if (targetSection) {
      targetSection.classList.remove('hidden');

      // Se for seção 3, atualizar resumo
      if (sectionNum === 3) {
        setTimeout(() => this.updateSummary(), 100);
      }
    }
  }

  /**
   * Coletar dados da seção atual
   */
  collectSectionData() {
    if (!this.form) return;

    const formData = new FormData(this.form);

    // Coletar todos os campos do formulário
    for (let [key, value] of formData.entries()) {
      this.formData.set(key, value);
    }

    // Coletar checkboxes não marcados
    const checkboxes = this.form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((cb) => {
      if (!cb.checked) {
        this.formData.set(cb.name, false);
      }
    });

    console.log('Dados coletados:', Object.fromEntries(this.formData));
  }

  /**
   * Validar seção atual
   */
  validateCurrentSection() {
    const sectionElement = document.getElementById(`section-${this.currentSection}`);
    if (!sectionElement) return true;

    // Buscar campos obrigatórios na seção atual
    const requiredFields = sectionElement.querySelectorAll('[required]');
    let isValid = true;
    const errors = [];

    console.log(
      `Validando ${requiredFields.length} campos obrigatórios na seção ${this.currentSection}`
    );

    requiredFields.forEach((field) => {
      const value = this.getFieldValue(field);
      const isEmpty = this.isFieldEmpty(field, value);

      if (isEmpty) {
        isValid = false;
        const label = this.getFieldLabel(field);
        errors.push(`${label} est requis`);

        // Marcar campo com erro
        field.classList.add('border-red-500');
      } else {
        // Remover marca de erro
        field.classList.remove('border-red-500');
      }
    });

    // Validações específicas por seção
    if (this.currentSection === 1) {
      isValid = this.validateSection1() && isValid;
    } else if (this.currentSection === 2) {
      isValid = this.validateSection2() && isValid;
    } else if (this.currentSection === 3) {
      isValid = this.validateSection3() && isValid;
    }

    if (!isValid) {
      this.showValidationErrors(errors);
    } else {
      this.hideValidationErrors();
    }

    console.log(`Validação seção ${this.currentSection}: ${isValid ? 'OK' : 'ERRO'}`);
    return isValid;
  }

  /**
   * Obter valor do campo
   */
  getFieldValue(field) {
    if (field.type === 'checkbox' || field.type === 'radio') {
      return field.checked;
    }
    return field.value?.trim();
  }

  /**
   * Verificar se campo está vazio
   */
  isFieldEmpty(field, value) {
    if (field.type === 'checkbox' || field.type === 'radio') {
      return !value;
    }
    return !value || (field.tagName === 'SELECT' && field.value === '');
  }

  /**
   * Obter label do campo
   */
  getFieldLabel(field) {
    const label = this.form.querySelector(`label[for="${field.id}"]`);
    if (label) {
      return label.textContent.replace('*', '').trim();
    }
    return field.name || field.id || 'Campo';
  }

  /**
   * Validações específicas da seção 1
   */
  validateSection1() {
    let isValid = true;

    // Verificar se pelo menos uma peça foi selecionada
    const pieceCheckboxes = document.querySelectorAll('input[name^="pieces_"]:checked');
    if (pieceCheckboxes.length === 0) {
      isValid = false;
      this.showError('Au moins une pièce doit être sélectionnée');
    }

    return isValid;
  }

  /**
   * Validações específicas da seção 2
   */
  validateSection2() {
    let isValid = true;

    // Validar coerência das superfícies
    const surfaceTotal = parseFloat(document.getElementById('id_surface_totale')?.value || 0);
    const surfaceMurs = parseFloat(document.getElementById('id_surface_murs')?.value || 0);
    const surfacePlafond = parseFloat(document.getElementById('id_surface_plafond')?.value || 0);

    if (surfaceTotal > 0 && surfaceMurs + surfacePlafond > surfaceTotal * 4) {
      isValid = false;
      this.showError('Les surfaces semblent incohérentes');
    }

    return isValid;
  }

  /**
   * Validações específicas da seção 3
   */
  validateSection3() {
    let isValid = true;
    const errors = [];
    console.log('🔍 Validando seção 3...');
    // Verificar campos obrigatórios específicos da seção 3
    const requiredFieldsData = [
      { id: 'id_title', label: 'Titre', required: true },
      { id: 'id_description', label: 'Description', required: true },
      { id: 'id_type_projet', label: 'Type de projet', required: true },
      { id: 'id_surface_totale', label: 'Surface totale', required: true },
      { id: 'id_adresse_travaux', label: 'Adresse des travaux', required: true },
      { id: 'id_ville', label: 'Ville', required: true },
      { id: 'id_code_postal', label: 'Code postal', required: true },
      { id: 'id_contact_telephone', label: 'Téléphone de contact', required: true },
      { id: 'id_date_debut_souhaitee', label: 'Date de début souhaitée', required: true },
      { id: 'id_date_fin_souhaitee', label: 'Date de fin souhaitée', required: true },
      { id: 'id_budget_minimum', label: 'Budget minimum', required: true },
      { id: 'id_budget_maximum', label: 'Budget maximum', required: true },
    ];

    // Validar campos obrigatórios
    requiredFieldsData.forEach(({ id, label, required }) => {
      const field = document.getElementById(id);
      console.log(
        `Verificando campo ${id}:`,
        field ? `valor="${field.value}"` : 'CAMPO NÃO ENCONTRADO'
      );

      if (!field) {
        if (required) {
          console.error(`❌ Campo obrigatório ${id} não encontrado no DOM`);
          isValid = false;
          errors.push(`Campo ${label} não encontrado`);
        }
        return;
      }

      if (required && (!field.value || field.value.trim() === '')) {
        isValid = false;
        field.classList.add('border-red-500');
        errors.push(`${label} est requis`);
        console.log(`❌ Campo ${id} está vazio`);
      } else {
        field.classList.remove('border-red-500');
        console.log(`✅ Campo ${id} OK`);
      }
    });

    // Validar que pelo menos uma peça foi selecionada
    const pieces = [
      'pieces_salon',
      'pieces_cuisine',
      'pieces_chambre',
      'pieces_salle_de_bain',
      'pieces_bureau',
      'pieces_couloir',
      'pieces_exterieur',
    ];

    const selectedPieces = pieces.filter((name) => {
      const field = document.querySelector(`input[name="${name}"]`);
      return field && field.checked;
    });

    if (selectedPieces.length === 0) {
      isValid = false;
      errors.push('Vous devez sélectionner au moins une pièce');
      console.log('❌ Nenhuma peça selecionada');
    } else {
      console.log(`✅ Peças selecionadas: ${selectedPieces.join(', ')}`);
    }

    // Validações adicionais (budget, datas)
    this.validateBudgetAndDates(errors);

    if (errors.length > 0) {
      console.log('❌ Seção 3 com erros:', errors);
      this.showValidationErrors(errors);
    } else {
      console.log('✅ Seção 3 validada com sucesso');
    }

    return isValid;
  }

  // ✅ ADICIONAR função auxiliar para validações de budget e datas
  validateBudgetAndDates(errors) {
    // Validar budget
    const budgetMinField = document.getElementById('id_budget_minimum');
    const budgetMaxField = document.getElementById('id_budget_maximum');

    if (budgetMinField && budgetMaxField) {
      const budgetMin = parseFloat(budgetMinField.value || 0);
      const budgetMax = parseFloat(budgetMaxField.value || 0);

      if (budgetMin > 0 && budgetMax > 0 && budgetMin >= budgetMax) {
        budgetMinField.classList.add('border-red-500');
        budgetMaxField.classList.add('border-red-500');
        errors.push('Le budget minimum doit être inférieur au budget maximum');
      } else {
        budgetMinField.classList.remove('border-red-500');
        budgetMaxField.classList.remove('border-red-500');
      }
    }

    // Validar datas
    const dateDebutField = document.getElementById('id_date_debut_souhaitee');
    const dateFinField = document.getElementById('id_date_fin_souhaitee');

    if (dateDebutField && dateFinField) {
      const dateDebut = dateDebutField.value;
      const dateFin = dateFinField.value;

      if (dateDebut && dateFin && new Date(dateDebut) >= new Date(dateFin)) {
        dateDebutField.classList.add('border-red-500');
        dateFinField.classList.add('border-red-500');
        errors.push('La date de début doit être antérieure à la date de fin');
      } else {
        dateDebutField.classList.remove('border-red-500');
        dateFinField.classList.remove('border-red-500');
      }
    }
  }

  debugFormFields() {
    console.log('=== DEBUG FORM FIELDS ===');

    // Verificar todos os campos obrigatórios
    const allRequiredFields = [
      'id_title',
      'id_description',
      'id_type_projet',
      'id_surface_totale',
      'id_adresse_travaux',
      'id_ville',
      'id_code_postal',
      'id_contact_telephone',
      'id_date_debut_souhaitee',
      'id_date_fin_souhaitee',
      'id_budget_minimum',
      'id_budget_maximum',
    ];

    allRequiredFields.forEach((id) => {
      const field = document.getElementById(id);
      if (!field) {
        console.error(`❌ CAMPO FALTANDO: ${id}`);
      } else {
        const value = field.value || '';
        const isEmpty = value.trim() === '';
        console.log(`${isEmpty ? '❌' : '✅'} ${id}: "${value}"`);
      }
    });

    // Verificar checkboxes
    ['accept_conditions', 'accept_contact'].forEach((id) => {
      const field = document.getElementById(id);
      if (!field) {
        console.error(`❌ CHECKBOX FALTANDO: ${id}`);
      } else {
        console.log(`${field.checked ? '✅' : '❌'} ${id}: ${field.checked}`);
      }
    });

    // Verificar peças selecionadas
    const pieces = [
      'pieces_salon',
      'pieces_cuisine',
      'pieces_chambre',
      'pieces_salle_de_bain',
      'pieces_bureau',
      'pieces_couloir',
      'pieces_exterieur',
    ];
    const selectedPieces = pieces.filter((name) => {
      const field = document.querySelector(`input[name="${name}"]`);
      return field && field.checked;
    });

    console.log(
      `Peças selecionadas: ${selectedPieces.length > 0 ? '✅' : '❌'} [${selectedPieces.join(
        ', '
      )}]`
    );

    // Verificar token CSRF
    const csrf = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
    console.log(
      `Token CSRF: ${csrf && csrf.value ? '✅' : '❌'} ${csrf?.value?.substring(0, 10)}...`
    );
  }

  // ... outros métodos da classe

  /**
   * Mostrar erros de validação
   */
  showValidationErrors(errors) {
    const summaryElement = document.getElementById('validation-summary');
    const errorsElement = document.getElementById('validation-errors');

    if (summaryElement && errorsElement && errors.length > 0) {
      errorsElement.innerHTML = errors.map((error) => `<li>${error}</li>`).join('');
      summaryElement.classList.remove('hidden');

      // Scroll para o topo para mostrar erros
      summaryElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  /**
   * Esconder erros de validação
   */
  hideValidationErrors() {
    const summaryElement = document.getElementById('validation-summary');
    if (summaryElement) {
      summaryElement.classList.add('hidden');
    }
  }

  /**
   * Mostrar erro específico
   */
  showError(message) {
    const summaryElement = document.getElementById('validation-summary');
    const errorsElement = document.getElementById('validation-errors');

    if (summaryElement && errorsElement) {
      errorsElement.innerHTML = `<li>${message}</li>`;
      summaryElement.classList.remove('hidden');
    }
  }

  /**
   * Atualizar UI (progress bar, steps, etc.)
   */
  updateUI() {
    this.updateProgressBar();
    this.updateStepsIndicator();
  }

  /**
   * Atualizar barra de progresso
   */
  updateProgressBar() {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (progressBar && progressText) {
      const percentage = Math.round((this.currentSection / this.totalSections) * 100);
      progressBar.style.width = `${percentage}%`;
      progressText.textContent = `Étape ${this.currentSection} sur ${this.totalSections} (${percentage}%)`;
    }
  }

  /**
   * Atualizar indicador de etapas
   */
  updateStepsIndicator() {
    for (let i = 1; i <= this.totalSections; i++) {
      const circle = document.getElementById(`circle-${i}`);
      const step = document.getElementById(`step-${i}`);

      if (circle && step) {
        if (i < this.currentSection) {
          // Etapa concluída
          circle.className =
            'flex items-center justify-center w-10 h-10 rounded-full bg-green-600 text-white text-sm font-bold';
          circle.innerHTML = '<i class="fas fa-check"></i>';
        } else if (i === this.currentSection) {
          // Etapa atual
          circle.className =
            'flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-sm font-bold';
          circle.textContent = i;
        } else {
          // Etapa futura
          circle.className =
            'flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 text-gray-600 text-sm font-bold';
          circle.textContent = i;
        }
      }
    }

    // Atualizar linhas de progresso
    const line1 = document.getElementById('line-1');
    const line2 = document.getElementById('line-2');

    if (line1) {
      line1.className =
        this.currentSection > 1
          ? 'flex-1 h-1 mx-4 bg-green-500 rounded-full'
          : 'flex-1 h-1 mx-4 bg-gray-200 rounded-full';
    }

    if (line2) {
      line2.className =
        this.currentSection > 2
          ? 'flex-1 h-1 mx-4 bg-green-500 rounded-full'
          : 'flex-1 h-1 mx-4 bg-gray-200 rounded-full';
    }
  }

  /**
   * Atualizar resumo do projeto (seção 3)
   */
  updateSummary() {
    const summaryElement = document.getElementById('project-summary');
    if (!summaryElement) return;

    const data = Object.fromEntries(this.formData);

    // Gerar HTML do resumo
    const summaryHTML = this.generateSummaryHTML(data);
    summaryElement.innerHTML = summaryHTML;
  }

  /**
   * Gerar HTML do resumo
   */
  generateSummaryHTML(data) {
    const pieces = this.getSelectedPieces(data);

    return `
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 class="font-semibold text-blue-900 mb-3">Informations générales</h4>
          <ul class="space-y-2 text-sm">
            <li><strong>Titre:</strong> ${data.title || 'Non spécifié'}</li>
            <li><strong>Type:</strong> ${this.getTypeLabel(data.type_projet)}</li>
            <li><strong>Description:</strong> ${(data.description || 'Non spécifiée').substring(
              0,
              100
            )}${data.description?.length > 100 ? '...' : ''}</li>
          </ul>
        </div>
        
        <div>
          <h4 class="font-semibold text-blue-900 mb-3">Détails techniques</h4>
          <ul class="space-y-2 text-sm">
            <li><strong>Surface totale:</strong> ${data.surface_totale || '0'} m²</li>
            <li><strong>Nombre de pièces:</strong> ${data.nombre_pieces || '1'}</li>
            <li><strong>Pièces concernées:</strong> ${pieces.join(', ') || 'Non spécifiées'}</li>
          </ul>
        </div>
        
        <div>
          <h4 class="font-semibold text-blue-900 mb-3">Localisation</h4>
          <ul class="space-y-2 text-sm">
            <li><strong>Adresse:</strong> ${data.adresse_travaux || 'Non spécifiée'}</li>
            <li><strong>Ville:</strong> ${data.ville || 'Non spécifiée'}</li>
            <li><strong>Code postal:</strong> ${data.code_postal || 'Non spécifié'}</li>
          </ul>
        </div>
        
        <div>
          <h4 class="font-semibold text-blue-900 mb-3">Budget et planning</h4>
          <ul class="space-y-2 text-sm">
            <li><strong>Budget:</strong> ${data.budget_minimum || '0'}€ - ${
      data.budget_maximum || '0'
    }€</li>
            <li><strong>Début souhaité:</strong> ${data.date_debut_souhaitee || 'Non spécifié'}</li>
            <li><strong>Fin souhaitée:</strong> ${data.date_fin_souhaitee || 'Non spécifiée'}</li>
          </ul>
        </div>
      </div>
    `;
  }

  /**
   * Obter peças selecionadas
   */
  getSelectedPieces(data) {
    const pieces = [];
    const pieceMap = {
      pieces_salon: 'Salon',
      pieces_cuisine: 'Cuisine',
      pieces_chambre: 'Chambre',
      pieces_salle_de_bain: 'Salle de bain',
      pieces_bureau: 'Bureau',
      pieces_couloir: 'Couloir',
    };

    Object.keys(pieceMap).forEach((key) => {
      if (data[key] === 'on' || data[key] === true) {
        pieces.push(pieceMap[key]);
      }
    });

    return pieces;
  }

  /**
   * Obter label do tipo de projeto
   */
  getTypeLabel(typeValue) {
    const typeMap = {
      peinture_interieure: 'Peinture intérieure',
      peinture_exterieure: 'Peinture extérieure',
      renovation_complete: 'Rénovation complète',
      ravalement_facade: 'Ravalement de façade',
    };
    return typeMap[typeValue] || typeValue;
  }

  /**
   * Processar submit do formulário
   */
  handleSubmit(event) {
    console.log('🚀 PROCESSANDO SUBMIT DO FORMULÁRIO');
    console.log('Event:', event);
    console.log('Current section:', this.currentSection);
    console.log('Is submitting:', this.isSubmitting);

    // Evitar submissão múltipla
    if (this.isSubmitting) {
      console.log('❌ Já está enviando, cancelando');
      event.preventDefault();
      return false;
    }

    // Verificar se estamos na seção 3
    if (this.currentSection !== 3) {
      console.log('❌ Não está na seção final, indo para seção 3');
      event.preventDefault();
      this.nextSection(3);
      return false;
    }

    // ✅ VALIDAÇÃO ESPECIAL PARA CHECKBOXES OBRIGATÓRIOS
    const conditionsField = document.getElementById('accept_conditions');
    const contactField = document.getElementById('accept_contact');

    if (!conditionsField || !conditionsField.checked) {
      event.preventDefault();
      this.showError('Vous devez accepter les conditions générales');
      return false;
    }

    if (!contactField || !contactField.checked) {
      event.preventDefault();
      this.showError("Vous devez accepter d'être contacté");
      return false;
    }

    // Coletar dados finais
    this.collectSectionData();
    console.log('📊 Dados coletados:', Object.fromEntries(this.formData));

    // Verificar token CSRF
    const csrfInput = this.form.querySelector('input[name="csrfmiddlewaretoken"]');
    if (!csrfInput || !csrfInput.value) {
      console.error('❌ Token CSRF não encontrado!');
      event.preventDefault();
      this.showError('Erreur de sécurité (CSRF). Veuillez recharger la page.');
      return false;
    }

    // Validar seção 3 novamente
    if (!this.validateSection3()) {
      console.log('❌ Validação da seção 3 falhou');
      event.preventDefault();
      return false;
    }

    // Marcar como enviando
    console.log('✅ Validação OK, enviando formulário...');
    this.isSubmitting = true;
    this.updateSubmitButton();
    this.showSubmitIndicator();

    // Permitir envio nativo do formulário
    console.log('🎯 Formulário sendo enviado para Django');
    return true;
  }
  /**
   * Validar formulário completo
   */
  validateCompleteForm() {
    let isValid = true;
    const errors = [];

    // Validar todas as seções
    for (let i = 1; i <= this.totalSections; i++) {
      const prevSection = this.currentSection;
      this.currentSection = i;

      if (!this.validateCurrentSection()) {
        isValid = false;
        errors.push(`Erreurs dans la section ${i}`);
      }

      this.currentSection = prevSection;
    }

    if (!isValid) {
      this.showValidationErrors(errors);
      // Ir para primeira seção com erro
      this.currentSection = 1;
      this.showSection(1);
      this.updateUI();
    }

    return isValid;
  }

  /**
   * Atualizar botão de submit
   */
  updateSubmitButton() {
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Envoi en cours...';
    }
  }

  /**
   * Mostrar indicador de submit
   */
  showSubmitIndicator() {
    let overlay = document.getElementById('submit-overlay');
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.id = 'submit-overlay';
      overlay.className =
        'fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50';
      overlay.innerHTML = `
        <div class="bg-white rounded-lg p-8 shadow-xl max-w-md mx-4">
          <div class="flex items-center gap-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <div>
              <h3 class="font-semibold text-gray-900 text-lg">Envoi du projet en cours</h3>
              <p class="text-sm text-gray-600 mt-1">Veuillez patienter...</p>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(overlay);
    }
    overlay.classList.remove('hidden');
  }

  /**
   * Calculadora de superfície
   */
  calculateSurface() {
    const longueur = parseFloat(document.getElementById('calc-longueur')?.value || 0);
    const largeur = parseFloat(document.getElementById('calc-largeur')?.value || 0);
    const hauteur = parseFloat(document.getElementById('calc-hauteur')?.value || 2.5);

    if (longueur > 0 && largeur > 0) {
      const surfaceSol = longueur * largeur;
      const surfaceMurs = 2 * (longueur + largeur) * hauteur;
      const surfacePlafond = surfaceSol;

      // Atualizar resultados
      document.getElementById('result-sol').textContent = `${surfaceSol.toFixed(2)} m²`;
      document.getElementById('result-murs').textContent = `${surfaceMurs.toFixed(2)} m²`;
      document.getElementById('result-plafond').textContent = `${surfacePlafond.toFixed(2)} m²`;

      // Mostrar botão aplicar
      const applyBtn = document.getElementById('apply-calculation');
      if (applyBtn) {
        applyBtn.classList.remove('hidden');
      }
    }
  }

  /**
   * Aplicar cálculo de superfície
   */
  applySurfaceCalculation() {
    const surfaceSol = parseFloat(document.getElementById('result-sol')?.textContent || 0);
    const surfaceMurs = parseFloat(document.getElementById('result-murs')?.textContent || 0);
    const surfacePlafond = parseFloat(document.getElementById('result-plafond')?.textContent || 0);

    // Aplicar valores aos campos
    const totalField = document.getElementById('id_surface_totale');
    const mursField = document.getElementById('id_surface_murs');
    const plafondField = document.getElementById('id_surface_plafond');

    if (totalField) totalField.value = surfaceSol.toFixed(2);
    if (mursField) mursField.value = surfaceMurs.toFixed(2);
    if (plafondField) plafondField.value = surfacePlafond.toFixed(2);

    // Coletar dados atualizados
    this.collectSectionData();

    // Feedback visual
    this.showAutoSaveIndicator('Surfaces calculées et appliquées');
  }

  /**
   * Preview automático da calculadora
   */
  calculateAutoPreview() {
    // Calcular automaticamente enquanto o usuário digita
    setTimeout(() => this.calculateSurface(), 300);
  }

  /**
   * Modal de ajuda
   */
  showHelp() {
    const modal = document.getElementById('help-modal');
    if (modal) {
      modal.classList.remove('hidden');
    }
  }

  closeHelp() {
    const modal = document.getElementById('help-modal');
    if (modal) {
      modal.classList.add('hidden');
    }
  }

  /**
   * Auto-save functionality
   */
  setupAutoSave() {
    // Carregar dados salvos ao inicializar
    this.loadFormData();

    // Configurar intervalo de auto-save
    setInterval(() => {
      if (this.formData.size > 0) {
        this.saveFormDataLocally();
      }
    }, 30000); // Auto-save a cada 30 segundos
  }

  scheduleAutoSave() {
    this.clearAutoSave();
    this.autoSaveTimeout = setTimeout(() => {
      this.saveFormDataLocally();
      this.showAutoSaveIndicator();
    }, 2000);
  }

  clearAutoSave() {
    if (this.autoSaveTimeout) {
      clearTimeout(this.autoSaveTimeout);
    }
  }

  saveFormDataLocally() {
    try {
      const dataToSave = {
        currentSection: this.currentSection,
        formData: Object.fromEntries(this.formData),
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem('project_form_data', JSON.stringify(dataToSave));
    } catch (e) {
      console.warn('Erro ao salvar dados localmente:', e);
    }
  }

  loadFormData() {
    try {
      const savedData = localStorage.getItem('project_form_data');
      if (savedData) {
        const data = JSON.parse(savedData);

        // Restaurar dados do formulário
        if (data.formData) {
          Object.entries(data.formData).forEach(([key, value]) => {
            const field = this.form.querySelector(`[name="${key}"]`);
            if (field) {
              if (field.type === 'checkbox') {
                field.checked = value === true || value === 'on';
              } else {
                field.value = value;
              }
            }
          });

          // Atualizar mapa de dados
          this.formData = new Map(Object.entries(data.formData));
        }

        console.log('Dados carregados do localStorage');
      }
    } catch (e) {
      console.warn('Erro ao carregar dados salvos:', e);
    }
  }

  clearSavedData() {
    try {
      localStorage.removeItem('project_form_data');
    } catch (e) {
      console.warn('Erro ao limpar dados salvos:', e);
    }
  }

  showAutoSaveIndicator(message = 'Sauvegarde automatique') {
    const indicator = document.getElementById('auto-save-indicator');
    if (indicator) {
      indicator.querySelector('span').textContent = message;
      indicator.style.opacity = '1';
      setTimeout(() => {
        indicator.style.opacity = '0';
      }, 2000);
    }
  }

  focusFirstField() {
    setTimeout(() => {
      const currentSection = document.getElementById(`section-${this.currentSection}`);
      if (currentSection) {
        const firstInput = currentSection.querySelector(
          'input:not([type="hidden"]), select, textarea'
        );
        if (firstInput) {
          firstInput.focus();
        }
      }
    }, 100);
  }
}

// ================================
// SUBSTITUIR O FINAL DO ARQUIVO (após a classe ProjectCreateController)
// ================================

// ================================
// FUNÇÕES GLOBAIS DE DEBUG E TESTE
// ================================

/**
 * Função para preencher dados de teste
 */
function fillTestData() {
  console.log('🔧 Preenchendo dados de teste...');

  try {
    // Dados básicos (Seção 1)
    const titleField = document.getElementById('id_title');
    const descField = document.getElementById('id_description');
    const typeField = document.getElementById('id_type_projet');
    const surfaceField = document.getElementById('id_surface_totale');

    if (titleField) titleField.value = 'Projeto de Teste';
    if (descField)
      descField.value =
        'Descrição detalhada do projeto de teste para validação do formulário com mais de 20 caracteres.';
    if (typeField) typeField.value = 'peinture_interieure';
    if (surfaceField) surfaceField.value = '50';

    // Peças (Seção 1)
    const salonCheckbox = document.querySelector('input[name="pieces_salon"]');
    const cuisineCheckbox = document.querySelector('input[name="pieces_cuisine"]');

    if (salonCheckbox) salonCheckbox.checked = true;
    if (cuisineCheckbox) cuisineCheckbox.checked = true;

    // Localização (Seção 3)
    const adresseField = document.getElementById('id_adresse_travaux');
    const villeField = document.getElementById('id_ville');
    const codePostalField = document.getElementById('id_code_postal');
    const telephoneField = document.getElementById('id_contact_telephone');

    if (adresseField) adresseField.value = '123 Rue de Test';
    if (villeField) villeField.value = 'Cidade Teste';
    if (codePostalField) codePostalField.value = '12345';
    if (telephoneField) telephoneField.value = '+33123456789';

    // Datas e budget (Seção 3)
    const dateDebutField = document.getElementById('id_date_debut_souhaitee');
    const dateFinField = document.getElementById('id_date_fin_souhaitee');
    const budgetMinField = document.getElementById('id_budget_minimum');
    const budgetMaxField = document.getElementById('id_budget_maximum');

    if (dateDebutField) dateDebutField.value = '2024-02-01';
    if (dateFinField) dateFinField.value = '2024-03-01';
    if (budgetMinField) budgetMinField.value = '2000';
    if (budgetMaxField) budgetMaxField.value = '5000';

    // Checkboxes obrigatórios (Seção 3)
    const conditionsCheckbox = document.getElementById('accept_conditions');
    const contactCheckbox = document.getElementById('accept_contact');

    if (conditionsCheckbox) conditionsCheckbox.checked = true;
    if (contactCheckbox) contactCheckbox.checked = true;

    console.log('✅ Dados de teste preenchidos!');

    // Coletar dados no controller se existir
    if (window.projectCreateController) {
      window.projectCreateController.collectSectionData();
    }
  } catch (error) {
    console.error('❌ Erro ao preencher dados de teste:', error);
  }
}
/**
 * Função para debug detalhado da seção 3
 */
function debugSection3() {
  console.log('=== DEBUG SEÇÃO 3 ===');

  const requiredFieldsSection3 = [
    'id_adresse_travaux',
    'id_ville',
    'id_code_postal',
    'id_contact_telephone',
    'id_date_debut_souhaitee',
    'id_date_fin_souhaitee',
    'id_budget_minimum',
    'id_budget_maximum',
  ];

  console.log('Campos obrigatórios na seção 3:');
  requiredFieldsSection3.forEach((id) => {
    const field = document.getElementById(id);
    if (!field) {
      console.error(`❌ CAMPO FALTANDO: ${id}`);
    } else {
      const value = field.value || '';
      const isEmpty = value.trim() === '';
      const hasRequired = field.hasAttribute('required');
      console.log(`${isEmpty ? '❌' : '✅'} ${id}: "${value}" (required: ${hasRequired})`);
    }
  });

  // Debug checkboxes
  ['accept_conditions', 'accept_contact'].forEach((id) => {
    const field = document.getElementById(id);
    if (!field) {
      console.error(`❌ CHECKBOX FALTANDO: ${id}`);
    } else {
      console.log(`${field.checked ? '✅' : '❌'} ${id}: ${field.checked}`);
    }
  });
}

/**
 * Função para testar validação completa
 */
function testFormValidation() {
  console.log('=== TESTE DE VALIDAÇÃO COMPLETO ===');

  const controller = window.projectCreateController;
  if (!controller) {
    console.error('❌ Controller não encontrado!');
    return;
  }

  // Executar debug dos campos
  controller.debugFormFields();

  // Testar validação de cada seção
  for (let i = 1; i <= 3; i++) {
    console.log(`\n--- TESTANDO SEÇÃO ${i} ---`);
    const prevSection = controller.currentSection;
    controller.currentSection = i;

    const isValid = controller.validateCurrentSection();
    console.log(`Seção ${i}: ${isValid ? '✅ VÁLIDA' : '❌ INVÁLIDA'}`);

    controller.currentSection = prevSection;
  }

  // Testar validação completa
  console.log('\n--- VALIDAÇÃO COMPLETA ---');
  const isCompletelyValid = controller.validateCompleteForm();
  console.log(`Formulário completo: ${isCompletelyValid ? '✅ VÁLIDO' : '❌ INVÁLIDO'}`);
}

/**
 * Função para debug dos campos do formulário
 */
function debugFormFields() {
  console.log('=== DEBUG FORM FIELDS ===');

  // Verificar todos os campos obrigatórios
  const allRequiredFields = [
    'id_title',
    'id_description',
    'id_type_projet',
    'id_surface_totale',
    'id_adresse_travaux',
    'id_ville',
    'id_code_postal',
    'id_contact_telephone',
    'id_date_debut_souhaitee',
    'id_date_fin_souhaitee',
    'id_budget_minimum',
    'id_budget_maximum',
  ];

  allRequiredFields.forEach((id) => {
    const field = document.getElementById(id);
    if (!field) {
      console.error(`❌ CAMPO FALTANDO: ${id}`);
    } else {
      const value = field.value || '';
      const isEmpty = value.trim() === '';
      console.log(`${isEmpty ? '❌' : '✅'} ${id}: "${value}"`);
    }
  });

  // Verificar checkboxes
  ['accept_conditions', 'accept_contact'].forEach((id) => {
    const field = document.getElementById(id);
    if (!field) {
      console.error(`❌ CHECKBOX FALTANDO: ${id}`);
    } else {
      console.log(`${field.checked ? '✅' : '❌'} ${id}: ${field.checked}`);
    }
  });

  // Verificar peças selecionadas
  const pieces = [
    'pieces_salon',
    'pieces_cuisine',
    'pieces_chambre',
    'pieces_salle_de_bain',
    'pieces_bureau',
    'pieces_couloir',
    'pieces_exterieur',
  ];
  const selectedPieces = pieces.filter((name) => {
    const field = document.querySelector(`input[name="${name}"]`);
    return field && field.checked;
  });

  console.log(
    `Peças selecionadas: ${selectedPieces.length > 0 ? '✅' : '❌'} [${selectedPieces.join(', ')}]`
  );

  // Verificar token CSRF
  const form = document.getElementById('project-form');
  const csrf = form?.querySelector('input[name="csrfmiddlewaretoken"]');
  console.log(
    `Token CSRF: ${csrf && csrf.value ? '✅' : '❌'} ${csrf?.value?.substring(0, 10)}...`
  );
}

/**
 * Função para forçar submissão do formulário
 */
function forceSubmitForm() {
  console.log('🔧 FORÇANDO SUBMISSÃO MANUAL');

  const form = document.getElementById('project-form');
  const controller = window.projectCreateController;

  if (!form) {
    console.error('❌ Formulário não encontrado!');
    return;
  }

  if (!controller) {
    console.error('❌ Controller não encontrado!');
    return;
  }

  // Ir para seção 3
  controller.currentSection = 3;
  controller.showSection(3);

  // Coletar dados
  controller.collectSectionData();
  console.log('Dados coletados:', Object.fromEntries(controller.formData));

  // Preencher campos obrigatórios se estiverem vazios (para teste)
  const requiredDefaults = {
    id_adresse_travaux: 'Test Address 123',
    id_ville: 'Test City',
    id_code_postal: '12345',
    id_contact_telephone: '+33123456789',
    id_budget_minimum: '1000',
    id_budget_maximum: '5000',
    id_date_debut_souhaitee: '2024-01-01',
    id_date_fin_souhaitee: '2024-02-01',
  };

  Object.entries(requiredDefaults).forEach(([id, value]) => {
    const field = document.getElementById(id);
    if (field && !field.value) {
      field.value = value;
      console.log(`Preenchido ${id} com: ${value}`);
    }
  });

  // Marcar checkboxes obrigatórios
  const conditionsCheckbox = document.getElementById('accept_conditions');
  const contactCheckbox = document.getElementById('accept_contact');

  if (conditionsCheckbox) conditionsCheckbox.checked = true;
  if (contactCheckbox) contactCheckbox.checked = true;

  // Tentar submeter
  console.log('Tentando submeter formulário...');
  form.submit();
}

/**
 * Função de debug geral
 */
function debugProjectForm() {
  console.log('=== DEBUG PROJECT FORM ===');
  console.log('Controller:', window.projectCreateController);
  console.log('Form:', document.getElementById('project-form'));
  console.log('Submit button:', document.getElementById('submit-btn'));

  if (window.projectCreateController) {
    console.log('Current section:', window.projectCreateController.currentSection);
    console.log('Form data:', Object.fromEntries(window.projectCreateController.formData));
    console.log('Is submitting:', window.projectCreateController.isSubmitting);
  }
}

// ================================
// EXPOR FUNÇÕES GLOBALMENTE (apenas uma vez)
// ================================
// ================================
// EXPOR FUNÇÕES GLOBALMENTE
// ================================
window.fillTestData = fillTestData;
window.testFormValidation = testFormValidation;
window.forceSubmitForm = forceSubmitForm;
window.debugSection3 = debugSection3;

console.log('✅ Funções de debug disponíveis:');
console.log('   - fillTestData()');
console.log('   - testFormValidation()');
console.log('   - forceSubmitForm()');
console.log('   - debugSection3()');

// ================================
// INICIALIZAÇÃO (apenas uma vez)
// ================================
function initProjectController() {
  console.log('Inicializando ProjectCreateController...');

  if (typeof ProjectCreateController === 'undefined') {
    console.error('Classe ProjectCreateController não está definida!');
    return;
  }

  // Criar instância global do controller
  window.projectCreateController = new ProjectCreateController();

  // Função de debug global
  window.debugProjectForm = function () {
    console.log('=== DEBUG PROJECT FORM ===');
    console.log('Controller:', window.projectCreateController);
    console.log('Form:', document.getElementById('project-form'));
    console.log('Submit button:', document.getElementById('submit-btn'));
    if (window.projectCreateController) {
      console.log('Current section:', window.projectCreateController.currentSection);
      console.log('Form data:', Object.fromEntries(window.projectCreateController.formData));
      console.log('Is submitting:', window.projectCreateController.isSubmitting);
    }
  };

  console.log('✅ Controller inicializado com sucesso!');
}

// Executar imediatamente se DOM já está pronto, senão aguardar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initProjectController);
} else {
  // DOM já está carregado, executar imediatamente
  initProjectController();
}

// Cleanup ao sair da página
window.addEventListener('beforeunload', function (e) {
  if (window.projectCreateController && !window.projectCreateController.isSubmitting) {
    window.projectCreateController.collectSectionData();
    window.projectCreateController.saveFormDataLocally();
  }
});

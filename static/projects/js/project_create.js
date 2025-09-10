/**
 * PROJECT CREATE - JavaScript Controller
 * Gestão completa do formulário multi-étapes com envio de dados
 */

class ProjectCreateController {
  constructor() {
    // Core state management
    this.currentSection = 1;
    this.totalSections = 3;
    this.form = document.getElementById('project-form');

    // Form data storage
    this.formData = new Map();
    this.isSubmitting = false;

    // Auto-save
    this.autoSaveInterval = null;

    // Validation
    this.validationErrors = new Map();
    this.isFormValid = false;

    this.init();
  }

  /**
   * Initializes the controller by setting up event listeners,
   * restoring state, and updating the UI.
   */
  init() {
    this.loadFormData();
    this.setupEventListeners();
    this.updateUI();
    this.setupAutoSave();
    this.setupFormInputStyling();

    // Initial focus on the first field of the first section
    this.focusFirstField();

    // Bind global functions for HTML access
    window.nextSection = (num) => this.nextSection(num);
    window.prevSection = (num) => this.prevSection(num);
    window.showHelp = () => this.showHelp();
    window.closeHelp = () => this.closeHelp();
    window.calculateSurface = () => this.calculateSurface();
    window.applySurfaceCalculation = () => this.applySurfaceCalculation();

    console.log('ProjectCreateController initialized');
  }

  /**
   * Sets up all the event listeners for the form and buttons.
   */
  setupEventListeners() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));

    // Add input event listeners to all form fields for real-time validation and summary updates
    this.form.addEventListener('input', (e) => {
      this.collectSectionData();
      if (this.currentSection === this.totalSections) {
        this.updateSummary();
      }
    });

    // Add change listeners for select and checkbox elements
    this.form.addEventListener('change', (e) => {
      this.collectSectionData();
      if (this.currentSection === this.totalSections) {
        this.updateSummary();
      }
    });

    // Setup click listeners for next buttons
    document.querySelectorAll('[id^="next-btn-"]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const nextSection = parseInt(btn.id.split('-')[2]) + 1;
        console.log('Next button clicked, going to section:', nextSection);
        this.nextSection(nextSection);
      });
    });
  }

  /**
   * Applies Tailwind form-input, form-select, and form-textarea classes
   * to form elements rendered by Django, ensuring consistent styling.
   */
  setupFormInputStyling() {
    const inputs = this.form.querySelectorAll(
      'input:not([type="checkbox"]):not([type="radio"]), select, textarea'
    );
    inputs.forEach((input) => {
      if (input.tagName === 'SELECT') {
        input.classList.add('form-input', 'form-select');
      } else if (input.tagName === 'TEXTAREA') {
        input.classList.add('form-input', 'form-textarea');
      } else {
        input.classList.add('form-input');
      }
    });
  }

  // ================================
  // NAVIGATION METHODS
  // ================================

  /**
   * Advances to the next section of the form if the current section is valid.
   * @param {number} sectionNumber - The number of the section to show.
   */
  nextSection(sectionNumber) {
    console.log('nextSection called with:', sectionNumber);
    console.log('current section:', this.currentSection);

    this.collectSectionData();

    if (this.validateCurrentSection()) {
      console.log('Validation passed, showing section:', sectionNumber);
      this.showSection(sectionNumber);
    } else {
      console.log('Validation failed');
    }
  }

  /**
   * Navigates back to the previous section of the form.
   * @param {number} sectionNumber - The number of the section to show.
   */
  prevSection(sectionNumber) {
    console.log('prevSection called with:', sectionNumber);
    this.collectSectionData();
    this.showSection(sectionNumber);
  }

  /**
   * Manages the visibility of the form sections and updates the UI.
   * @param {number} sectionNumber - The number of the section to show.
   */
  showSection(sectionNumber) {
    console.log('showSection called with:', sectionNumber);

    this.currentSection = sectionNumber;

    // Hide all sections first
    for (let i = 1; i <= this.totalSections; i++) {
      const section = document.getElementById(`section-${i}`);
      if (section) {
        section.classList.add('hidden');
        console.log(`Hiding section-${i}`);
      }
    }

    // Show current section
    const currentSectionElement = document.getElementById(`section-${sectionNumber}`);
    if (currentSectionElement) {
      currentSectionElement.classList.remove('hidden');
      currentSectionElement.classList.add('animate-fade-in');
      console.log(`Showing section-${sectionNumber}`);
    } else {
      console.error(`Section element section-${sectionNumber} not found!`);
    }

    this.updateUI();
    this.focusFirstField();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  /**
   * Updates the UI elements based on the current section.
   */
  updateUI() {
    this.updateProgressIndicator();
    this.updateStepIndicator();

    if (this.currentSection === this.totalSections) {
      this.updateSummary();
    }
  }

  /**
   * Updates the progress bar and text.
   */
  updateProgressIndicator() {
    const progressPercentage = (this.currentSection / this.totalSections) * 100;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (progressBar) {
      progressBar.style.width = `${progressPercentage}%`;
    }
    if (progressText) {
      progressText.textContent = `Étape ${this.currentSection} sur ${
        this.totalSections
      } (${Math.round(progressPercentage)}%)`;
    }
  }

  /**
   * Updates the step indicator circles and lines
   */
  updateStepIndicator() {
    for (let i = 1; i <= this.totalSections; i++) {
      const circle = document.getElementById(`circle-${i}`);
      const step = document.getElementById(`step-${i}`);
      const line = document.getElementById(`line-${i}`);

      if (circle && step) {
        if (i <= this.currentSection) {
          // Active or completed step
          circle.className =
            'flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-sm font-bold';
          step.classList.remove('opacity-50');
          step.classList.add('opacity-100');
        } else {
          // Future step
          circle.className =
            'flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 text-gray-600 text-sm font-bold';
          step.classList.remove('opacity-100');
          step.classList.add('opacity-50');
        }
      }

      if (line) {
        if (i < this.currentSection) {
          // Completed line
          line.className = 'flex-1 h-1 mx-4 bg-blue-600 rounded-full';
        } else {
          // Future line
          line.className = 'flex-1 h-1 mx-4 bg-gray-200 rounded-full';
        }
      }
    }
  }

  // ================================
  // FORM DATA & VALIDATION
  // ================================

  /**
   * Collects data from the current section's form fields.
   */
  collectSectionData() {
    const section = document.getElementById(`section-${this.currentSection}`);
    if (!section) {
      console.log('Section not found:', `section-${this.currentSection}`);
      return;
    }

    const inputs = section.querySelectorAll('input, select, textarea');
    console.log(`Found ${inputs.length} inputs in section ${this.currentSection}`);

    inputs.forEach((input) => {
      if (input.name) {
        if (input.type === 'checkbox') {
          this.formData.set(input.name, input.checked);
        } else {
          this.formData.set(input.name, input.value);
        }
      }
    });

    console.log('Form data collected:', Object.fromEntries(this.formData));
  }

  /**
   * Validates all required fields in the current section.
   * @returns {boolean} True if the section is valid, false otherwise.
   */
  validateCurrentSection() {
    const section = document.getElementById(`section-${this.currentSection}`);
    if (!section) {
      console.error('Section not found for validation');
      return false;
    }

    const requiredInputs = section.querySelectorAll('[required]');
    console.log(
      `Validating ${requiredInputs.length} required fields in section ${this.currentSection}`
    );

    this.validationErrors.clear();
    let hasErrors = false;
    const errors = [];

    requiredInputs.forEach((input) => {
      let isValid = false;

      if (input.type === 'checkbox') {
        isValid = input.checked;
      } else {
        isValid = input.value && input.value.trim() !== '';
      }

      if (!isValid) {
        const label = this.getFieldLabel(input);
        const errorText = `Le champ "${label}" est requis.`;
        errors.push(errorText);

        // Add error styling
        input.classList.add('border-red-500', 'ring-red-200');
        input.classList.remove('border-gray-300');
        hasErrors = true;

        console.log('Validation error for field:', input.name, 'Label:', label);
      } else {
        // Remove error styling
        input.classList.remove('border-red-500', 'ring-red-200');
        input.classList.add('border-gray-300');
      }
    });

    if (hasErrors) {
      this.showValidationSummary(errors);
      console.log('Validation failed with errors:', errors);
    } else {
      this.hideValidationSummary();
      console.log('Validation passed');
    }

    return !hasErrors;
  }

  /**
   * Gets the label text for a form field
   * @param {HTMLElement} input - The input element
   * @returns {string} The label text
   */
  getFieldLabel(input) {
    // Try to find associated label
    const label = document.querySelector(`label[for="${input.id}"]`);
    if (label) {
      return label.textContent.replace(/\s*\*\s*$/, '').trim();
    }

    // Try to find label in parent container
    const parentLabel = input.closest('.form-group')?.querySelector('label');
    if (parentLabel) {
      return parentLabel.textContent.replace(/\s*\*\s*$/, '').trim();
    }

    // Fallback to placeholder or name
    return input.placeholder || input.name || 'Champ requis';
  }

  /**
   * Displays a summary of validation errors.
   * @param {string[]} errors - An array of error messages.
   */
  showValidationSummary(errors) {
    const validationSummary = document.getElementById('validation-summary');
    const validationErrorsList = document.getElementById('validation-errors');

    if (validationSummary && validationErrorsList) {
      validationSummary.classList.remove('hidden');
      validationErrorsList.innerHTML = '';

      errors.forEach((error) => {
        const li = document.createElement('li');
        li.className = 'flex items-center gap-2';
        li.innerHTML = `<i class="fas fa-exclamation-triangle text-red-500"></i>${error}`;
        validationErrorsList.appendChild(li);
      });

      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }

  /**
   * Hides the validation summary.
   */
  hideValidationSummary() {
    const validationSummary = document.getElementById('validation-summary');
    if (validationSummary) {
      validationSummary.classList.add('hidden');
    }
  }

  // ================================
  // SUMMARY AND CALCULATOR
  // ================================

  /**
   * Updates the project summary in the final section.
   */
  updateSummary() {
    const summaryDiv = document.getElementById('project-summary');
    if (!summaryDiv) return;

    const data = Object.fromEntries(this.formData);
    console.log('Updating summary with data:', data);

    // Retrieve and format the data for display
    const title = data['title'] || 'Non renseigné';
    const typeProjet = data['type_projet']
      ? this.getSelectText('id_type_projet', data['type_projet'])
      : 'Non renseigné';
    const description = data['description'] || 'Non renseignée';
    const surfaceTotale = data['surface_totale'] || '0';
    const surfaceMurs = data['surface_murs'] || '0';
    const surfacePlafond = data['surface_plafond'] || '0';
    const adresseTravaux = data['adresse_travaux'] || 'Non renseignée';
    const ville = data['ville'] || 'Non renseignée';
    const codePostal = data['code_postal'] || 'Non renseigné';
    const dateDebutSouhaitee = data['date_debut_souhaitee'] || 'Non renseignée';
    const budgetMinimum = data['budget_minimum'] || '0';
    const budgetMaximum = data['budget_maximum'] || '0';

    // Collect selected pieces types
    const piecesTypes = [];
    if (data['pieces_salon']) piecesTypes.push('Salon');
    if (data['pieces_cuisine']) piecesTypes.push('Cuisine');
    if (data['pieces_chambre']) piecesTypes.push('Chambre');
    if (data['pieces_salle_de_bain']) piecesTypes.push('Salle de bain');
    if (data['pieces_bureau']) piecesTypes.push('Bureau');
    if (data['pieces_couloir']) piecesTypes.push('Couloir');

    const summaryContent = `
      <div class="space-y-6">
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-white p-4 rounded-lg border border-gray-200">
            <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <i class="fas fa-info-circle text-blue-600"></i>
              Informations Générales
            </h4>
            <div class="space-y-2 text-sm">
              <p><strong>Titre:</strong> ${title}</p>
              <p><strong>Type:</strong> ${typeProjet}</p>
              <p><strong>Pièces:</strong> ${
                piecesTypes.length > 0 ? piecesTypes.join(', ') : 'Non spécifiées'
              }</p>
              <p><strong>Description:</strong> ${
                description.length > 100 ? description.substring(0, 100) + '...' : description
              }</p>
            </div>
          </div>

          <div class="bg-white p-4 rounded-lg border border-gray-200">
            <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <i class="fas fa-ruler-combined text-blue-600"></i>
              Détails Techniques
            </h4>
            <div class="space-y-2 text-sm">
              <p><strong>Surface Totale:</strong> ${surfaceTotale} m²</p>
              <p><strong>Surface Murs:</strong> ${surfaceMurs} m²</p>
              <p><strong>Surface Plafond:</strong> ${surfacePlafond} m²</p>
              <p><strong>Nombre de pièces:</strong> ${data['nombre_pieces'] || 'Non spécifié'}</p>
            </div>
          </div>

          <div class="bg-white p-4 rounded-lg border border-gray-200">
            <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <i class="fas fa-map-marker-alt text-blue-600"></i>
              Localisation
            </h4>
            <div class="space-y-2 text-sm">
              <p><strong>Adresse:</strong> ${adresseTravaux}</p>
              <p><strong>Ville:</strong> ${ville}</p>
              <p><strong>Code Postal:</strong> ${codePostal}</p>
            </div>
          </div>

          <div class="bg-white p-4 rounded-lg border border-gray-200">
            <h4 class="font-bold text-gray-900 mb-3 flex items-center gap-2">
              <i class="fas fa-calendar-alt text-blue-600"></i>
              Planning & Budget
            </h4>
            <div class="space-y-2 text-sm">
              <p><strong>Début Souhaité:</strong> ${dateDebutSouhaitee}</p>
              <p><strong>Budget:</strong> ${budgetMinimum}€ - ${budgetMaximum}€</p>
            </div>
          </div>
        </div>
      </div>
    `;

    summaryDiv.innerHTML = summaryContent;
  }

  /**
   * Gets the text of a selected option from a select element.
   * @param {string} selectId - The ID of the select element.
   * @param {string} value - The value of the selected option.
   * @returns {string} The text of the selected option.
   */
  getSelectText(selectId, value) {
    const select = document.getElementById(selectId);
    if (select) {
      const option = select.querySelector(`option[value="${value}"]`);
      return option ? option.textContent : value;
    }
    return value;
  }

  /**
   * Calculates the surface areas based on user input from the calculator.
   */
  calculateSurface() {
    const longueur = parseFloat(document.getElementById('calc-longueur')?.value) || 0;
    const largeur = parseFloat(document.getElementById('calc-largeur')?.value) || 0;
    const hauteur = parseFloat(document.getElementById('calc-hauteur')?.value) || 2.5;

    if (longueur <= 0 || largeur <= 0) {
      alert('Veuillez saisir une longueur et une largeur valides.');
      return;
    }

    const surfaceSol = longueur * largeur;
    const surfaceMurs = (longueur + largeur) * 2 * hauteur;
    const surfacePlafond = surfaceSol;

    const resultSol = document.getElementById('result-sol');
    const resultMurs = document.getElementById('result-murs');
    const resultPlafond = document.getElementById('result-plafond');
    const applyBtn = document.getElementById('apply-calculation');

    if (resultSol) resultSol.textContent = `${surfaceSol.toFixed(2)} m²`;
    if (resultMurs) resultMurs.textContent = `${surfaceMurs.toFixed(2)} m²`;
    if (resultPlafond) resultPlafond.textContent = `${surfacePlafond.toFixed(2)} m²`;
    if (applyBtn) applyBtn.classList.remove('hidden');
  }

  /**
   * Applies the calculated surface values to the main form fields.
   */
  applySurfaceCalculation() {
    const resultSol = document.getElementById('result-sol')?.textContent;
    const resultMurs = document.getElementById('result-murs')?.textContent;
    const resultPlafond = document.getElementById('result-plafond')?.textContent;
    const hauteur = parseFloat(document.getElementById('calc-hauteur')?.value) || 2.5;

    if (resultSol && resultMurs && resultPlafond) {
      const surfaceSol = parseFloat(resultSol);
      const surfaceMurs = parseFloat(resultMurs);
      const surfacePlafond = parseFloat(resultPlafond);

      const surfaceTotaleInput = document.getElementById('id_surface_totale');
      const surfaceMursInput = document.getElementById('id_surface_murs');
      const surfacePlafondInput = document.getElementById('id_surface_plafond');
      const hauteurInput = document.getElementById('id_hauteur_sous_plafond');

      if (surfaceTotaleInput) {
        surfaceTotaleInput.value = (surfaceSol + surfaceMurs + surfacePlafond).toFixed(2);
      }
      if (surfaceMursInput) {
        surfaceMursInput.value = surfaceMurs.toFixed(2);
      }
      if (surfacePlafondInput) {
        surfacePlafondInput.value = surfacePlafond.toFixed(2);
      }
      if (hauteurInput) {
        hauteurInput.value = hauteur.toFixed(2);
      }

      this.collectSectionData(); // Update formData after applying values

      // Show success message
      alert('Surfaces calculées et appliquées avec succès !');

      // Hide apply button
      const applyBtn = document.getElementById('apply-calculation');
      if (applyBtn) applyBtn.classList.add('hidden');
    }
  }

  // ================================
  // AUTO-SAVE & LOCAL STORAGE
  // ================================

  /**
   * Sets up the auto-save mechanism to save form data to local storage.
   */
  setupAutoSave() {
    this.autoSaveInterval = setInterval(() => {
      this.collectSectionData();
      this.saveFormDataLocally();
      this.showAutoSaveIndicator();
    }, 30000); // Saves every 30 seconds
  }

  /**
   * Saves all collected form data to local storage.
   */
  saveFormDataLocally() {
    const dataToSave = Object.fromEntries(this.formData);
    localStorage.setItem('project_draft_data', JSON.stringify(dataToSave));
  }

  /**
   * Loads saved form data from local storage into the form fields.
   */
  loadFormData() {
    const savedData = localStorage.getItem('project_draft_data');
    if (savedData) {
      try {
        const data = JSON.parse(savedData);
        for (const [key, value] of Object.entries(data)) {
          this.formData.set(key, value);
          const input = document.querySelector(`[name="${key}"]`);
          if (input) {
            if (input.type === 'checkbox') {
              input.checked = value === true || value === 'true';
            } else {
              input.value = value;
            }
          }
        }
        console.log('Form data loaded from localStorage');
      } catch (error) {
        console.error('Error loading form data:', error);
        localStorage.removeItem('project_draft_data');
      }
    }
  }

  /**
   * Briefly shows the auto-save indicator.
   */
  showAutoSaveIndicator() {
    const indicator = document.getElementById('auto-save-indicator');
    if (indicator) {
      indicator.classList.remove('opacity-0');
      indicator.classList.add('opacity-100');
      setTimeout(() => {
        indicator.classList.remove('opacity-100');
        indicator.classList.add('opacity-0');
      }, 3000);
    }
  }

  // ================================
  // HELP MODAL
  // ================================

  /**
   * Displays the help modal.
   */
  showHelp() {
    const modal = document.getElementById('help-modal');
    if (modal) {
      modal.classList.remove('hidden');
      document.body.classList.add('overflow-hidden');
    }
  }

  /**
   * Hides the help modal.
   */
  closeHelp() {
    const modal = document.getElementById('help-modal');
    if (modal) {
      modal.classList.add('hidden');
      document.body.classList.remove('overflow-hidden');
    }
  }

  // ===============================
  // UTILITY METHODS
  // ===============================

  /**
   * Sets focus on the first form field of the current section.
   */
  focusFirstField() {
    const section = document.getElementById(`section-${this.currentSection}`);
    if (section) {
      const firstInput = section.querySelector(
        'input:not([type="hidden"]):not([disabled]), select:not([disabled]), textarea:not([disabled])'
      );
      if (firstInput) {
        setTimeout(() => {
          firstInput.focus();
          firstInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 100);
      }
    }
  }

  // ===============================
  // HANDLERS
  // ===============================

  /**
   * Handles the form submission process.
   * @param {Event} event - The form submit event.
   */
  handleSubmit(event) {
    console.log('Form submission attempted');

    // Don't prevent default if we're not in the last section
    if (this.currentSection !== this.totalSections) {
      event.preventDefault();
      this.nextSection(this.currentSection + 1);
      return;
    }

    // Final validation for submission
    this.collectSectionData();
    if (!this.validateCurrentSection() || this.isSubmitting) {
      event.preventDefault();
      return;
    }

    this.isSubmitting = true;

    const submitButton = document.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Envoi en cours...';
    }

    // Clear localStorage on successful submission
    localStorage.removeItem('project_draft_data');

    console.log('Form submitted successfully');
    // Let the form submit naturally
  }

  // ===============================
  // CLEANUP
  // ===============================

  /**
   * Cleans up resources before the page unloads.
   */
  destroy() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    this.collectSectionData();
    this.saveFormDataLocally();
  }
}

// ===============================
// MAIN ENTRY POINT
// ===============================

document.addEventListener('DOMContentLoaded', function () {
  console.log('DOM loaded, initializing ProjectCreateController');
  window.projectCreateController = new ProjectCreateController();
});

// Save data before the user leaves the page
window.addEventListener('beforeunload', function (e) {
  if (window.projectCreateController && !window.projectCreateController.isSubmitting) {
    window.projectCreateController.collectSectionData();
    window.projectCreateController.saveFormDataLocally();
  }
});

// Handle escape key for modal
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    const helpModal = document.getElementById('help-modal');
    if (helpModal && !helpModal.classList.contains('hidden')) {
      window.projectCreateController.closeHelp();
    }
  }
});

// A small debounce function for search inputs, if needed.

// Variáveis globais
let currentSection = 1;
const totalSections = 3;
let autoSaveTimeout;

// Função debounce (já existe no seu código)
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

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function () {
  initializeForm();
  setupEventListeners();
  setupAutoSave();
  setupCalculator();
});

// Inicializar formulário
function initializeForm() {
  // Mostrar apenas a primeira seção
  showSection(1);
  updateProgress(1);

  // Carregar dados salvos se existirem
  loadSavedData();
}

// Configurar event listeners
function setupEventListeners() {
  // Validação em tempo real
  const form = document.getElementById('project-form');
  if (form) {
    form.addEventListener('input', debounce(validateCurrentSection, 300));
    form.addEventListener('change', debounce(validateCurrentSection, 300));
  }

  // Navegação com teclado
  document.addEventListener('keydown', function (e) {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      if (currentSection < totalSections) {
        nextSection(currentSection + 1);
      } else {
        submitForm();
      }
    }
  });
}

// Navegação entre seções
function nextSection(sectionNumber) {
  if (validateCurrentSection()) {
    showSection(sectionNumber);
    updateProgress(sectionNumber);
    currentSection = sectionNumber;

    // Scroll para o topo
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function prevSection(sectionNumber) {
  showSection(sectionNumber);
  updateProgress(sectionNumber);
  currentSection = sectionNumber;

  // Scroll para o topo
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Mostrar seção específica
function showSection(sectionNumber) {
  // Esconder todas as seções
  for (let i = 1; i <= totalSections; i++) {
    const section = document.getElementById(`section-${i}`);
    if (section) {
      section.classList.add('hidden');
    }
  }

  // Mostrar seção atual
  const currentSectionEl = document.getElementById(`section-${sectionNumber}`);
  if (currentSectionEl) {
    currentSectionEl.classList.remove('hidden');
    currentSectionEl.classList.add('animate-fade-in');
  }
}

// Atualizar barra de progresso
function updateProgress(sectionNumber) {
  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-text');

  const percentage = (sectionNumber / totalSections) * 100;

  if (progressBar) {
    progressBar.style.width = `${percentage}%`;
  }

  if (progressText) {
    progressText.textContent = `Étape ${sectionNumber} sur ${totalSections} (${Math.round(
      percentage
    )}%)`;
  }

  // Atualizar indicadores visuais dos steps
  for (let i = 1; i <= totalSections; i++) {
    const circle = document.getElementById(`circle-${i}`);
    const step = document.getElementById(`step-${i}`);
    const line = document.getElementById(`line-${i}`);

    if (circle && step) {
      if (i < sectionNumber) {
        // Seção completada
        circle.className =
          'flex items-center justify-center w-10 h-10 rounded-full bg-green-600 text-white text-sm font-bold';
        circle.innerHTML = '<i class="fas fa-check"></i>';
        step.querySelectorAll('div').forEach((div) => {
          div.classList.remove('text-gray-600');
          div.classList.add('text-green-600');
        });
      } else if (i === sectionNumber) {
        // Seção atual
        circle.className =
          'flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-sm font-bold';
        circle.textContent = i;
        step.querySelectorAll('div').forEach((div) => {
          div.classList.remove('text-gray-600');
          div.classList.add('text-blue-600');
        });
      } else {
        // Seção futura
        circle.className =
          'flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 text-gray-600 text-sm font-bold';
        circle.textContent = i;
        step.querySelectorAll('div').forEach((div) => {
          div.classList.remove('text-blue-600', 'text-green-600');
          div.classList.add('text-gray-600');
        });
      }
    }

    if (line) {
      if (i < sectionNumber) {
        line.classList.remove('bg-gray-200');
        line.classList.add('bg-green-600');
      } else {
        line.classList.remove('bg-green-600');
        line.classList.add('bg-gray-200');
      }
    }
  }
}

// Validação da seção atual
function validateCurrentSection() {
  const section = document.getElementById(`section-${currentSection}`);
  if (!section) return true;

  const requiredFields = section.querySelectorAll('[required]');
  let isValid = true;
  const errors = [];

  // Limpar erros anteriores
  clearValidationErrors();

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      isValid = false;
      showFieldError(field, 'Ce champ est obligatoire');
      errors.push(`${getFieldLabel(field)} est obligatoire`);
    } else {
      clearFieldError(field);
    }
  });

  // Validações específicas por seção
  if (currentSection === 1) {
    isValid = validateSection1() && isValid;
  } else if (currentSection === 2) {
    isValid = validateSection2() && isValid;
  } else if (currentSection === 3) {
    isValid = validateSection3() && isValid;
  }

  // Mostrar resumo de erros se houver
  if (!isValid) {
    showValidationSummary(errors);
  } else {
    hideValidationSummary();
  }

  return isValid;
}

// Validações específicas da seção 1
function validateSection1() {
  let isValid = true;

  // Validar título
  const title = document.getElementById('id_title');
  if (title && title.value.length < 5) {
    showFieldError(title, 'Le titre doit contenir au moins 5 caractères');
    isValid = false;
  }

  // Validar descrição
  const description = document.getElementById('id_description');
  if (description && description.value.length < 20) {
    showFieldError(description, 'La description doit contenir au moins 20 caractères');
    isValid = false;
  }

  return isValid;
}

// Validações específicas da seção 2
function validateSection2() {
  let isValid = true;

  // Validar surface totale
  const surfaceTotal = document.getElementById('id_surface_totale');
  if (surfaceTotal && parseFloat(surfaceTotal.value) <= 0) {
    showFieldError(surfaceTotal, 'La surface totale doit être supérieure à 0');
    isValid = false;
  }

  return isValid;
}

// Validações específicas da seção 3
function validateSection3() {
  let isValid = true;

  // Validar código postal
  const codePostal = document.getElementById('id_code_postal');
  if (codePostal && !/^\d{5}$/.test(codePostal.value)) {
    showFieldError(codePostal, 'Le code postal doit contenir 5 chiffres');
    isValid = false;
  }

  return isValid;
}

// Mostrar erro em campo específico
function showFieldError(field, message) {
  clearFieldError(field);

  field.classList.add('border-red-500', 'focus:ring-red-500');

  const errorDiv = document.createElement('div');
  errorDiv.className = 'mt-1 flex items-center gap-2 text-red-600 text-sm field-error';
  errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i><span>${message}</span>`;

  field.parentNode.appendChild(errorDiv);
}

// Limpar erro de campo específico
function clearFieldError(field) {
  field.classList.remove('border-red-500', 'focus:ring-red-500');

  const existingError = field.parentNode.querySelector('.field-error');
  if (existingError) {
    existingError.remove();
  }
}

// Limpar todos os erros de validação
function clearValidationErrors() {
  document.querySelectorAll('.field-error').forEach((error) => error.remove());
  document.querySelectorAll('.border-red-500').forEach((field) => {
    field.classList.remove('border-red-500', 'focus:ring-red-500');
  });
}

// Mostrar resumo de validação
function showValidationSummary(errors) {
  const summary = document.getElementById('validation-summary');
  const errorsList = document.getElementById('validation-errors');

  if (summary && errorsList) {
    errorsList.innerHTML = errors.map((error) => `<li>• ${error}</li>`).join('');
    summary.classList.remove('hidden');

    // Scroll para o resumo
    summary.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// Esconder resumo de validação
function hideValidationSummary() {
  const summary = document.getElementById('validation-summary');
  if (summary) {
    summary.classList.add('hidden');
  }
}

// Obter label do campo
function getFieldLabel(field) {
  const label = document.querySelector(`label[for="${field.id}"]`);
  return label ? label.textContent.replace('*', '').trim() : field.name;
}

// Auto-save functionality
function setupAutoSave() {
  const form = document.getElementById('project-form');
  if (form) {
    form.addEventListener('input', debounce(autoSave, 2000));
  }
}

function autoSave() {
  const formData = new FormData(document.getElementById('project-form'));
  const data = {};

  // Converter FormData para objeto
  for (let [key, value] of formData.entries()) {
    if (data[key]) {
      // Se já existe, converter para array
      if (Array.isArray(data[key])) {
        data[key].push(value);
      } else {
        data[key] = [data[key], value];
      }
    } else {
      data[key] = value;
    }
  }

  // Salvar no localStorage
  localStorage.setItem('project_form_draft', JSON.stringify(data));

  // Mostrar indicador de salvamento
  showAutoSaveIndicator();
}

// Mostrar indicador de auto-save
function showAutoSaveIndicator() {
  const indicator = document.getElementById('auto-save-indicator');
  if (indicator) {
    indicator.style.opacity = '1';

    setTimeout(() => {
      indicator.style.opacity = '0';
    }, 2000);
  }
}

// Carregar dados salvos
function loadSavedData() {
  const savedData = localStorage.getItem('project_form_draft');
  if (savedData) {
    try {
      const data = JSON.parse(savedData);

      // Preencher campos do formulário
      Object.keys(data).forEach((key) => {
        const field = document.querySelector(`[name="${key}"]`);
        if (field) {
          if (field.type === 'checkbox') {
            field.checked = data[key] === 'on' || data[key] === true;
          } else {
            field.value = data[key];
          }
        }
      });

      console.log('Dados do rascunho carregados');
    } catch (error) {
      console.error('Erro ao carregar dados salvos:', error);
    }
  }
}

// Limpar dados salvos
function clearSavedData() {
  localStorage.removeItem('project_form_draft');
}

// Calculadora de superfície
function setupCalculator() {
  // Event listeners para campos de cálculo
  const surfaceFields = ['surface_murs', 'surface_plafond', 'surface_boiseries'];

  surfaceFields.forEach((fieldName) => {
    const field = document.getElementById(`id_${fieldName}`);
    if (field) {
      field.addEventListener('input', debounce(calculateTotalSurface, 300));
    }
  });
}

// Calcular superfície total
function calculateTotalSurface() {
  const surfaceMurs = parseFloat(document.getElementById('id_surface_murs')?.value || 0);
  const surfacePlafond = parseFloat(document.getElementById('id_surface_plafond')?.value || 0);
  const surfaceBoiseries = parseFloat(document.getElementById('id_surface_boiseries')?.value || 0);

  const total = surfaceMurs + surfacePlafond + surfaceBoiseries;

  const totalField = document.getElementById('id_surface_totale');
  if (totalField) {
    totalField.value = total.toFixed(2);

    // Trigger change event para auto-save
    totalField.dispatchEvent(new Event('input'));
  }

  // Atualizar estimativa de preço se disponível
  updatePriceEstimate(total);
}

// Atualizar estimativa de preço
function updatePriceEstimate(totalSurface) {
  const priceEstimateEl = document.getElementById('price-estimate');
  if (priceEstimateEl && totalSurface > 0) {
    // Preço base por m² (pode ser ajustado)
    const pricePerM2 = 25; // €/m²
    const estimatedPrice = totalSurface * pricePerM2;

    priceEstimateEl.innerHTML = `
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-center gap-2 mb-2">
          <i class="fas fa-calculator text-blue-600"></i>
          <span class="font-semibold text-blue-800">Estimation indicative</span>
        </div>
        <div class="text-2xl font-bold text-blue-600">
          ${estimatedPrice.toLocaleString('fr-FR')} €
        </div>
        <div class="text-sm text-blue-600 mt-1">
          Basé sur ${totalSurface}m² à ${pricePerM2}€/m²
        </div>
        <div class="text-xs text-gray-600 mt-2">
          * Prix indicatif, devis personnalisé sur demande
        </div>
      </div>
    `;
  }
}

// Função para mostrar ajuda
function showHelp() {
  const modal = document.getElementById('help-modal');
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }
}

// Função para fechar ajuda
function closeHelp() {
  const modal = document.getElementById('help-modal');
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = 'auto';
  }
}

// Submeter formulário
function submitForm() {
  if (validateCurrentSection()) {
    // Limpar dados salvos antes de submeter
    clearSavedData();

    // Mostrar loading
    showSubmitLoading();

    // Submeter formulário
    document.getElementById('project-form').submit();
  }
}

// Mostrar loading no submit
function showSubmitLoading() {
  const submitBtn = document.querySelector('button[type="submit"]');
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <i class="fas fa-spinner fa-spin mr-2"></i>
      Création en cours...
    `;
  }
}

// Event listeners para navegação
document.addEventListener('click', function (e) {
  // Botões de navegação
  if (e.target.matches('[data-next-section]')) {
    e.preventDefault();
    const nextSection = parseInt(e.target.dataset.nextSection);
    nextSection(nextSection);
  }

  if (e.target.matches('[data-prev-section]')) {
    e.preventDefault();
    const prevSection = parseInt(e.target.dataset.prevSection);
    prevSection(prevSection);
  }

  // Fechar modal de ajuda
  if (e.target.matches('#help-modal') || e.target.matches('[data-close-help]')) {
    closeHelp();
  }
});

// Prevenir saída acidental se há dados não salvos
window.addEventListener('beforeunload', function (e) {
  const savedData = localStorage.getItem('project_form_draft');
  if (savedData) {
    e.preventDefault();
    e.returnValue =
      'Vous avez des modifications non sauvegardées. Êtes-vous sûr de vouloir quitter ?';
  }
});

// Função para adicionar nova linha de pièce (se necessário)
function addPieceRow() {
  const container = document.getElementById('pieces-container');
  if (container) {
    const newRow = document.createElement('div');
    newRow.className = 'grid grid-cols-1 md:grid-cols-3 gap-4 piece-row';
    newRow.innerHTML = `
      <div>
        <input type="text" 
               name="piece_nom[]" 
               class="form-input" 
               placeholder="Nom de la pièce">
      </div>
      <div>
        <input type="number" 
               name="piece_surface[]" 
               class="form-input" 
               placeholder="Surface (m²)" 
               step="0.01" 
               min="0">
      </div>
      <div class="flex items-center gap-2">
        <select name="piece_type[]" class="form-input form-select flex-1">
          <option value="">Type de surface</option>
          <option value="murs">Murs</option>
          <option value="plafond">Plafond</option>
          <option value="boiseries">Boiseries</option>
        </select>
        <button type="button" 
                onclick="removePieceRow(this)" 
                class="btn btn-sm bg-red-100 text-red-600 hover:bg-red-200">
          <i class="fas fa-trash"></i>
        </button>
      </div>
    `;

    container.appendChild(newRow);

    // Adicionar event listeners para cálculo
    const surfaceInput = newRow.querySelector('input[name="piece_surface[]"]');
    if (surfaceInput) {
      surfaceInput.addEventListener('input', debounce(calculateTotalSurface, 300));
    }
  }
}

// Função para remover linha de pièce
function removePieceRow(button) {
  const row = button.closest('.piece-row');
  if (row) {
    row.remove();
    calculateTotalSurface();
  }
}

// Função para preview de imagem (se houver upload)
function previewImage(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();

    reader.onload = function (e) {
      const preview = document.getElementById('image-preview');
      if (preview) {
        preview.innerHTML = `
          <img src="${e.target.result}" 
               class="max-w-full h-auto rounded-lg shadow-sm" 
               alt="Preview">
        `;
      }
    };

    reader.readAsDataURL(input.files[0]);
  }
}

// Exportar funções globais necessárias
window.nextSection = nextSection;
window.prevSection = prevSection;
window.showHelp = showHelp;
window.closeHelp = closeHelp;
window.submitForm = submitForm;
window.addPieceRow = addPieceRow;
window.removePieceRow = removePieceRow;
window.previewImage = previewImage;

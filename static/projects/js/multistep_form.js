document.addEventListener('DOMContentLoaded', function () {
  console.log('🚀 Inicializando wizard de projeto');

  let currentStep = 1;
  const wizardData = {
    title: '',
    description: '',
    projectType: 'residentiel',
    surfaceArea: 0,
    paintType: '',
    colors: '',
    startDate: '',
    endDate: '',
    notes: '',
  };

  // ================================
  // FUNÇÃO PRINCIPAL DE NAVEGAÇÃO
  // ================================
  window.showStep = function (stepNum) {
    console.log(`🔄 Navegando para etapa ${stepNum}`);

    // Esconder todas as etapas
    document.querySelectorAll('.wizard-step').forEach((step) => {
      step.classList.add('hidden');
      step.classList.remove('active');
    });

    // Mostrar etapa atual
    const targetStep = document.getElementById(`step${stepNum}`);
    if (targetStep) {
      targetStep.classList.remove('hidden');
      targetStep.classList.add('active');
      currentStep = stepNum;

      console.log(`✅ Etapa ${stepNum} ativada`);

      // Atualizar progress bar
      updateProgressBar(stepNum);

      // Se for etapa 3, gerar resumo
      if (stepNum === 3) {
        setTimeout(() => updateSummary(), 100);
      }

      // Scroll para o topo
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      console.error(`❌ Etapa step${stepNum} não encontrada!`);
    }

    return true;
  };

  // ================================
  // ATUALIZAR PROGRESS BAR
  // ================================
  function updateProgressBar(step) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');

    if (progressBar) {
      const percentage = (step / 3) * 100;
      progressBar.style.width = `${percentage}%`;
    }

    if (progressText) {
      progressText.textContent = `Étape ${step} sur 3`;
    }

    // Atualizar indicadores visuais
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
      const stepNumber = index + 1;
      if (stepNumber < step) {
        indicator.classList.add('completed');
        indicator.classList.remove('active');
      } else if (stepNumber === step) {
        indicator.classList.add('active');
        indicator.classList.remove('completed');
      } else {
        indicator.classList.remove('active', 'completed');
      }
    });
  }

  // ================================
  // STEP 1 - NAVIGATION
  // ================================
  const step1NextBtn = document.getElementById('step1-next');
  if (step1NextBtn) {
    step1NextBtn.addEventListener('click', function () {
      console.log('🔄 Tentando avançar da etapa 1 para 2');

      const title = document.getElementById('step1-title')?.value.trim() || '';
      const description = document.getElementById('step1-description')?.value.trim() || '';
      const projectType = document.getElementById('step1-project-type')?.value || '';

      // Verificar se pelo menos uma peça foi selecionada
      const anyPieceSelected = [
        'step1-pieces-salon',
        'step1-pieces-cuisine',
        'step1-pieces-chambre',
        'step1-pieces-salle-de-bain',
        'step1-pieces-bureau',
        'step1-pieces-couloir',
      ].some((id) => document.getElementById(id)?.checked);

      const errors = [];

      // Validações
      if (!title) {
        errors.push('Le nom du projet est obligatoire');
      } else if (title.length < 3) {
        errors.push('Le nom du projet doit contenir au moins 3 caractères');
      }

      if (!projectType) {
        errors.push('Le type de projet est obligatoire');
      }

      if (!description) {
        errors.push('La description détaillée est obligatoire');
      } else if (description.length < 20) {
        errors.push('La description doit contenir au moins 20 caractères pour un devis précis');
      }

      if (!anyPieceSelected) {
        errors.push('Sélectionner les types de pièces aidera à affiner le devis.');
      }

      if (errors.length > 0) {
        alert(errors.join('\n'));
        return;
      }

      // Salvar dados
      wizardData.title = title;
      wizardData.description = description;
      wizardData.projectType = projectType;

      console.log('✅ Dados da etapa 1 salvos:', wizardData);
      showStep(2);
    });
  }

  // ================================
  // STEP 2 - NAVIGATION
  // ================================
  const step2PrevBtn = document.getElementById('step2-prev');
  if (step2PrevBtn) {
    step2PrevBtn.addEventListener('click', () => {
      console.log('🔄 Voltando da etapa 2 para 1');
      showStep(1);
    });
  }

  const step2NextBtn = document.getElementById('step2-next');
  if (step2NextBtn) {
    step2NextBtn.addEventListener('click', function () {
      console.log('🔄 Tentando avançar da etapa 2 para 3');

      const errors = [];
      const warnings = [];

      // Validações obrigatórias
      const surfaceArea = document.getElementById('step2-surface-area')?.value.trim() || '';
      if (!surfaceArea || parseFloat(surfaceArea) <= 0) {
        errors.push('• La surface totale est obligatoire et doit être supérieure à 0 m²');
      }

      const etatSurfaces = document.getElementById('step2-etat-surfaces')?.value || '';
      if (!etatSurfaces) {
        errors.push("• L'état des surfaces est obligatoire");
      }

      // Validações recomendadas
      const nombrePieces = document.getElementById('step2-nombre-pieces')?.value || '';
      if (!nombrePieces || parseInt(nombrePieces) <= 0) {
        warnings.push('• Le nombre de pièces est recommandé pour un devis précis');
      }

      const finitions = document.getElementById('step2-paint-type')?.value || '';
      if (!finitions) {
        warnings.push('• Le type de finitions aide à établir un devis précis');
      }

      // Verificar erros
      if (errors.length > 0) {
        alert('Erreurs à corriger :\n\n' + errors.join('\n'));
        return;
      }

      // Mostrar avisos
      if (warnings.length > 0) {
        const proceed = confirm(
          'Informations recommandées :\n\n' +
            warnings.join('\n') +
            '\n\nVoulez-vous continuer sans ces informations ?'
        );
        if (!proceed) return;
      }

      // Salvar dados
      wizardData.surfaceArea = parseFloat(surfaceArea);
      wizardData.etatSurfaces = etatSurfaces;
      wizardData.nombrePieces = nombrePieces;
      wizardData.finitions = finitions;
      wizardData.couleurMurs = document.getElementById('step2-couleur-murs')?.value.trim() || '';
      wizardData.couleurPlafond =
        document.getElementById('step2-couleur-plafond')?.value.trim() || '';
      wizardData.couleurBoiseries =
        document.getElementById('step2-couleur-boiseries')?.value.trim() || '';

      console.log('✅ Dados da etapa 2 salvos:', wizardData);
      showStep(3);
    });
  }
  // Surface calculator
  document.getElementById('calc-surface').addEventListener('click', function () {
    const length = parseFloat(document.getElementById('calc-length').value) || 0;
    const width = parseFloat(document.getElementById('calc-width').value) || 0;
    const height = parseFloat(document.getElementById('calc-height').value) || 2.5;

    if (length > 0 && width > 0) {
      const wallArea = 2 * (length + width) * height;
      const totalSurface = wallArea;

      document.getElementById(
        'calc-result'
      ).innerHTML = `Surface estimée: <strong>${totalSurface.toFixed(1)} m²</strong>`;
      document.getElementById('step2-surface-area').value = totalSurface.toFixed(1);

      updateCostEstimate();
    } else {
      document.getElementById('calc-result').innerHTML =
        '<span class="text-red-500">Veuillez remplir longueur et largeur</span>';
    }
  });

  // ================================
  // STEP 3 - NAVIGATION
  // ================================
  const step3PrevBtn = document.getElementById('step3-prev');
  if (step3PrevBtn) {
    step3PrevBtn.addEventListener('click', () => {
      console.log('🔄 Voltando da etapa 3 para 2');
      showStep(2);
    });
  }

  const finalSubmitBtn = document.getElementById('final-submit');
  if (finalSubmitBtn) {
    finalSubmitBtn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('🔄 Tentando submeter formulário final');

      if (validateStep3()) {
        console.log('✅ Validação da etapa 3 passou, submetendo formulário');
        document.getElementById('project-form').submit();
      }
    });
  }

  // ================================
  // VALIDAÇÃO DA ETAPA 3
  // ================================
  function validateStep3() {
    let isValid = true;
    const errors = [];

    // Validações obrigatórias
    const adresse = document.getElementById('step3-adresse-travaux');
    if (adresse && (!adresse.value.trim() || adresse.value.trim().length < 10)) {
      showFieldError(adresse, "L'adresse doit contenir au moins 10 caractères");
      isValid = false;
    } else if (adresse) {
      clearFieldError(adresse);
    }

    const ville = document.getElementById('step3-ville');
    if (ville && !ville.value.trim()) {
      showFieldError(ville, 'La ville est obligatoire');
      isValid = false;
    } else if (ville) {
      clearFieldError(ville);
    }

    const codePostal = document.getElementById('step3-code-postal');
    const codePostalRegex = /^[0-9]{5}$/;
    if (codePostal && (!codePostal.value.trim() || !codePostalRegex.test(codePostal.value))) {
      showFieldError(codePostal, 'Le code postal doit contenir exactement 5 chiffres');
      isValid = false;
    } else if (codePostal) {
      clearFieldError(codePostal);
    }

    // Validação de checkboxes obrigatórios
    const acceptConditions = document.getElementById('step3-accept-conditions');
    if (acceptConditions && !acceptConditions.checked) {
      showFieldError(acceptConditions, 'Vous devez accepter les conditions générales');
      isValid = false;
    } else if (acceptConditions) {
      clearFieldError(acceptConditions);
    }

    const acceptContact = document.getElementById('step3-accept-contact');
    if (acceptContact && !acceptContact.checked) {
      showFieldError(acceptContact, 'Vous devez autoriser le contact');
      isValid = false;
    } else if (acceptContact) {
      clearFieldError(acceptContact);
    }

    if (!isValid) {
      showNotification('Veuillez corriger les erreurs avant de continuer', 'error');
      const firstError = document.querySelector('.border-red-500');
      if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }

    return isValid;
  }

  function calculateEstimate(surface, projectType) {
    const rates = {
      residentiel: { min: 25, max: 35 },
      commercial: { min: 30, max: 45 },
      artistique: { min: 45, max: 70 },
      renovation: { min: 35, max: 50 },
    };

    const rate = rates[projectType] || rates['residentiel'];
    const minCost = Math.round(surface * rate.min);
    const maxCost = Math.round(surface * rate.max);

    return { minCost, maxCost, rate };
  }

  // ================================
  // FUNÇÕES DE NAVEGAÇÃO E VALIDAÇÃO
  // ================================

  window.showStep = function (stepNum) {
    console.log(`🔄 Navegando para etapa ${stepNum}`);

    // Esconder todas as etapas
    document.querySelectorAll('.wizard-step').forEach((step) => {
      step.classList.add('hidden');
      step.classList.remove('active');
    });

    // Mostrar etapa atual
    const targetStep = document.getElementById(`step${stepNum}`);
    if (targetStep) {
      targetStep.classList.remove('hidden');
      targetStep.classList.add('active');
      currentStep = stepNum;

      console.log(`✅ Etapa ${stepNum} ativada`);

      // Atualizar progress bar
      updateProgressBar(stepNum);

      // Se for etapa 3, gerar resumo
      if (stepNum === 3) {
        setTimeout(() => updateSummary(), 100);
      }

      // Scroll para o topo
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      console.error(`❌ Etapa step${stepNum} não encontrada!`);
    }

    return true;
  };

  // ================================
  // ATUALIZAR PROGRESS BAR
  // ================================
  function updateProgressBar(step) {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('.progress-text');

    if (progressBar) {
      const percentage = (step / 3) * 100;
      progressBar.style.width = `${percentage}%`;
    }

    if (progressText) {
      progressText.textContent = `Étape ${step} sur 3`;
    }

    // Atualizar indicadores visuais
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
      const stepNumber = index + 1;
      if (stepNumber < step) {
        indicator.classList.add('completed');
        indicator.classList.remove('active');
      } else if (stepNumber === step) {
        indicator.classList.add('active');
        indicator.classList.remove('completed');
      } else {
        indicator.classList.remove('active', 'completed');
      }
    });
  }

  // ================================
  // FUNÇÕES DE VALIDAÇÃO DE CAMPOS
  // ================================

  function showFieldError(field, message) {
    // Remover erro anterior
    clearFieldError(field);

    // Adicionar classe de erro
    field.classList.add('border-red-500', 'bg-red-50');
    field.classList.remove('border-gray-300');

    // Criar elemento de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error mt-1 text-sm text-red-600 flex items-center';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-1"></i>${message}`;

    // Inserir após o campo
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
  }

  function clearFieldError(field) {
    // Remover classes de erro
    field.classList.remove('border-red-500', 'bg-red-50');
    field.classList.add('border-gray-300');

    // Remover mensagem de erro
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
      errorDiv.remove();
    }
  }

  // ================================
  // SISTEMA DE NOTIFICAÇÕES
  // ================================

  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;

    const colors = {
      success: 'bg-green-500 text-white',
      error: 'bg-red-500 text-white',
      warning: 'bg-yellow-500 text-white',
      info: 'bg-blue-500 text-white',
    };

    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle',
    };

    notification.className += ` ${colors[type]}`;
    notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${icons[type]} mr-2"></i>
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
      notification.classList.remove('translate-x-full');
    }, 100);

    // Auto remover após 5 segundos
    setTimeout(() => {
      notification.classList.add('translate-x-full');
      setTimeout(() => notification.remove(), 300);
    }, 5000);
  }

  // ================================
  // UPLOAD DE IMAGENS
  // ================================

  const imageUpload = document.getElementById('step2-images');
  const imagePreview = document.getElementById('image-preview');

  if (imageUpload && imagePreview) {
    imageUpload.addEventListener('change', function (e) {
      const files = Array.from(e.target.files);
      imagePreview.innerHTML = '';

      if (files.length === 0) {
        imagePreview.innerHTML =
          '<p class="text-gray-500 text-center py-4">Aucune image sélectionnée</p>';
        return;
      }

      files.forEach((file, index) => {
        if (file.type.startsWith('image/')) {
          const reader = new FileReader();
          reader.onload = function (e) {
            const imageDiv = document.createElement('div');
            imageDiv.className = 'relative group';
            imageDiv.innerHTML = `
                            <img src="${e.target.result}" alt="Preview ${index + 1}" 
                                 class="w-full h-32 object-cover rounded-lg border border-gray-200">
                            <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 
                                        transition-opacity duration-200 rounded-lg flex items-center justify-center">
                                <button type="button" onclick="removeImage(${index})" 
                                        class="text-white hover:text-red-300 transition-colors">
                                    <i class="fas fa-trash-alt text-xl"></i>
                                </button>
                            </div>
                            <div class="absolute bottom-2 left-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
                                ${file.name}
                            </div>
                        `;
            imagePreview.appendChild(imageDiv);
          };
          reader.readAsDataURL(file);
        }
      });
    });
  }

  window.removeImage = function (index) {
    const imageUpload = document.getElementById('step2-images');
    const dt = new DataTransfer();
    const files = Array.from(imageUpload.files);

    files.forEach((file, i) => {
      if (i !== index) {
        dt.items.add(file);
      }
    });

    imageUpload.files = dt.files;
    imageUpload.dispatchEvent(new Event('change'));
  };

  // ================================
  // INICIALIZAÇÃO
  // ================================

  // Mostrar primeira etapa
  showStep(1);

  // Adicionar listeners para campos que afetam estimativa
  document.getElementById('step1-project-type').addEventListener('change', updateCostEstimate);

  // Validação em tempo real para campos importantes
  document.getElementById('step1-title').addEventListener('input', function () {
    if (this.value.trim().length >= 3) {
      clearFieldError(this);
    }
  });

  document.getElementById('step1-description').addEventListener('input', function () {
    if (this.value.trim().length >= 20) {
      clearFieldError(this);
    }
  });

  document.getElementById('step2-surface-area').addEventListener('input', function () {
    if (parseFloat(this.value) > 0) {
      clearFieldError(this);
    }
  });

  // Validação de campos da etapa 3
  ['step3-adresse-travaux', 'step3-ville', 'step3-code-postal'].forEach((id) => {
    const field = document.getElementById(id);
    if (field) {
      field.addEventListener('input', function () {
        clearFieldError(this);
      });
    }
  });

  console.log('✅ Wizard de projeto inicializado com sucesso');
});

// ================================
// FUNÇÕES GLOBAIS PARA DEBUG
// ================================

window.debugWizard = function () {
  console.log('🔍 Debug do Wizard:');
  console.log('Etapa atual:', currentStep);
  console.log('Dados do wizard:', wizardData);
  console.log('Elementos encontrados:');
  for (let i = 1; i <= 3; i++) {
    const step = document.getElementById(`step${i}`);
    console.log(`- Step ${i}:`, step ? '✅' : '❌');
  }
};

window.testNavigation = function () {
  console.log('🧪 Testando navegação...');
  showStep(1);
  setTimeout(() => showStep(2), 1000);
  setTimeout(() => showStep(3), 2000);
  setTimeout(() => showStep(1), 3000);
};

// Função para mostrar etapas - CORRIGIDA
function showStep(stepNum) {
  console.log(`Navegando para etapa ${stepNum}`);

  // Esconder todas as etapas
  document.querySelectorAll('.wizard-step').forEach((step) => {
    step.classList.add('hidden');
    step.classList.remove('active');
  });

  // Mostrar etapa atual
  const currentStep = document.getElementById(`step${stepNum}`);
  if (currentStep) {
    currentStep.classList.remove('hidden');
    currentStep.classList.add('active');
  } else {
    console.error(`Etapa step${stepNum} não encontrada!`);
    return;
  }

  // Atualizar indicadores de progresso
  document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
    const stepNumber = index + 1;
    const circle = indicator.querySelector('.step-circle');
    const text = indicator.querySelector('.text-sm.font-semibold');

    if (stepNumber < stepNum) {
      // Etapas concluídas - Verde
      circle.className =
        'flex items-center justify-center w-10 h-10 rounded-full bg-green-600 text-white text-sm font-bold step-circle';
      if (text) text.className = 'text-sm font-semibold text-green-600';
    } else if (stepNumber === stepNum) {
      // Etapa atual - Azul
      circle.className =
        'flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-sm font-bold step-circle';
      if (text) text.className = 'text-sm font-semibold text-blue-600';
    } else {
      // Etapas futuras - Cinza
      circle.className =
        'flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 text-gray-600 text-sm font-bold step-circle';
      if (text) text.className = 'text-sm font-semibold text-gray-600';
    }
  });

  // Atualizar barra de progresso
  const progressBar = document.querySelector('.progress-bar');
  const progressText = document.querySelector('.progress-text');

  if (progressBar && progressText) {
    const progressPercentage = ((stepNum - 1) / 2) * 100; // 3 etapas: 0%, 50%, 100%
    progressBar.style.width = `${progressPercentage}%`;
    progressText.textContent = `Étape ${stepNum} sur 3 (${Math.round((stepNum / 3) * 100)}%)`;
  }

  // Scroll suave para o topo
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Inicializar na primeira etapa
document.addEventListener('DOMContentLoaded', function () {
  showStep(1);

  // Adicionar eventos aos botões
  const step1Next = document.getElementById('step1-next');
  if (step1Next) {
    step1Next.addEventListener('click', () => showStep(2));
  }

  // Adicionar outros botões quando necessário
});

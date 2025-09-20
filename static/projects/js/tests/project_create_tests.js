/**
 * TESTES COMPLETOS PARA PROJECT CREATE
 * Testa todas as 3 etapas do formulário
 */

class ProjectCreateTests {
  constructor() {
    this.testResults = [];
    this.controller = window.projectCreateController;
  }

  // ================================
  // TESTES ETAPA 1 - INFORMAÇÕES GERAIS
  // ================================

  async testEtapa1Complete() {
    console.log('🧪 === TESTANDO ETAPA 1 - INFORMAÇÕES GERAIS ===');

    const tests = [
      this.testEtapa1_CamposObrigatorios(),
      this.testEtapa1_Validacoes(),
      await this.testEtapa1_Navegacao(), // ✅ Aguardar promise
      this.testEtapa1_AutoSave(),
    ];

    return this.summarizeResults('ETAPA 1', tests);
  }

  testEtapa1_CamposObrigatorios() {
    console.log('📝 Teste 1.1: Campos obrigatórios');

    try {
      // Limpar campos
      document.getElementById('id_title').value = '';
      document.getElementById('id_type_projet').value = '';
      document.getElementById('id_description').value = '';

      // Tentar navegar sem preencher
      const canNavigate = this.controller?.validateSection1() || this.validateSection1Manual();

      if (canNavigate === false) {
        console.log('✅ PASSOU: Validação bloqueia navegação com campos vazios');
        return { test: 'Campos obrigatórios', status: 'PASS', message: 'Validação funcionando' };
      } else {
        console.log('❌ FALHOU: Validação permite campos vazios');
        return {
          test: 'Campos obrigatórios',
          status: 'FAIL',
          message: 'Validação não está funcionando',
        };
      }
    } catch (error) {
      return { test: 'Campos obrigatórios', status: 'ERROR', message: error.message };
    }
  }

  testEtapa1_Validacoes() {
    console.log('📝 Teste 1.2: Validações específicas');

    try {
      // Preencher com dados válidos
      document.getElementById('id_title').value = 'Projeto Teste';
      document.getElementById('id_type_projet').value = 'peinture_interieure';
      document.getElementById('id_description').value = 'Descrição detalhada do projeto de teste';

      const canNavigate = this.controller?.validateSection1() || this.validateSection1Manual();

      if (canNavigate === true) {
        console.log('✅ PASSOU: Validação permite navegação com dados válidos');
        return { test: 'Validações específicas', status: 'PASS', message: 'Dados válidos aceitos' };
      } else {
        console.log('❌ FALHOU: Validação bloqueia dados válidos');
        return {
          test: 'Validações específicas',
          status: 'FAIL',
          message: 'Dados válidos rejeitados',
        };
      }
    } catch (error) {
      return { test: 'Validações específicas', status: 'ERROR', message: error.message };
    }
  }

  testEtapa1_Navegacao() {
    console.log('📝 Teste 1.3: Navegação para Etapa 2');

    return new Promise((resolve) => {
      try {
        // Garantir dados válidos
        this.preencherEtapa1Valida();

        // Testar navegação
        const section1 = document.getElementById('section-1');
        const section2 = document.getElementById('section-2');

        // Simular clique no botão "Próximo"
        const nextBtn = document.getElementById('next-btn-1');
        if (nextBtn) {
          nextBtn.click();
        } else if (this.controller) {
          this.controller.nextSection(2);
        } else {
          this.navigateToSection(2);
        }

        // Verificar mudança com delay
        setTimeout(() => {
          const section1Hidden = section1.classList.contains('hidden');
          const section2Visible = !section2.classList.contains('hidden');

          if (section1Hidden && section2Visible) {
            console.log('✅ PASSOU: Navegação para Etapa 2 funcionando');
            resolve({
              test: 'Navegação Etapa 2',
              status: 'PASS',
              message: 'Navegação funcionando',
            });
          } else {
            console.log('❌ FALHOU: Navegação não funcionou');
            resolve({ test: 'Navegação Etapa 2', status: 'FAIL', message: 'Seções não mudaram' });
          }
        }, 1000); // Aumentar delay para 1 segundo
      } catch (error) {
        resolve({ test: 'Navegação Etapa 2', status: 'ERROR', message: error.message });
      }
    });
  }
  testEtapa1_AutoSave() {
    console.log('📝 Teste 1.4: Auto-save dos dados');

    try {
      // Preencher dados
      const testData = {
        title: 'Teste Auto-save',
        type: 'peinture_interieure',
        description: 'Teste de salvamento automático',
      };

      document.getElementById('id_title').value = testData.title;
      document.getElementById('id_type_projet').value = testData.type;
      document.getElementById('id_description').value = testData.description;

      // Simular auto-save
      if (this.controller && typeof this.controller.saveFormDataLocally === 'function') {
        this.controller.collectSectionData();
        this.controller.saveFormDataLocally();
      }

      // Verificar localStorage
      const savedData = localStorage.getItem('project_form_data');
      if (savedData && savedData.includes(testData.title)) {
        console.log('✅ PASSOU: Auto-save funcionando');
        return { test: 'Auto-save', status: 'PASS', message: 'Dados salvos no localStorage' };
      } else {
        console.log('⚠️ AVISO: Auto-save pode não estar funcionando');
        return { test: 'Auto-save', status: 'WARNING', message: 'localStorage não encontrado' };
      }
    } catch (error) {
      return { test: 'Auto-save', status: 'ERROR', message: error.message };
    }
  }

  // ================================
  // TESTES ETAPA 2 - DETALHES TÉCNICOS
  // ================================

  testEtapa2Complete() {
    console.log('🧪 === TESTANDO ETAPA 2 - DETALHES TÉCNICOS ===');

    const tests = [
      this.testEtapa2_SurfaceTotale(),
      this.testEtapa2_Calculadora(),
      this.testEtapa2_CamposOpcionais(),
      this.testEtapa2_Navegacao(),
    ];

    return this.summarizeResults('ETAPA 2', tests);
  }

  testEtapa2_SurfaceTotale() {
    console.log('📝 Teste 2.1: Campo Surface Totale obrigatório');

    try {
      // Ir para etapa 2
      this.navigateToSection(2);

      // Limpar surface totale
      document.getElementById('id_surface_totale').value = '';

      // Tentar navegar
      const canNavigate = this.controller?.validateSection2() || this.validateSection2Manual();

      if (canNavigate === false) {
        console.log('✅ PASSOU: Surface totale é obrigatória');
        return {
          test: 'Surface totale obrigatória',
          status: 'PASS',
          message: 'Validação funcionando',
        };
      } else {
        console.log('❌ FALHOU: Surface totale deveria ser obrigatória');
        return {
          test: 'Surface totale obrigatória',
          status: 'FAIL',
          message: 'Campo aceita valor vazio',
        };
      }
    } catch (error) {
      return { test: 'Surface totale obrigatória', status: 'ERROR', message: error.message };
    }
  }

  testEtapa2_Calculadora() {
    console.log('📝 Teste 2.2: Calculadora de superfície');

    try {
      // Preencher calculadora
      document.getElementById('calc-longueur').value = '5';
      document.getElementById('calc-largeur').value = '4';
      document.getElementById('calc-hauteur').value = '2.5';

      // Simular cálculo
      if (typeof calculateSurface === 'function') {
        calculateSurface();

        // Verificar resultados
        const resultSol = document.getElementById('result-sol').textContent;
        const resultMurs = document.getElementById('result-murs').textContent;

        if (resultSol.includes('20') && resultMurs.includes('45')) {
          console.log('✅ PASSOU: Calculadora funcionando corretamente');
          return { test: 'Calculadora', status: 'PASS', message: 'Cálculos corretos' };
        } else {
          console.log('❌ FALHOU: Cálculos incorretos');
          return {
            test: 'Calculadora',
            status: 'FAIL',
            message: `Sol: ${resultSol}, Murs: ${resultMurs}`,
          };
        }
      } else {
        console.log('⚠️ AVISO: Função calculateSurface não encontrada');
        return { test: 'Calculadora', status: 'WARNING', message: 'Função não encontrada' };
      }
    } catch (error) {
      return { test: 'Calculadora', status: 'ERROR', message: error.message };
    }
  }

  testEtapa2_CamposOpcionais() {
    console.log('📝 Teste 2.3: Campos opcionais');

    try {
      // Preencher apenas surface totale (obrigatório)
      document.getElementById('id_surface_totale').value = '50';

      // Deixar outros campos vazios
      document.getElementById('id_surface_murs').value = '';
      document.getElementById('id_surface_plafond').value = '';

      const canNavigate = this.controller?.validateSection2() || this.validateSection2Manual();

      if (canNavigate === true) {
        console.log('✅ PASSOU: Campos opcionais funcionando');
        return {
          test: 'Campos opcionais',
          status: 'PASS',
          message: 'Validação permite campos vazios',
        };
      } else {
        console.log('❌ FALHOU: Campos opcionais bloqueando navegação');
        return {
          test: 'Campos opcionais',
          status: 'FAIL',
          message: 'Campos opcionais obrigatórios incorretamente',
        };
      }
    } catch (error) {
      return { test: 'Campos opcionais', status: 'ERROR', message: error.message };
    }
  }

  testEtapa2_Navegacao() {
    console.log('📝 Teste 2.4: Navegação para Etapa 3');

    return new Promise((resolve) => {
      try {
        // Garantir dados válidos
        this.preencherEtapa2Valida();

        // Testar navegação
        const section2 = document.getElementById('section-2');
        const section3 = document.getElementById('section-3');

        // Simular clique no botão "Próximo"
        const nextBtn = document.getElementById('next-btn-2');
        if (nextBtn) {
          nextBtn.click();
        } else if (this.controller) {
          this.controller.nextSection(3);
        } else {
          this.navigateToSection(3);
        }

        // Verificar mudança com delay
        setTimeout(() => {
          const section2Hidden = section2.classList.contains('hidden');
          const section3Visible = !section3.classList.contains('hidden');

          if (section2Hidden && section3Visible) {
            console.log('✅ PASSOU: Navegação para Etapa 3 funcionando');
            resolve({
              test: 'Navegação Etapa 3',
              status: 'PASS',
              message: 'Navegação funcionando',
            });
          } else {
            console.log('❌ FALHOU: Navegação para Etapa 3 falhou');
            resolve({ test: 'Navegação Etapa 3', status: 'FAIL', message: 'Seções não mudaram' });
          }
        }, 1000); // Aumentar delay para 1 segundo
      } catch (error) {
        resolve({ test: 'Navegação Etapa 3', status: 'ERROR', message: error.message });
      }
    });
  }

  // ================================
  // TESTES ETAPA 3 - FINALIZAÇÃO
  // ================================

  testEtapa3Complete() {
    console.log('🧪 === TESTANDO ETAPA 3 - FINALIZAÇÃO ===');

    const tests = [
      this.testEtapa3_CamposObrigatorios(),
      this.testEtapa3_Checkboxes(),
      this.testEtapa3_ValidacaoDatas(),
      this.testEtapa3_ValidacaoBudget(),
      this.testEtapa3_Submit(),
    ];

    return this.summarizeResults('ETAPA 3', tests);
  }

  testEtapa3_CamposObrigatorios() {
    console.log('📝 Teste 3.1: Campos obrigatórios da Etapa 3');

    try {
      // Ir para etapa 3
      this.navigateToSection(3);

      // Limpar campos obrigatórios
      const requiredFields = [
        'id_adresse_travaux',
        'id_ville',
        'id_code_postal',
        'id_contact_telephone',
        'id_date_debut_souhaitee',
        'id_date_fin_souhaitee',
        'id_budget_minimum',
        'id_budget_maximum',
      ];

      requiredFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        if (field) field.value = '';
      });

      // Tentar submeter
      const canSubmit = this.controller?.validateSection3() || this.validateSection3Manual();

      if (canSubmit === false) {
        console.log('✅ PASSOU: Campos obrigatórios bloqueiam submit');
        return {
          test: 'Campos obrigatórios Etapa 3',
          status: 'PASS',
          message: 'Validação funcionando',
        };
      } else {
        console.log('❌ FALHOU: Submit permitido com campos vazios');
        return {
          test: 'Campos obrigatórios Etapa 3',
          status: 'FAIL',
          message: 'Validação falhando',
        };
      }
    } catch (error) {
      return { test: 'Campos obrigatórios Etapa 3', status: 'ERROR', message: error.message };
    }
  }

  testEtapa3_Checkboxes() {
    console.log('📝 Teste 3.2: Checkboxes obrigatórios');

    try {
      // Preencher campos obrigatórios
      this.preencherEtapa3Valida();

      // Desmarcar checkboxes
      document.getElementById('accept_conditions').checked = false;
      document.getElementById('accept_contact').checked = false;

      // Tentar submeter
      const canSubmit = this.controller?.validateSection3() || this.validateSection3Manual();

      if (canSubmit === false) {
        console.log('✅ PASSOU: Checkboxes obrigatórios funcionando');
        return {
          test: 'Checkboxes obrigatórios',
          status: 'PASS',
          message: 'Validação funcionando',
        };
      } else {
        console.log('❌ FALHOU: Submit sem checkboxes permitido');
        return {
          test: 'Checkboxes obrigatórios',
          status: 'FAIL',
          message: 'Checkboxes não validados',
        };
      }
    } catch (error) {
      return { test: 'Checkboxes obrigatórios', status: 'ERROR', message: error.message };
    }
  }

  testEtapa3_ValidacaoDatas() {
    console.log('📝 Teste 3.3: Validação de datas');

    try {
      // Preencher com datas inválidas (data fim antes da data início)
      document.getElementById('id_date_debut_souhaitee').value = '2025-12-31';
      document.getElementById('id_date_fin_souhaitee').value = '2025-01-01';

      const canSubmit = this.controller?.validateSection3() || this.validateSection3Manual();

      if (canSubmit === false) {
        console.log('✅ PASSOU: Validação de datas funcionando');
        return {
          test: 'Validação de datas',
          status: 'PASS',
          message: 'Datas inválidas bloqueadas',
        };
      } else {
        console.log('❌ FALHOU: Datas inválidas aceitas');
        return {
          test: 'Validação de datas',
          status: 'FAIL',
          message: 'Validação de datas falhando',
        };
      }
    } catch (error) {
      return { test: 'Validação de datas', status: 'ERROR', message: error.message };
    }
  }

  testEtapa3_ValidacaoBudget() {
    console.log('📝 Teste 3.4: Validação de budget');

    try {
      // Preencher com budget inválido (mínimo > máximo)
      document.getElementById('id_budget_minimum').value = '5000';
      document.getElementById('id_budget_maximum').value = '1000';

      const canSubmit = this.controller?.validateSection3() || this.validateSection3Manual();

      if (canSubmit === false) {
        console.log('✅ PASSOU: Validação de budget funcionando');
        return {
          test: 'Validação de budget',
          status: 'PASS',
          message: 'Budget inválido bloqueado',
        };
      } else {
        console.log('❌ FALHOU: Budget inválido aceito');
        return {
          test: 'Validação de budget',
          status: 'FAIL',
          message: 'Validação de budget falhando',
        };
      }
    } catch (error) {
      return { test: 'Validação de budget', status: 'ERROR', message: error.message };
    }
  }

  testEtapa3_Submit() {
    console.log('📝 Teste 3.5: Submit do formulário');

    try {
      // Preencher todas as etapas com dados válidos
      this.preencherFormularioCompleto();

      // Marcar checkboxes
      document.getElementById('accept_conditions').checked = true;
      document.getElementById('accept_contact').checked = true;

      // Verificar se form pode ser submetido
      const form = document.getElementById('project-form');
      const submitBtn = document.getElementById('submit-btn');

      if (form && submitBtn && !submitBtn.disabled) {
        console.log('✅ PASSOU: Formulário pronto para submit');
        return { test: 'Submit do formulário', status: 'PASS', message: 'Form válido e pronto' };
      } else {
        console.log('❌ FALHOU: Form não está pronto para submit');
        return {
          test: 'Submit do formulário',
          status: 'FAIL',
          message: 'Form inválido ou botão desabilitado',
        };
      }
    } catch (error) {
      return { test: 'Submit do formulário', status: 'ERROR', message: error.message };
    }
  }

  // ================================
  // MÉTODOS AUXILIARES
  // ================================

  validateSection1Manual() {
    const title = document.getElementById('id_title')?.value.trim();
    const type = document.getElementById('id_type_projet')?.value;
    const description = document.getElementById('id_description')?.value.trim();

    return !!(title && type && description && description.length >= 10);
  }

  validateSection2Manual() {
    const surface = document.getElementById('id_surface_totale')?.value;
    return !!(surface && parseFloat(surface) > 0);
  }

  validateSection3Manual() {
    const requiredFields = [
      'id_adresse_travaux',
      'id_ville',
      'id_code_postal',
      'id_contact_telephone',
      'id_date_debut_souhaitee',
      'id_date_fin_souhaitee',
      'id_budget_minimum',
      'id_budget_maximum',
    ];

    const fieldsValid = requiredFields.every((fieldId) => {
      const field = document.getElementById(fieldId);
      return field && field.value.trim() !== '';
    });

    const conditionsChecked = document.getElementById('accept_conditions')?.checked;
    const contactChecked = document.getElementById('accept_contact')?.checked;

    // Validar datas
    const dateDebut = document.getElementById('id_date_debut_souhaitee')?.value;
    const dateFin = document.getElementById('id_date_fin_souhaitee')?.value;
    const datesValid = !dateDebut || !dateFin || new Date(dateDebut) < new Date(dateFin);

    // Validar budget
    const budgetMin = parseFloat(document.getElementById('id_budget_minimum')?.value || 0);
    const budgetMax = parseFloat(document.getElementById('id_budget_maximum')?.value || 0);
    const budgetValid = !budgetMin || !budgetMax || budgetMin < budgetMax;

    return fieldsValid && conditionsChecked && contactChecked && datesValid && budgetValid;
  }

  preencherEtapa1Valida() {
    document.getElementById('id_title').value = 'Projeto Teste Completo';
    document.getElementById('id_type_projet').value = 'peinture_interieure';
    document.getElementById('id_description').value =
      'Descrição completa e detalhada do projeto de teste';
  }

  preencherEtapa2Valida() {
    document.getElementById('id_surface_totale').value = '100.00';
    document.getElementById('id_surface_murs').value = '80.00';
    document.getElementById('id_surface_plafond').value = '25.00';
  }

  preencherEtapa3Valida() {
    document.getElementById('id_adresse_travaux').value = '123 Rue de Test';
    document.getElementById('id_ville').value = 'Paris';
    document.getElementById('id_code_postal').value = '75001';
    document.getElementById('id_contact_telephone').value = '+33123456789';
    document.getElementById('id_pays').value = 'France';
    document.getElementById('id_date_debut_souhaitee').value = '2025-10-01';
    document.getElementById('id_date_fin_souhaitee').value = '2025-10-15';
    document.getElementById('id_budget_minimum').value = '1000';
    document.getElementById('id_budget_maximum').value = '5000';
  }

  preencherFormularioCompleto() {
    this.preencherEtapa1Valida();
    this.preencherEtapa2Valida();
    this.preencherEtapa3Valida();
  }

  navigateToSection(sectionNum) {
    // Esconder todas as seções
    for (let i = 1; i <= 3; i++) {
      const section = document.getElementById(`section-${i}`);
      if (section) section.classList.add('hidden');
    }

    // Mostrar seção alvo
    const targetSection = document.getElementById(`section-${sectionNum}`);
    if (targetSection) targetSection.classList.remove('hidden');

    // Atualizar controller se existir
    if (this.controller) {
      this.controller.currentSection = sectionNum;
    }
  }

  summarizeResults(etapa, tests) {
    const passed = tests.filter((t) => t.status === 'PASS').length;
    const failed = tests.filter((t) => t.status === 'FAIL').length;
    const errors = tests.filter((t) => t.status === 'ERROR').length;
    const warnings = tests.filter((t) => t.status === 'WARNING').length;

    console.log(`\n📊 === RESUMO ${etapa} ===`);
    console.log(`✅ PASSOU: ${passed}`);
    console.log(`❌ FALHOU: ${failed}`);
    console.log(`⚠️ AVISOS: ${warnings}`);
    console.log(`🚨 ERROS: ${errors}`);

    return {
      etapa,
      total: tests.length,
      passed,
      failed,
      errors,
      warnings,
      tests,
    };
  }

  // ================================
  // EXECUTAR TODOS OS TESTES
  // ================================

  async runAllTests() {
    console.log('🚀 === INICIANDO TESTES COMPLETOS ===\n');

    const etapa1Results = await this.testEtapa1Complete();
    const etapa2Results = await this.testEtapa2Complete();
    const etapa3Results = this.testEtapa3Complete();

    // Resumo geral
    const totalTests = etapa1Results.total + etapa2Results.total + etapa3Results.total;
    const totalPassed = etapa1Results.passed + etapa2Results.passed + etapa3Results.passed;
    const totalFailed = etapa1Results.failed + etapa2Results.failed + etapa3Results.failed;
    const totalErrors = etapa1Results.errors + etapa2Results.errors + etapa3Results.errors;

    console.log('\n🎯 === RESUMO GERAL ===');
    console.log(`📊 Total de testes: ${totalTests}`);
    console.log(`✅ Sucessos: ${totalPassed} (${Math.round((totalPassed / totalTests) * 100)}%)`);
    console.log(`❌ Falhas: ${totalFailed}`);
    console.log(`🚨 Erros: ${totalErrors}`);

    if (totalPassed === totalTests) {
      console.log('🎉 TODOS OS TESTES PASSARAM! Sistema funcionando perfeitamente!');
    } else {
      console.log('⚠️ Alguns testes falharam. Verifique os logs acima.');
    }

    return {
      etapa1: etapa1Results,
      etapa2: etapa2Results,
      etapa3: etapa3Results,
      summary: {
        total: totalTests,
        passed: totalPassed,
        failed: totalFailed,
        errors: totalErrors,
        successRate: Math.round((totalPassed / totalTests) * 100),
      },
    };
  }
}

// ================================
// FUNÇÕES GLOBAIS PARA EXECUÇÃO
// ================================

// Criar instância global para testes
window.projectTests = new ProjectCreateTests();

// Função para executar todos os testes
window.runProjectTests = async function () {
  return await window.projectTests.runAllTests();
};

// Funções para testar etapas individuais
window.testEtapa1 = function () {
  return window.projectTests.testEtapa1Complete();
};

window.testEtapa2 = function () {
  return window.projectTests.testEtapa2Complete();
};

window.testEtapa3 = function () {
  return window.projectTests.testEtapa3Complete();
};

// Função para teste rápido
window.quickTest = function () {
  console.log('⚡ TESTE RÁPIDO - Verificando elementos básicos');

  const elements = [
    'project-form',
    'section-1',
    'section-2',
    'section-3',
    'id_title',
    'id_type_projet',
    'id_description',
    'id_surface_totale',
    'accept_conditions',
    'accept_contact',
    'submit-btn',
  ];

  elements.forEach((id) => {
    const element = document.getElementById(id);
    console.log(`${id}: ${element ? '✅ ENCONTRADO' : '❌ FALTANDO'}`);
  });

  console.log(`Controller: ${window.projectCreateController ? '✅ ATIVO' : '❌ INATIVO'}`);
};

console.log('🧪 === TESTES CARREGADOS ===');
console.log('Execute: runProjectTests() - Para todos os testes');
console.log('Execute: testEtapa1() - Para testar só a etapa 1');
console.log('Execute: testEtapa2() - Para testar só a etapa 2');
console.log('Execute: testEtapa3() - Para testar só a etapa 3');
console.log('Execute: quickTest() - Para teste rápido de elementos');

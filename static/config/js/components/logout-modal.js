/**
 * Componente Modal de Logout
 * Gerencia a exibição e interação do modal de confirmação de logout
 */

class LogoutModal {
  constructor() {
    this.modal = null;
    this.modalContent = null;
    this.init();
  }

  init() {
    // Aguardar o DOM estar carregado
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setupModal());
    } else {
      this.setupModal();
    }
  }

  setupModal() {
    this.modal = document.getElementById('logoutModal');
    this.modalContent = document.getElementById('logoutModalContent');

    if (!this.modal || !this.modalContent) {
      console.warn('Modal de logout não encontrado no DOM');
      return;
    }

    this.bindEvents();
  }

  bindEvents() {
    // Fechar modal ao clicar fora dele
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.close();
      }
    });

    // Fechar modal com tecla ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) {
        this.close();
      }
    });

    // Prevenir scroll do body quando modal estiver aberto
    this.modal.addEventListener('transitionend', (e) => {
      if (e.target === this.modal && this.modal.classList.contains('hidden')) {
        document.body.style.overflow = '';
      }
    });
  }

  open() {
    if (!this.modal || !this.modalContent) return;

    // Mostrar modal
    this.modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Animação de entrada
    requestAnimationFrame(() => {
      this.modalContent.classList.remove('scale-95', 'opacity-0');
      this.modalContent.classList.add('scale-100', 'opacity-100');
    });

    // Focar no primeiro botão
    setTimeout(() => {
      const firstButton = this.modal.querySelector('button');
      if (firstButton) firstButton.focus();
    }, 100);
  }

  close() {
    if (!this.modal || !this.modalContent) return;

    // Animação de saída
    this.modalContent.classList.remove('scale-100', 'opacity-100');
    this.modalContent.classList.add('scale-95', 'opacity-0');

    // Esconder modal após animação
    setTimeout(() => {
      this.modal.classList.add('hidden');
      document.body.style.overflow = '';
    }, 300);
  }

  isOpen() {
    return this.modal && !this.modal.classList.contains('hidden');
  }

  toggle() {
    if (this.isOpen()) {
      this.close();
    } else {
      this.open();
    }
  }
}

// Instanciar o modal
const logoutModal = new LogoutModal();

// Funções globais para compatibilidade
function openLogoutModal() {
  logoutModal.open();
}

function closeLogoutModal() {
  logoutModal.close();
}

// Exportar para uso em módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LogoutModal;
}

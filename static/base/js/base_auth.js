// Global utilities and base functionality
window.LopesPeinture = {
  // Toast notification system
  showToast: function (message, type = 'info', duration = 5000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const toastId = 'toast-' + Date.now();

    const typeClasses = {
      success: 'bg-green-500 border-green-600',
      error: 'bg-red-500 border-red-600',
      warning: 'bg-yellow-500 border-yellow-600',
      info: 'bg-blue-500 border-blue-600',
    };

    const typeIcons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle',
    };

    toast.id = toastId;
    toast.className = `${
      typeClasses[type] || typeClasses.info
    } text-white px-6 py-4 rounded-lg shadow-lg border-l-4 transform translate-x-full transition-transform duration-300 ease-in-out mb-2 max-w-sm`;

    toast.innerHTML = `
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <i class="fas ${typeIcons[type] || typeIcons.info} mr-3" aria-hidden="true"></i>
                <span class="font-medium">${message}</span>
              </div>
              <button 
                onclick="LopesPeinture.hideToast('${toastId}')" 
                class="ml-4 text-white hover:text-gray-200 focus:outline-none focus:ring-2 focus:ring-white focus:ring-opacity-50 rounded"
                aria-label="Fermer la notification"
              >
                <i class="fas fa-times" aria-hidden="true"></i>
              </button>
            </div>
          `;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.classList.remove('translate-x-full');
    }, 100);

    // Auto remove
    if (duration > 0) {
      setTimeout(() => {
        this.hideToast(toastId);
      }, duration);
    }
  },

  hideToast: function (toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
      toast.classList.add('translate-x-full');
      setTimeout(() => {
        toast.remove();
      }, 300);
    }
  },

  // Loading overlay
  showLoading: function () {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.classList.remove('hidden');
    }
  },

  hideLoading: function () {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
      overlay.classList.add('hidden');
    }
  },

  // Form utilities
  validateEmail: function (email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  validatePassword: function (password) {
    return {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };
  },

  // Phone number formatting (French)
  formatPhoneNumber: function (value) {
    const cleaned = value.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$/);
    if (match) {
      return `${match[1]} ${match[2]} ${match[3]} ${match[4]} ${match[5]}`;
    }
    return value;
  },

  // CSRF token helper
  getCSRFToken: function () {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  },

  // Accessibility helpers
  announceToScreenReader: function (message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  },
};

// DOM Ready functionality
document.addEventListener('DOMContentLoaded', function () {
  // Initialize form enhancements
  initializeFormEnhancements();

  // Initialize accessibility features
  initializeAccessibility();

  // Initialize animations
  initializeAnimations();

  // Handle Django messages
  handleDjangoMessages();
});

function initializeFormEnhancements() {
  // Auto-focus management
  const firstErrorField = document.querySelector('input.border-red-500, .error input');
  const firstInput = document.querySelector(
    'input:not([type="hidden"]):not([type="checkbox"]):not([disabled])'
  );

  if (firstErrorField) {
    firstErrorField.focus();
    firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
  } else if (firstInput && !firstInput.value) {
    firstInput.focus();
  }

  // Enhanced input validation
  const inputs = document.querySelectorAll(
    'input[type="email"], input[type="password"], input[type="text"]'
  );
  inputs.forEach((input) => {
    // Remove error styling on input
    input.addEventListener('input', function () {
      this.classList.remove('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
      this.classList.add('border-gray-300', 'focus:border-blue-500', 'focus:ring-blue-500');

      // Remove error message if exists
      const errorMsg = this.parentNode.querySelector('.error-message');
      if (errorMsg) {
        errorMsg.remove();
      }
    });

    // Email validation
    if (input.type === 'email') {
      input.addEventListener('blur', function () {
        if (this.value && !LopesPeinture.validateEmail(this.value)) {
          this.classList.add('border-red-500', 'focus:border-red-500', 'focus:ring-red-500');
          showFieldError(this, 'Veuillez entrer une adresse email valide');
        }
      });
    }

    // Phone number formatting
    if (input.name === 'phone' || input.id === 'phone') {
      input.addEventListener('input', function () {
        this.value = LopesPeinture.formatPhoneNumber(this.value);
      });
    }
  });

  // Form submission handling
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', function (e) {
      const submitButton = this.querySelector('button[type="submit"]');
      if (submitButton && !submitButton.disabled) {
        // Show loading state
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.innerHTML =
          '<i class="fas fa-spinner fa-spin mr-2" aria-hidden="true"></i>Traitement...';

        // Reset after timeout to prevent permanent disabled state
        setTimeout(() => {
          if (submitButton.disabled) {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
          }
        }, 10000);
      }
    });
  });
}

function initializeAccessibility() {
  // Keyboard navigation for custom elements
  document.addEventListener('keydown', function (e) {
    // ESC key handling for modals
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('.modal:not(.hidden)');
      modals.forEach((modal) => {
        if (typeof closeModal === 'function') {
          closeModal();
        }
      });
    }
  });

  // Skip link functionality
  const skipLink = document.querySelector('.skip-link');
  if (skipLink) {
    skipLink.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.focus();
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }
}

function initializeAnimations() {
  // Intersection Observer for animations
  if ('IntersectionObserver' in window) {
    const animatedElements = document.querySelectorAll('[class*="animate-"]');

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px',
      }
    );

    animatedElements.forEach((el) => observer.observe(el));
  }
}

function handleDjangoMessages() {
  // Convert Django messages to toast notifications
  const messages = document.querySelectorAll('.django-message');
  messages.forEach((message) => {
    const type = message.dataset.type || 'info';
    const text = message.textContent.trim();

    if (text) {
      LopesPeinture.showToast(text, type);
    }

    // Hide the original message
    message.style.display = 'none';
  });
}

function showFieldError(field, message) {
  // Remove existing error message
  const existingError = field.parentNode.querySelector('.error-message');
  if (existingError) {
    existingError.remove();
  }

  // Create new error message
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message text-red-600 text-sm mt-1 flex items-center';
  errorDiv.innerHTML = `<i class="fas fa-exclamation-circle mr-1" aria-hidden="true"></i>${message}`;

  field.parentNode.appendChild(errorDiv);

  // Announce to screen readers
  LopesPeinture.announceToScreenReader(`Erreur: ${message}`);
}

// Password toggle functionality
window.togglePassword = function (fieldId, button) {
  const field = document.getElementById(fieldId);
  const icon = button.querySelector('i');

  if (!field || !icon) return;

  if (field.type === 'password') {
    field.type = 'text';
    icon.classList.remove('fa-eye');
    icon.classList.add('fa-eye-slash');
    button.setAttribute('aria-label', 'Masquer le mot de passe');
    button.setAttribute('title', 'Masquer le mot de passe');
  } else {
    field.type = 'password';
    icon.classList.remove('fa-eye-slash');
    icon.classList.add('fa-eye');
    button.setAttribute('aria-label', 'Afficher le mot de passe');
    button.setAttribute('title', 'Afficher le mot de passe');
  }

  // Maintain focus on the input field
  field.focus();
};

// Enhanced password strength indicator
window.checkPasswordStrength = function (password, targetId) {
  const target = document.getElementById(targetId);
  if (!target) return;

  const checks = LopesPeinture.validatePassword(password);
  const strength = Object.values(checks).filter(Boolean).length;

  let strengthText = '';
  let strengthClass = '';

  if (password.length === 0) {
    target.innerHTML = '';
    return;
  }

  switch (strength) {
    case 0:
    case 1:
      strengthText = 'Très faible';
      strengthClass = 'text-red-600';
      break;
    case 2:
      strengthText = 'Faible';
      strengthClass = 'text-orange-600';
      break;
    case 3:
      strengthText = 'Moyen';
      strengthClass = 'text-yellow-600';
      break;
    case 4:
      strengthText = 'Fort';
      strengthClass = 'text-blue-600';
      break;
    case 5:
      strengthText = 'Très fort';
      strengthClass = 'text-green-600';
      break;
  }

  const progressWidth = (strength / 5) * 100;

  target.innerHTML = `
          <div class="mt-2">
            <div class="flex justify-between items-center mb-1">
              <span class="text-sm font-medium ${strengthClass}">Force: ${strengthText}</span>
              <span class="text-xs text-gray-500">${strength}/5</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="h-2 rounded-full transition-all duration-300 ${strengthClass.replace(
                'text-',
                'bg-'
              )}" style="width: ${progressWidth}%"></div>
            </div>
            <div class="mt-2 text-xs text-gray-600 space-y-1">
              <div class="flex items-center ${checks.length ? 'text-green-600' : 'text-gray-400'}">
                <i class="fas ${
                  checks.length ? 'fa-check' : 'fa-times'
                } mr-2" aria-hidden="true"></i>
                Au moins 8 caractères
              </div>
              <div class="flex items-center ${
                checks.uppercase ? 'text-green-600' : 'text-gray-400'
              }">
                <i class="fas ${
                  checks.uppercase ? 'fa-check' : 'fa-times'
                } mr-2" aria-hidden="true"></i>
                Une majuscule
              </div>
              <div class="flex items-center ${
                checks.lowercase ? 'text-green-600' : 'text-gray-400'
              }">
                <i class="fas ${
                  checks.lowercase ? 'fa-check' : 'fa-times'
                } mr-2" aria-hidden="true"></i>
                Une minuscule
              </div>
              <div class="flex items-center ${checks.number ? 'text-green-600' : 'text-gray-400'}">
                <i class="fas ${
                  checks.number ? 'fa-check' : 'fa-times'
                } mr-2" aria-hidden="true"></i>
                Un chiffre
              </div>
              <div class="flex items-center ${checks.special ? 'text-green-600' : 'text-gray-400'}">
                <i class="fas ${
                  checks.special ? 'fa-check' : 'fa-times'
                } mr-2" aria-hidden="true"></i>
                Un caractère spécial
              </div>
            </div>
          </div>
        `;
};

// Email availability checker
window.checkEmailAvailability = function (email, targetId) {
  const target = document.getElementById(targetId);
  if (!target || !email || !LopesPeinture.validateEmail(email)) {
    if (target) target.innerHTML = '';
    return;
  }

  target.innerHTML =
    '<div class="text-sm text-gray-500 mt-1"><i class="fas fa-spinner fa-spin mr-2" aria-hidden="true"></i>Vérification...</div>';

  fetch('{% url "accounts:check_email_exists" %}', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': LopesPeinture.getCSRFToken(),
    },
    body: `email=${encodeURIComponent(email)}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.exists) {
        target.innerHTML =
          '<div class="text-sm text-red-600 mt-1 flex items-center"><i class="fas fa-exclamation-circle mr-2" aria-hidden="true"></i>Cette adresse email est déjà utilisée</div>';
      } else {
        target.innerHTML =
          '<div class="text-sm text-green-600 mt-1 flex items-center"><i class="fas fa-check-circle mr-2" aria-hidden="true"></i>Adresse email disponible</div>';
      }
    })
    .catch((error) => {
      console.error('Error checking email:', error);
      target.innerHTML =
        '<div class="text-sm text-gray-500 mt-1"><i class="fas fa-exclamation-triangle mr-2" aria-hidden="true"></i>Impossible de vérifier l\'email</div>';
    });
};

// Debounce utility
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

// Apply debouncing to email check
if (typeof window.checkEmailAvailability === 'function') {
  window.checkEmailAvailability = debounce(window.checkEmailAvailability, 500);
}

// Service Worker registration for PWA capabilities
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker
      .register('/sw.js')
      .then(function (registration) {
        console.log('ServiceWorker registration successful');
      })
      .catch(function (error) {
        console.log('ServiceWorker registration failed');
      });
  });
}

// Performance monitoring
window.addEventListener('load', function () {
  if ('performance' in window) {
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    if (loadTime > 3000) {
      console.warn('Page load time is slow:', loadTime + 'ms');
    }
  }
});

// Error handling for uncaught errors
window.addEventListener('error', function (e) {
  console.error('Uncaught error:', e.error);
  LopesPeinture.showToast("Une erreur inattendue s'est produite. Veuillez réessayer.", 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function (e) {
  console.error('Unhandled promise rejection:', e.reason);
  LopesPeinture.showToast(
    "Une erreur de connexion s'est produite. Veuillez vérifier votre connexion internet.",
    'error'
  );
});

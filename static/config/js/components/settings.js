// Fonctions JavaScript pour les modals et actions
function openPasswordModal() {
  document.getElementById('passwordModal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closePasswordModal() {
  document.getElementById('passwordModal').classList.add('hidden');
  document.body.style.overflow = '';
}

function confirmDeleteAccount() {
  document.getElementById('deleteModal').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
  document.getElementById('deleteModal').classList.add('hidden');
  document.body.style.overflow = '';
}

function exportData() {
  // Mostrar loading
  const button = event.target;
  const originalText = button.innerHTML;
  button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Préparation...';
  button.disabled = true;

  // Simular export (substituir pela lógica real)
  fetch('{% url "config:export_data" %}', {
    method: 'POST',
    headers: {
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
      'Content-Type': 'application/json',
    },
  })
    .then((response) => response.blob())
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = 'mes_donnees_lopespeinture.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);

      // Restaurer le bouton
      button.innerHTML = originalText;
      button.disabled = false;

      // Notification de succès
      showNotification('Vos données ont été exportées avec succès!', 'success');
    })
    .catch((error) => {
      console.error('Erreur:', error);
      button.innerHTML = originalText;
      button.disabled = false;
      showNotification("Erreur lors de l'export des données", 'error');
    });
}

function deleteAccount() {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = '{% url "config:delete_account" %}';

  const csrfToken = document.createElement('input');
  csrfToken.type = 'hidden';
  csrfToken.name = 'csrfmiddlewaretoken';
  csrfToken.value = document.querySelector('[name=csrfmiddlewaretoken]').value;

  form.appendChild(csrfToken);
  document.body.appendChild(form);
  form.submit();
}

function viewLoginHistory() {
  window.location.href = '{% url "config:login_history" %}';
}

function showNotification(message, type = 'info') {
  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 z-50 ${colors[type]} border px-4 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full max-w-sm`;
  notification.innerHTML = `
                    <div class="flex items-center">
                      <i class="fas fa-${
                        type === 'success'
                          ? 'check-circle'
                          : type === 'error'
                          ? 'exclamation-circle'
                          : 'info-circle'
                      } mr-2"></i>
                      <span class="text-sm">${message}</span>
                      <button onclick="this.parentElement.parentElement.remove()" class="ml-4 hover:opacity-75">
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.classList.remove('translate-x-full');
  }, 100);

  setTimeout(() => {
    notification.classList.add('translate-x-full');
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

// Fechar modals ao clicar fora
document.addEventListener('click', function (e) {
  if (e.target.id === 'passwordModal') {
    closePasswordModal();
  }
  if (e.target.id === 'deleteModal') {
    closeDeleteModal();
  }
});

// Fechar modals com ESC
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    closePasswordModal();
    closeDeleteModal();
  }
});

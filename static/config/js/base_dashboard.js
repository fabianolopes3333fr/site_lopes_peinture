document.addEventListener('DOMContentLoaded', function () {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const sidebarOverlay = document.getElementById('sidebarOverlay');
        let sidebarCollapsed = false;
        let isMobile = window.innerWidth < 1024;

        // Toggle Sidebar Function
        function toggleSidebar() {
          if (isMobile) {
            // Mobile: Show/Hide sidebar with overlay
            sidebar.classList.toggle('-translate-x-full');
            sidebarOverlay.classList.toggle('hidden');
          } else {
            // Desktop: Collapse/Expand sidebar
            sidebarCollapsed = !sidebarCollapsed;

            if (sidebarCollapsed) {
              sidebar.classList.add('sidebar-collapsed');
              sidebar.querySelector('.sidebar-header-text').style.display = 'none';
              sidebar.querySelector('.sidebar-header-icon').style.display = 'block';
              mainContent.classList.remove('content-normal');
              mainContent.classList.add('content-expanded');
            } else {
              sidebar.classList.remove('sidebar-collapsed');
              sidebar.querySelector('.sidebar-header-text').style.display = 'block';
              sidebar.querySelector('.sidebar-header-icon').style.display = 'none';
              mainContent.classList.remove('content-expanded');
              mainContent.classList.add('content-normal');
            }
          }
        }

        // Event Listeners
        sidebarToggle.addEventListener('click', toggleSidebar);

        // Close sidebar on overlay click (mobile)
        sidebarOverlay.addEventListener('click', function () {
          if (isMobile) {
            sidebar.classList.add('-translate-x-full');
            sidebarOverlay.classList.add('hidden');
          }
        });

        // Handle window resize
        window.addEventListener('resize', function () {
          const newIsMobile = window.innerWidth < 1024;

          if (newIsMobile !== isMobile) {
            isMobile = newIsMobile;

            if (isMobile) {
              // Switch to mobile mode
              sidebar.classList.remove('sidebar-collapsed');
              sidebar.classList.add('-translate-x-full');
              sidebar.querySelector('.sidebar-header-text').style.display = 'block';
              sidebar.querySelector('.sidebar-header-icon').style.display = 'none';
              mainContent.classList.remove('content-expanded', 'content-normal');
              sidebarOverlay.classList.add('hidden');
              sidebarCollapsed = false;
            } else {
              // Switch to desktop mode
              sidebar.classList.remove('-translate-x-full');
              sidebarOverlay.classList.add('hidden');

              if (sidebarCollapsed) {
                sidebar.classList.add('sidebar-collapsed');
                sidebar.querySelector('.sidebar-header-text').style.display = 'none';
                sidebar.querySelector('.sidebar-header-icon').style.display = 'block';
                mainContent.classList.add('content-expanded');
              } else {
                mainContent.classList.add('content-normal');
              }
            }
          }
        });

        // Initialize mobile state
        if (isMobile) {
          sidebar.classList.add('-translate-x-full');
          mainContent.classList.remove('content-normal', 'content-expanded');
        }

        // Close mobile sidebar on escape key
        document.addEventListener('keydown', function (e) {
          if (e.key === 'Escape' && isMobile && !sidebar.classList.contains('-translate-x-full')) {
            sidebar.classList.add('-translate-x-full');
            sidebarOverlay.classList.add('hidden');
          }
        });

        // Prevent body scroll when mobile sidebar is open
        const observer = new MutationObserver(function (mutations) {
          mutations.forEach(function (mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
              if (isMobile) {
                if (sidebar.classList.contains('-translate-x-full')) {
                  document.body.style.overflow = '';
                } else {
                  document.body.style.overflow = 'hidden';
                }
              } else {
                document.body.style.overflow = '';
              }
            }
          });
        });

        observer.observe(sidebar, { attributes: true });

        // Handle command buttons (for modals, etc.)
        document.addEventListener('click', function (e) {
          const commandButton = e.target.closest('[command]');
          if (commandButton) {
            const command = commandButton.getAttribute('command');
            const commandFor = commandButton.getAttribute('commandfor');

            if (command === 'show-modal' && commandFor) {
              const modal = document.getElementById(commandFor);
              if (modal) {
                modal.classList.remove('hidden');
                modal.classList.add('flex');
                document.body.style.overflow = 'hidden';
              }
            }
          }
        });

        // Auto-hide alerts after 5 seconds
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
          setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease-out';
            alert.style.opacity = '0';
            setTimeout(function () {
              alert.remove();
            }, 500);
          }, 5000);
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
          anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
              target.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
              });
            }
          });
        });

        // Add loading state to buttons
        document.addEventListener('click', function (e) {
          const button = e.target.closest('button[type="submit"], .btn-loading');
          if (button && !button.disabled) {
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Chargement...';

            // Reset after 3 seconds (fallback)
            setTimeout(function () {
              button.disabled = false;
              button.innerHTML = originalText;
            }, 3000);
          }
        });

        // Initialize tooltips for collapsed sidebar
        function initTooltips() {
          const tooltipElements = document.querySelectorAll('.sidebar-tooltip');
          tooltipElements.forEach(function (tooltip) {
            const parent = tooltip.parentElement;

            parent.addEventListener('mouseenter', function () {
              if (sidebar.classList.contains('sidebar-collapsed')) {
                tooltip.style.opacity = '1';
                tooltip.style.visibility = 'visible';
              }
            });

            parent.addEventListener('mouseleave', function () {
              tooltip.style.opacity = '0';
              tooltip.style.visibility = 'hidden';
            });
          });
        }

        initTooltips();

        // Performance optimization: Debounce resize events
        let resizeTimeout;
        window.addEventListener('resize', function () {
          clearTimeout(resizeTimeout);
          resizeTimeout = setTimeout(function () {
            // Additional resize logic if needed
          }, 250);
        });

        // Add focus management for accessibility
        document.addEventListener('keydown', function (e) {
          // Tab navigation improvements
          if (e.key === 'Tab') {
            const focusableElements = document.querySelectorAll(
              'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey && document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        });

        // Console log for debugging (remove in production)
        console.log('Dashboard initialized successfully');
        console.log('Mobile mode:', isMobile);
        console.log('Sidebar collapsed:', sidebarCollapsed);
      });

      // Additional utility functions
      function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-20 right-4 z-50 bg-${type}-50 border border-${type}-200 text-${type}-800 px-4 py-3 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full`;
        notification.innerHTML = `
                  <div class="flex items-center">
                    <i class="fas fa-info-circle mr-2"></i>
                    ${message}
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-${type}-600 hover:text-${type}-800">
                      <i class="fas fa-times"></i>
                    </button>
                  </div>
                `;

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
          notification.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
          notification.classList.add('translate-x-full');
          setTimeout(() => notification.remove(), 300);
        }, 5000);
      }

      // Export for global use
      window.dashboardUtils = {
        showNotification,
        toggleSidebar: function () {
          document.getElementById('sidebarToggle').click();
        },
      };
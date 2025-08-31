document.addEventListener('DOMContentLoaded', function () {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const closeSidebarBtn = document.getElementById('closeSidebarBtn');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const mobileSidebar = document.getElementById('mobileSidebar');
  const body = document.body;

  // Function to open sidebar
  function openSidebar() {
    sidebarOverlay.classList.add('active');
    mobileSidebar.classList.add('active');
    body.classList.add('sidebar-open');
  }

  // Function to close sidebar
  function closeSidebar() {
    sidebarOverlay.classList.remove('active');
    mobileSidebar.classList.remove('active');
    body.classList.remove('sidebar-open');
  }

  // Event listeners
  mobileMenuBtn.addEventListener('click', openSidebar);
  closeSidebarBtn.addEventListener('click', closeSidebar);
  sidebarOverlay.addEventListener('click', closeSidebar);

  // Close sidebar on escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileSidebar.classList.contains('active')) {
      closeSidebar();
    }
  });

  // Close sidebar when clicking on navigation links (mobile)
  const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
  mobileNavLinks.forEach((link) => {
    link.addEventListener('click', closeSidebar);
  });

  // Prevent sidebar from closing when clicking inside it
  mobileSidebar.addEventListener('click', function (e) {
    e.stopPropagation();
  });

  // Handle window resize
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 1024) {
      closeSidebar();
    }
  });

  // Track user interactions for analytics
  const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
  phoneLinks.forEach((link) => {
    link.addEventListener('click', function () {
      // Track phone clicks
      if (typeof gtag !== 'undefined') {
        gtag('event', 'phone_call', {
          event_category: 'contact',
          event_label: 'header_phone',
          value: 1,
        });
      }
    });
  });

  // Track devis button clicks
  const devisButtons = document.querySelectorAll('a[href*="contact"]');
  devisButtons.forEach((button) => {
    if (button.textContent.includes('Devis')) {
      button.addEventListener('click', function () {
        if (typeof gtag !== 'undefined') {
          gtag('event', 'devis_request', {
            event_category: 'conversion',
            event_label: 'header_devis_button',
            value: 1,
          });
        }
      });
    }
  });

  // Track navigation clicks
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
  navLinks.forEach((link) => {
    link.addEventListener('click', function () {
      const linkText = this.textContent.trim();

      if (typeof gtag !== 'undefined') {
        gtag('event', 'navigation_click', {
          event_category: 'navigation',
          event_label: linkText,
          value: 1,
        });
      }
    });
  });

  // Track user menu interactions
  const userMenuItems = document.querySelectorAll('.dropdown-item, .mobile-auth-link');
  userMenuItems.forEach((item) => {
    item.addEventListener('click', function () {
      const itemText = this.textContent.trim();

      if (typeof gtag !== 'undefined') {
        gtag('event', 'user_menu_click', {
          event_category: 'user_interaction',
          event_label: itemText,
          value: 1,
        });
      }
    });
  });

  // Enhanced dropdown behavior for desktop
  const userDropdown = document.querySelector('.group');
  if (userDropdown) {
    let dropdownTimeout;

    userDropdown.addEventListener('mouseenter', function () {
      clearTimeout(dropdownTimeout);
    });

    userDropdown.addEventListener('mouseleave', function () {
      dropdownTimeout = setTimeout(() => {
        // Additional cleanup if needed
      }, 150);
    });
  }

  // Add loading states for auth actions
  const authLinks = document.querySelectorAll(
    'a[href*="login"], a[href*="logout"], a[href*="register"]'
  );
  authLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      // Add loading state
      const icon = this.querySelector('i');
      if (icon) {
        icon.className = 'fas fa-spinner fa-spin mr-2';
      }

      // Show loading text
      const span = this.querySelector('span');
      if (span) {
        span.textContent = 'Chargement...';
      }
    });
  });

  // Initialize tooltips for user avatar (if using a tooltip library)
  const userAvatar = document.querySelector('.user-avatar');
  if (userAvatar && typeof bootstrap !== 'undefined') {
    new bootstrap.Tooltip(userAvatar, {
      title: 'Menu utilisateur',
      placement: 'bottom',
    });
  }

  // Keyboard navigation for dropdown menus
  document.addEventListener('keydown', function (e) {
    const activeDropdown = document.querySelector('.group:hover .absolute');
    if (activeDropdown && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
      e.preventDefault();
      const items = activeDropdown.querySelectorAll('a');
      const currentIndex = Array.from(items).findIndex((item) => item === document.activeElement);

      if (e.key === 'ArrowDown') {
        const nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
        items[nextIndex].focus();
      } else {
        const prevIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
        items[prevIndex].focus();
      }
    }
  });

  // Auto-hide mobile sidebar after inactivity
  let sidebarInactivityTimer;

  function resetSidebarTimer() {
    clearTimeout(sidebarInactivityTimer);
    sidebarInactivityTimer = setTimeout(() => {
      if (mobileSidebar.classList.contains('active')) {
        closeSidebar();
      }
    }, 30000); // 30 seconds of inactivity
  }

  mobileSidebar.addEventListener('click', resetSidebarTimer);
  mobileSidebar.addEventListener('touchstart', resetSidebarTimer);

  // Initialize timer when sidebar opens
  mobileMenuBtn.addEventListener('click', resetSidebarTimer);

  // Smooth scroll for anchor links
  const anchorLinks = document.querySelectorAll('a[href^="#"]');
  anchorLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);

      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });

        // Close mobile sidebar if open
        if (mobileSidebar.classList.contains('active')) {
          closeSidebar();
        }
      }
    });
  });

  // Add visual feedback for touch devices
  if ('ontouchstart' in window) {
    const touchElements = document.querySelectorAll(
      '.mobile-nav-link, .mobile-auth-link, .btn-primary'
    );

    touchElements.forEach((element) => {
      element.addEventListener('touchstart', function () {
        this.style.transform = 'scale(0.98)';
        this.style.transition = 'transform 0.1s ease';
      });

      element.addEventListener('touchend', function () {
        setTimeout(() => {
          this.style.transform = '';
        }, 100);
      });
    });
  }

  // Performance optimization: Lazy load user avatar if using external images
  const avatarImages = document.querySelectorAll('.user-avatar img');
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          img.classList.remove('lazy');
          observer.unobserve(img);
        }
      });
    });

    avatarImages.forEach((img) => imageObserver.observe(img));
  }
});

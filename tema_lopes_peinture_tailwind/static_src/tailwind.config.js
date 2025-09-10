/**
 * Tailwind CSS Configuration - Lopes Peinture
 * Configuração corrigida e otimizada para o projeto
 */

module.exports = {
  content: [
    // Templates do Django
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',

    // JavaScript files
    '../static/**/*.js',
    '../../static/**/*.js',
    '../../**/static/**/*.js',

    // Python files (for class detection)
    '../../**/*.py',
    '../**/*.py',

    // CSS files
    '../static/**/*.css',
    '../../static/**/*.css',

    // Assets
    '../static/**/*.{svg,png,jpg,jpeg,gif,webp}',
    '../../static/**/*.{svg,png,jpg,jpeg,gif,webp}',
  ],

  theme: {
    extend: {
      // Fontes do projeto
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Poppins', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },

      // Cores da marca Lopes Peinture
      colors: {
        // Cores principais da marca
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Azul principal
          600: '#2563eb', // Azul escuro
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          DEFAULT: '#2563eb',
        },

        // Cores de sucesso
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          DEFAULT: '#22c55e',
        },

        // Cores de erro/perigo
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          DEFAULT: '#ef4444',
        },

        // Cores de aviso
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          DEFAULT: '#f59e0b',
        },

        // Cores de informação
        info: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          DEFAULT: '#0ea5e9',
        },
      },

      // Gradientes customizados
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%)',
        'gradient-brand-light': 'linear-gradient(135deg, #3b82f6 0%, #60a5fa 50%, #93c5fd 100%)',
        'gradient-success': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        'gradient-danger': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'gradient-warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        'gradient-info': 'linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)',
      },

      // Sombras customizadas
      boxShadow: {
        brand: '0 4px 20px rgba(37, 99, 235, 0.3)',
        'brand-lg': '0 10px 30px rgba(37, 99, 235, 0.4)',
        success: '0 4px 20px rgba(34, 197, 94, 0.3)',
        danger: '0 4px 20px rgba(239, 68, 68, 0.3)',
        warning: '0 4px 20px rgba(245, 158, 11, 0.3)',
        info: '0 4px 20px rgba(14, 165, 233, 0.3)',
        soft: '0 2px 15px rgba(0, 0, 0, 0.08)',
        glass: '0 8px 32px rgba(31, 38, 135, 0.37)',
      },

      // Animações customizadas
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'bounce-soft': 'bounceSoft 2s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },

      // Espaçamentos extras
      spacing: {
        18: '4.5rem',
        88: '22rem',
      },

      // Z-index organizados
      zIndex: {
        dropdown: '1000',
        modal: '1050',
        tooltip: '1070',
        navbar: '1090',
      },
    },
  },

  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),

    // Plugin para botões
    function ({ addComponents, theme }) {
      addComponents({
        // Base do botão
        '.btn': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1.5rem',
          fontSize: '0.875rem',
          fontWeight: '600',
          lineHeight: '1.25rem',
          borderRadius: '0.5rem',
          border: 'none',
          textDecoration: 'none',
          cursor: 'pointer',
          transition: 'all 0.2s ease-in-out',
          outline: 'none',
          position: 'relative',

          '&:disabled': {
            opacity: '0.5',
            cursor: 'not-allowed',
          },
        },

        // Botão primário
        '.btn-primary': {
          background: theme('backgroundImage.gradient-brand'),
          color: theme('colors.white'),
          boxShadow: theme('boxShadow.brand'),

          '&:hover:not(:disabled)': {
            transform: 'translateY(-2px)',
            boxShadow: theme('boxShadow.brand-lg'),
          },

          '&:active': {
            transform: 'translateY(0)',
          },
        },

        // Botão secundário
        '.btn-secondary': {
          backgroundColor: theme('colors.white'),
          color: theme('colors.gray.700'),
          border: `2px solid ${theme('colors.gray.300')}`,

          '&:hover:not(:disabled)': {
            backgroundColor: theme('colors.gray.50'),
            borderColor: theme('colors.gray.400'),
            transform: 'translateY(-1px)',
          },
        },

        // Botão de sucesso
        '.btn-success': {
          background: theme('backgroundImage.gradient-success'),
          color: theme('colors.white'),

          '&:hover:not(:disabled)': {
            transform: 'translateY(-2px)',
            filter: 'brightness(1.1)',
          },
        },

        // Botão de perigo
        '.btn-danger': {
          background: theme('backgroundImage.gradient-danger'),
          color: theme('colors.white'),

          '&:hover:not(:disabled)': {
            transform: 'translateY(-2px)',
            filter: 'brightness(1.1)',
          },
        },

        // Botão fantasma
        '.btn-ghost': {
          backgroundColor: 'transparent',
          color: theme('colors.gray.600'),

          '&:hover:not(:disabled)': {
            backgroundColor: theme('colors.gray.100'),
            color: theme('colors.gray.900'),
          },
        },

        // Tamanhos de botão
        '.btn-sm': {
          padding: '0.5rem 1rem',
          fontSize: '0.75rem',
        },

        '.btn-lg': {
          padding: '1rem 2rem',
          fontSize: '1rem',
        },

        '.btn-icon': {
          padding: '0.75rem',
          width: '2.75rem',
          height: '2.75rem',
        },
      });
    },

    // Plugin para formulários
    function ({ addComponents, theme }) {
      addComponents({
        '.form-group': {
          marginBottom: '1.5rem',
        },

        '.form-label': {
          display: 'block',
          fontSize: '0.875rem',
          fontWeight: '500',
          color: theme('colors.gray.700'),
          marginBottom: '0.5rem',
        },

        '.form-input': {
          width: '100%',
          padding: '0.75rem 1rem',
          border: `2px solid ${theme('colors.gray.300')}`,
          borderRadius: '0.5rem',
          backgroundColor: theme('colors.white'),
          fontSize: '0.875rem',
          transition: 'all 0.2s ease-in-out',

          '&::placeholder': {
            color: theme('colors.gray.400'),
          },

          '&:focus': {
            outline: 'none',
            borderColor: theme('colors.brand.500'),
            boxShadow: `0 0 0 3px ${theme('colors.brand.100')}`,
          },

          '&.error': {
            borderColor: theme('colors.danger.500'),
            backgroundColor: theme('colors.danger.50'),
          },
        },

        '.form-select': {
          backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e")`,
          backgroundPosition: 'right 0.5rem center',
          backgroundRepeat: 'no-repeat',
          backgroundSize: '1.5em 1.5em',
          paddingRight: '2.5rem',
        },
      });
    },

    // Plugin para cards
    function ({ addComponents, theme }) {
      addComponents({
        '.card': {
          backgroundColor: theme('colors.white'),
          borderRadius: '0.75rem',
          boxShadow: theme('boxShadow.soft'),
          border: `1px solid ${theme('colors.gray.200')}`,
          overflow: 'hidden',
          transition: 'all 0.3s ease-in-out',
        },

        '.card-hover': {
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme('boxShadow.xl'),
          },
        },

        '.card-header': {
          padding: '1.5rem',
          borderBottom: `1px solid ${theme('colors.gray.200')}`,
        },

        '.card-body': {
          padding: '1.5rem',
        },

        '.card-footer': {
          padding: '1rem 1.5rem',
          backgroundColor: theme('colors.gray.50'),
          borderTop: `1px solid ${theme('colors.gray.200')}`,
        },
      });
    },

    // Plugin para badges
    function ({ addComponents, theme }) {
      addComponents({
        '.badge': {
          display: 'inline-flex',
          alignItems: 'center',
          padding: '0.25rem 0.75rem',
          fontSize: '0.75rem',
          fontWeight: '600',
          borderRadius: '9999px',
          textTransform: 'uppercase',
          letterSpacing: '0.025em',
        },

        '.badge-primary': {
          backgroundColor: theme('colors.brand.100'),
          color: theme('colors.brand.800'),
        },

        '.badge-secondary': {
          backgroundColor: theme('colors.gray.100'),
          color: theme('colors.gray.800'),
        },

        '.badge-success': {
          backgroundColor: theme('colors.success.100'),
          color: theme('colors.success.800'),
        },

        '.badge-danger': {
          backgroundColor: theme('colors.danger.100'),
          color: theme('colors.danger.800'),
        },

        '.badge-warning': {
          backgroundColor: theme('colors.warning.100'),
          color: theme('colors.warning.800'),
        },

        '.badge-info': {
          backgroundColor: theme('colors.info.100'),
          color: theme('colors.info.800'),
        },

        '.badge-outline': {
          backgroundColor: 'transparent',
          border: '1px solid currentColor',
        },
      });
    },

    // Plugin para barras de progresso
    function ({ addComponents, theme }) {
      addComponents({
        '.progress': {
          width: '100%',
          height: '0.5rem',
          backgroundColor: theme('colors.gray.200'),
          borderRadius: '9999px',
          overflow: 'hidden',
        },

        '.progress-bar': {
          height: '100%',
          backgroundColor: theme('colors.brand.500'),
          borderRadius: '9999px',
          transition: 'width 0.6s ease',
        },
      });
    },

    // Plugin para modais
    function ({ addComponents, theme }) {
      addComponents({
        '.modal-overlay': {
          position: 'fixed',
          inset: '0',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          zIndex: theme('zIndex.modal'),
          display: 'none',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',

          '&.show': {
            display: 'flex',
          },
        },

        '.modal': {
          backgroundColor: theme('colors.white'),
          borderRadius: '0.75rem',
          boxShadow: theme('boxShadow.2xl'),
          maxWidth: '32rem',
          width: '100%',
          maxHeight: '90vh',
          overflow: 'auto',
        },

        '.modal-header': {
          padding: '1.5rem 1.5rem 0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        },

        '.modal-title': {
          fontSize: '1.125rem',
          fontWeight: '600',
          color: theme('colors.gray.900'),
        },

        '.modal-close': {
          padding: '0.5rem',
          backgroundColor: 'transparent',
          border: 'none',
          borderRadius: '0.375rem',
          color: theme('colors.gray.400'),
          cursor: 'pointer',

          '&:hover': {
            color: theme('colors.gray.600'),
            backgroundColor: theme('colors.gray.100'),
          },
        },
      });
    },

    // Plugin para navegação
    function ({ addComponents, theme }) {
      addComponents({
        '.nav-link': {
          display: 'block',
          padding: '0.5rem 1rem',
          color: theme('colors.gray.600'),
          textDecoration: 'none',
          borderRadius: '0.375rem',
          transition: 'all 0.2s ease-in-out',

          '&:hover': {
            color: theme('colors.brand.600'),
            backgroundColor: theme('colors.brand.50'),
          },

          '&.active': {
            color: theme('colors.brand.600'),
            backgroundColor: theme('colors.brand.100'),
            fontWeight: '500',
          },
        },
      });
    },

    // Plugin para ícones
    function ({ addComponents, theme }) {
      addComponents({
        '.icon': {
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: '0',
        },

        '.icon-sm': {
          width: '1rem',
          height: '1rem',
        },

        '.icon-md': {
          width: '1.25rem',
          height: '1.25rem',
        },

        '.icon-lg': {
          width: '1.5rem',
          height: '1.5rem',
        },

        '.icon-xl': {
          width: '2rem',
          height: '2rem',
        },
      });
    },

    // Plugin para utilitários
    function ({ addUtilities }) {
      addUtilities({
        '.flex-center': {
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        },

        '.text-gradient': {
          background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },

        '.line-clamp-2': {
          display: '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          overflow: 'hidden',
        },
      });
    },
  ],

  // Classes sempre incluídas
  safelist: [
    // Botões
    'btn',
    'btn-primary',
    'btn-secondary',
    'btn-success',
    'btn-danger',
    'btn-ghost',
    'btn-sm',
    'btn-lg',
    'btn-icon',

    // Cards
    'card',
    'card-hover',
    'card-header',
    'card-body',
    'card-footer',

    // Formulários
    'form-group',
    'form-label',
    'form-input',
    'form-select',

    // Badges
    'badge',
    'badge-primary',
    'badge-secondary',
    'badge-success',
    'badge-danger',
    'badge-warning',
    'badge-info',
    'badge-outline',

    // Progresso
    'progress',
    'progress-bar',

    // Modal
    'modal-overlay',
    'modal',
    'modal-header',
    'modal-title',
    'modal-close',

    // Navegação
    'nav-link',

    // Ícones
    'icon',
    'icon-sm',
    'icon-md',
    'icon-lg',
    'icon-xl',

    // Utilitários
    'flex-center',
    'text-gradient',
    'line-clamp-2',

    // Animações
    'animate-fade-in',
    'animate-fade-in-up',
    'animate-slide-up',
    'animate-bounce-soft',

    // Estados hover
    'hover:scale-105',
    'hover:shadow-lg',
    'hover:transform',
    'hover:-translate-y-1',

    // Cores da marca
    'bg-brand-50',
    'bg-brand-100',
    'bg-brand-500',
    'bg-brand-600',
    'text-brand-500',
    'text-brand-600',
    'text-brand-700',
    'border-brand-200',
    'border-brand-300',

    // Gradientes
    'bg-gradient-brand',
    'bg-gradient-success',
    'bg-gradient-danger',

    // Grid responsivo
    'grid-cols-1',
    'sm:grid-cols-2',
    'md:grid-cols-2',
    'lg:grid-cols-3',
    'xl:grid-cols-4',

    // Estados de cores
    'bg-success-50',
    'bg-success-100',
    'bg-success-500',
    'text-success-600',
    'text-success-700',
    'text-success-800',
    'border-success-200',
    'border-success-300',

    'bg-danger-50',
    'bg-danger-100',
    'bg-danger-500',
    'text-danger-600',
    'text-danger-700',
    'text-danger-800',
    'border-danger-200',
    'border-danger-300',

    'bg-warning-50',
    'bg-warning-100',
    'bg-warning-500',
    'text-warning-600',
    'text-warning-700',
    'text-warning-800',
    'border-warning-200',
    'border-warning-300',

    'bg-info-50',
    'bg-info-100',
    'bg-info-500',
    'text-info-600',
    'text-info-700',
    'text-info-800',
    'border-info-200',
    'border-info-300',
  ],
};

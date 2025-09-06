/**
 * Tailwind CSS Configuration - Lopes Peinture
 *
 * Configuração personalizada para o sistema de serviços de pintura
 * com cores oficiais da marca, fontes otimizadas e componentes customizados.
 */

module.exports = {
  content: [
    /**
     * HTML Templates - Paths to Django template files containing Tailwind CSS classes
     */

    // Templates within theme app
    '../templates/**/*.html',

    // Main templates directory of the project (BASE_DIR/templates)
    '../../templates/**/*.html',

    // Templates in other django apps (BASE_DIR/<any_app_name>/templates)
    '../../**/templates/**/*.html',

    // Account templates
    '../../accounts/templates/**/*.html',

    // Projects templates
    '../../projects/templates/**/*.html',

    // Profiles templates
    '../../profiles/templates/**/*.html',

    // Pages templates
    '../../pages/templates/**/*.html',

    /**
     * JavaScript files - Process JS files that might contain Tailwind classes
     */
    '../../**/*.js',
    '../../static/js/**/*.js',
    '../../theme/static/js/**/*.js',

    // Exclude node_modules
    '!../../**/node_modules',

    /**
     * Python files - Django views, forms, and components with Tailwind classes
     */
    '../../**/*.py',

    /**
     * Additional file types
     */
    '../../**/*.vue',
    '../../**/*.jsx',
    '../../**/*.tsx',
  ],

  darkMode: 'class', // Enable dark mode support

  theme: {
    extend: {
      /**
       * Typography - Open Sans + Nunito configuration
       */
      fontFamily: {
        sans: [
          'Open Sans',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif',
        ],
        display: [
          'Nunito',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif',
        ],
        body: ['Open Sans', 'system-ui', 'sans-serif'],
        heading: ['Nunito', 'system-ui', 'sans-serif'],
      },

      /**
       * Brand Colors - Lopes Peinture Official Palette
       */
      colors: {
        // Main brand colors (from site gradient)
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          primary: 'rgba(30, 58, 138, 0.9)', // Primary brand color
          secondary: 'rgba(55, 48, 163, 0.9)', // Secondary brand color
          tertiary: 'rgba(88, 28, 135, 0.9)', // Tertiary brand color
          light: '#f8fafc', // Light background
          dark: '#1e293b', // Dark text/backgrounds
        },

        // Semantic colors
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

        // Neutral grays
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
        },
      },

      /**
       * Typography Scale - Responsive and accessible
       */
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem', letterSpacing: '0.025em' }],
        sm: ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '0.025em' }],
        base: ['1rem', { lineHeight: '1.5rem', letterSpacing: '0' }],
        lg: ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '0' }],
        xl: ['1.25rem', { lineHeight: '1.75rem', letterSpacing: '-0.025em' }],
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '-0.025em' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '-0.025em' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem', letterSpacing: '-0.025em' }],
        '5xl': ['3rem', { lineHeight: '1.2', letterSpacing: '-0.025em' }],
        '6xl': ['3.75rem', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
        '7xl': ['4.5rem', { lineHeight: '1.1', letterSpacing: '-0.025em' }],
        '8xl': ['6rem', { lineHeight: '1', letterSpacing: '-0.025em' }],
        '9xl': ['8rem', { lineHeight: '1', letterSpacing: '-0.025em' }],
      },

      /**
       * Font Weights
       */
      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
        extrabold: '800',
        black: '900',
      },

      /**
       * Spacing Scale - Consistent spacing system
       */
      spacing: {
        18: '4.5rem',
        72: '18rem',
        80: '20rem',
        88: '22rem',
        96: '24rem',
        104: '26rem',
        112: '28rem',
        120: '30rem',
        128: '32rem',
      },

      /**
       * Border Radius - Rounded corners
       */
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        DEFAULT: '0.25rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        full: '9999px',
      },

      /**
       * Box Shadows - Elevation system
       */
      boxShadow: {
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        DEFAULT: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
        brand: '0 4px 20px rgba(30, 58, 138, 0.3)', // CORRIGIDO - usar cor primary
        'brand-lg': '0 10px 30px rgba(30, 58, 138, 0.2)', // CORRIGIDO - usar cor primary
        success: '0 4px 20px rgba(34, 197, 94, 0.3)',
        danger: '0 4px 20px rgba(239, 68, 68, 0.3)',
        none: 'none',
      },

      /**
       * Animations - Smooth and professional
       */
      animation: {
        // Float effect for logos and icons
        float: 'float 6s ease-in-out infinite',
        'float-slow': 'float 8s ease-in-out infinite',

        // Fade animations
        'fade-in': 'fadeIn 0.8s ease-out forwards',
        'fade-in-slow': 'fadeIn 1.2s ease-out forwards',
        'fade-out': 'fadeOut 0.5s ease-in forwards',

        // Slide animations
        'slide-up': 'slideUp 0.6s ease-out forwards',
        'slide-down': 'slideDown 0.6s ease-out forwards',
        'slide-left': 'slideLeft 0.6s ease-out forwards',
        'slide-right': 'slideRight 0.8s ease-out forwards',

        // Scale animations
        'scale-in': 'scaleIn 0.5s ease-out forwards',
        'scale-out': 'scaleOut 0.3s ease-in forwards',

        // Pulse and bounce
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',

        // Rotation
        'spin-slow': 'spin 3s linear infinite',

        // Custom business animations
        'paint-drip': 'paintDrip 2s ease-in-out infinite',
        'brush-stroke': 'brushStroke 1.5s ease-out forwards',
      },

      /**
       * Keyframes for custom animations
       */
      keyframes: {
        float: {
          '0%, 100%': {
            transform: 'translateY(0px) rotate(0deg)',
            opacity: '1',
          },
          '25%': {
            transform: 'translateY(-10px) rotate(2deg)',
            opacity: '0.9',
          },
          '50%': {
            transform: 'translateY(-5px) rotate(-1deg)',
            opacity: '1',
          },
          '75%': {
            transform: 'translateY(-15px) rotate(3deg)',
            opacity: '0.95',
          },
        },

        fadeIn: {
          '0%': {
            opacity: '0',
            transform: 'translateY(20px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },

        fadeOut: {
          '0%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
          '100%': {
            opacity: '0',
            transform: 'translateY(-20px)',
          },
        },

        slideUp: {
          '0%': {
            opacity: '0',
            transform: 'translateY(30px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },

        slideDown: {
          '0%': {
            opacity: '0',
            transform: 'translateY(-30px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)',
          },
        },

        slideLeft: {
          '0%': {
            opacity: '0',
            transform: 'translateX(30px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },

        slideRight: {
          '0%': {
            opacity: '0',
            transform: 'translateX(-30px)',
          },
          '100%': {
            opacity: '1',
            transform: 'translateX(0)',
          },
        },

        scaleIn: {
          '0%': {
            opacity: '0',
            transform: 'scale(0.9)',
          },
          '100%': {
            opacity: '1',
            transform: 'scale(1)',
          },
        },

        scaleOut: {
          '0%': {
            opacity: '1',
            transform: 'scale(1)',
          },
          '100%': {
            opacity: '0',
            transform: 'scale(0.9)',
          },
        },

        paintDrip: {
          '0%, 100%': {
            transform: 'translateY(0px) scaleY(1)',
            opacity: '0.8',
          },
          '50%': {
            transform: 'translateY(10px) scaleY(1.1)',
            opacity: '1',
          },
        },

        brushStroke: {
          '0%': {
            strokeDasharray: '0 1000',
            opacity: '0',
          },
          '50%': {
            opacity: '1',
          },
          '100%': {
            strokeDasharray: '1000 0',
            opacity: '1',
          },
        },
      },

      /**
       * Animation Delays - Staggered animations
       */
      animationDelay: {
        0: '0ms',
        75: '75ms',
        100: '100ms',
        150: '150ms',
        200: '200ms',
        300: '300ms',
        400: '400ms',
        500: '500ms',
        600: '600ms',
        700: '700ms',
        800: '800ms',
        900: '900ms',
        1000: '1000ms',
      },

      /**
       * Backdrop Blur - Glass morphism effects
       */
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '40px',
        '3xl': '64px',
      },

      /**
       * Gradients - Custom gradient stops
       */
      backgroundImage: {
        'gradient-brand':
          'linear-gradient(135deg, rgba(30, 58, 138, 0.9) 0%, rgba(55, 48, 163, 0.9) 50%, rgba(88, 28, 135, 0.9) 100%)',
        'gradient-brand-reverse':
          'linear-gradient(135deg, rgba(88, 28, 135, 0.9) 0%, rgba(55, 48, 163, 0.9) 50%, rgba(30, 58, 138, 0.9) 100%)',
        'gradient-overlay':
          'linear-gradient(135deg, rgba(30, 58, 138, 0.8) 0%, rgba(55, 48, 163, 0.7) 100%)',
        'gradient-success': 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        'gradient-danger': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        'gradient-warning': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
      },

      /**
       * Z-Index Scale - Layering system
       */
      zIndex: {
        0: '0',
        10: '10',
        20: '20',
        30: '30',
        40: '40',
        50: '50',
        auto: 'auto',
        dropdown: '1000',
        sticky: '1020',
        fixed: '1030',
        'modal-backdrop': '1040',
        modal: '1050',
        popover: '1060',
        tooltip: '1070',
        toast: '1080',
        navbar: '1090',
      },

      /**
       * Screen Breakpoints - Responsive design
       */
      screens: {
        xs: '475px',
        sm: '640px',
        md: '768px',
        lg: '1024px',
        xl: '1280px',
        '2xl': '1536px',
        '3xl': '1920px',
        // Max-width breakpoints
        'max-xs': { max: '474px' },
        'max-sm': { max: '639px' },
        'max-md': { max: '767px' },
        'max-lg': { max: '1023px' },
        'max-xl': { max: '1279px' },
        'max-2xl': { max: '1535px' },
      },
    },
  },

  /**
   * Plugins - Extended functionality
   */
  plugins: [
    // Forms plugin for better form styling
    require('@tailwindcss/forms')({
      strategy: 'class', // Use class strategy for better control
    }),

    // Typography plugin for prose content
    require('@tailwindcss/typography'),

    // Aspect ratio utilities
    require('@tailwindcss/aspect-ratio'),

    // Custom utilities plugin
    function ({ addUtilities, addComponents, theme }) {
      // Add custom utilities
      addUtilities({
        // Animation delay utilities
        '.animate-delay-75': { 'animation-delay': '75ms' },
        '.animate-delay-100': { 'animation-delay': '100ms' },
        '.animate-delay-150': { 'animation-delay': '150ms' },
        '.animate-delay-200': { 'animation-delay': '200ms' },
        '.animate-delay-300': { 'animation-delay': '300ms' },
        '.animate-delay-400': { 'animation-delay': '400ms' },
        '.animate-delay-500': { 'animation-delay': '500ms' },
        '.animate-delay-600': { 'animation-delay': '600ms' },
        '.animate-delay-700': { 'animation-delay': '700ms' },
        '.animate-delay-800': { 'animation-delay': '800ms' },
        '.animate-delay-900': { 'animation-delay': '900ms' },
        '.animate-delay-1000': { 'animation-delay': '1000ms' },

        // Text shadow utilities
        '.text-shadow-sm': { 'text-shadow': '1px 1px 2px rgba(0, 0, 0, 0.1)' },
        '.text-shadow': { 'text-shadow': '2px 2px 4px rgba(0, 0, 0, 0.1)' },
        '.text-shadow-lg': { 'text-shadow': '4px 4px 8px rgba(0, 0, 0, 0.15)' },
        '.text-shadow-none': { 'text-shadow': 'none' },

        // Glass morphism utilities
        '.glass': {
          background: 'rgba(255, 255, 255, 0.25)',
          'backdrop-filter': 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.18)',
        },
        '.glass-dark': {
          background: 'rgba(0, 0, 0, 0.25)',
          'backdrop-filter': 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
      });

      // Add custom components
      addComponents({
        // Button components
        '.btn-primary': {
          background:
            'linear-gradient(135deg, rgba(30, 58, 138, 0.9) 0%, rgba(55, 48, 163, 0.9) 50%, rgba(88, 28, 135, 0.9) 100%)',
          color: theme('colors.white'),
          'box-shadow': theme('boxShadow.brand'),
          '&:hover': {
            background:
              'linear-gradient(135deg, rgba(88, 28, 135, 0.9) 0%, rgba(55, 48, 163, 0.9) 50%, rgba(30, 58, 138, 0.9) 100%)',
            transform: 'translateY(-2px)',
            'box-shadow': theme('boxShadow.brand-lg'),
          },
          '&:active': {
            transform: 'translateY(0)',
          },
          '&:disabled': {
            opacity: '0.5',
            cursor: 'not-allowed',
            transform: 'none',
          },
        },
        '.btn-secondary': {
          background: theme('colors.neutral.100'),
          color: theme('colors.neutral.900'),
          border: `1px solid ${theme('colors.neutral.300')}`,
          '&:hover': {
            background: theme('colors.neutral.200'),
            transform: 'translateY(-1px)',
          },
        },

        // Form components
        '.form-input': {
          width: '100%',
          padding: '0.75rem 1rem',
          border: `2px solid ${theme('colors.neutral.300')}`,
          'border-radius': theme('borderRadius.lg'),
          background: theme('colors.white'),
          transition: 'all 0.2s ease-in-out',
          'font-family': theme('fontFamily.sans'),
          '&:focus': {
            outline: 'none',
            'border-color': 'rgba(55, 48, 163, 0.9)', // CORRIGIDO - usar secondary color
            ring: '4px',
            'ring-color': 'rgba(55, 48, 163, 0.1)', // CORRIGIDO - usar secondary color
          },
          '&::placeholder': {
            color: theme('colors.neutral.500'),
          },
          '&.error': {
            'border-color': theme('colors.danger.500'),
            '&:focus': {
              'border-color': theme('colors.danger.500'),
              'ring-color': 'rgba(239, 68, 68, 0.1)',
            },
          },
        },

        // Card components
        '.card': {
          background: theme('colors.white'),
          'border-radius': theme('borderRadius.xl'),
          'box-shadow': theme('boxShadow.lg'),
          overflow: 'hidden',
        },
        '.card-header': {
          padding: '1.5rem',
          'border-bottom': `1px solid ${theme('colors.neutral.200')}`,
        },
        '.card-body': {
          padding: '1.5rem',
        },
        '.card-footer': {
          padding: '1.5rem',
          'border-top': `1px solid ${theme('colors.neutral.200')}`,
          background: theme('colors.neutral.50'),
        },
      });
    },
  ],

  /**
   * Safelist - Always include these classes in the build
   */
  safelist: [
    // Animation classes
    'animate-float',
    'animate-fade-in',
    'animate-slide-up',
    'animate-slide-right',
    'animate-pulse-slow',

    // Delay classes
    'animate-delay-200',
    'animate-delay-400',
    'animate-delay-600',
    'animate-delay-800',
    'animate-delay-1000',

    // Brand colors
    'text-brand-primary',
    'text-brand-secondary',
    'text-brand-tertiary',
    'bg-brand-primary',
    'bg-brand-secondary',
    'bg-brand-tertiary',

    // Semantic colors
    'text-success',
    'text-danger',
    'text-warning',
    'bg-success',
    'bg-danger',
    'bg-warning',

    // Form states
    'border-red-500',
    'border-green-500',
    'border-brand-secondary',
    'ring-blue-100',
    'ring-red-100',
    'ring-green-100',
  ],
};

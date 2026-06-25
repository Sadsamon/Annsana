/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // --- Annsana Design Tokens (TSD Section 9.1) ---
        earth: {
          900: '#2C1810',
          700: '#5C3D2E',
          400: '#A0785A',
          100: '#F5EDE4',
        },
        terracotta: {
          DEFAULT: '#C0693B',
          light: '#D4845E',
        },
        sage: {
          DEFAULT: '#6B7C5E',
          light: '#8A9E7A',
        },
        parchment: {
          DEFAULT: '#F8F2E8',
          dark: '#EDE4D3',
        },
        ink: {
          DEFAULT: '#1A1A2E',
          soft: '#4A4A6A',
        },
      },
      fontFamily: {
        display: ['"Playfair Display"', 'serif'],
        body: ['"Inter"', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

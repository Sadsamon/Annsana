/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // ── Core palette — "Griot" design system ────────────────
        // Every value is warm-brown based. No purple. No blue. No cold.
        'earth': {
          900: '#1C0D08',  // Inkwood  — deep, like aged ironwood
          700: '#5C2E12',  // Mahogany — rich warm brown
          400: '#9C6440',  // Sienna   — secondary text, borders
          100: '#F0E4D4',  // Linen    — card backgrounds
        },
        'terracotta': {
          DEFAULT:  '#C4582A',  // Clay oxide — primary CTA
          light:    '#E07845',  // Hover/active
          dark:     '#8B3E15',  // Pressed
        },
        'sage': {
          DEFAULT:  '#4A7228',  // Grove — verified/trust indicator
          light:    '#6A9A40',  // Hover
          muted:    '#F0F4E8',  // Background tint for badges
        },
        'kente': {
          DEFAULT:  '#B8860B',  // Muted gold — Griot status
          light:    '#D4A517',  // Hover
          muted:    '#FEF3CD',  // Background tint for Griot badges
        },
        'parchment': {
          DEFAULT:  '#FAF5ED',  // Page background — warm off-white
          dark:     '#F0E4D4',  // Slightly deeper — used on hover states
        },
        'ink': {
          DEFAULT:  '#2C1810',  // Primary text — warm dark brown (NOT purple)
          soft:     '#6B4030',  // Secondary text — muted warm brown
          faint:    '#9C7060',  // Placeholder, timestamps
        },
      },
      fontFamily: {
        'display': ['"Playfair Display"', 'Georgia', 'serif'],
        'body':    ['"Inter"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'xl':  '12px',
        '2xl': '16px',
        '3xl': '20px',
      },
      boxShadow: {
        'warm': '0 1px 3px rgba(28,13,8,0.08), 0 4px 12px rgba(28,13,8,0.06)',
        'warm-md': '0 4px 16px rgba(28,13,8,0.10), 0 1px 4px rgba(28,13,8,0.06)',
      },
    },
  },
  plugins: [],
};

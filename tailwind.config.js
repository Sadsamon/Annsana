/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        terracotta: {
          50: "var(--color-terracotta-50)",
          100: "var(--color-terracotta-100)",
          500: "var(--color-terracotta-500)",
          700: "var(--color-terracotta-700)",
        },
        indigo: {
          50: "var(--color-indigo-50)",
          100: "var(--color-indigo-100)",
          500: "var(--color-indigo-500)",
          700: "var(--color-indigo-700)",
        },
        gold: {
          50: "var(--color-gold-50)",
          100: "var(--color-gold-100)",
          500: "var(--color-gold-500)",
          700: "var(--color-gold-700)",
        },
        savanna: {
          50: "var(--color-savanna-50)",
          100: "var(--color-savanna-100)",
          500: "var(--color-savanna-500)",
          700: "var(--color-savanna-700)",
        },
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
    },
  },
  plugins: [],
};

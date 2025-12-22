/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#ebf0ff',
          200: '#d6e0ff',
          300: '#b3c5ff',
          400: '#85a0ff',
          500: '#5c7aff',
          600: '#3d54ff',
          700: '#2e3eff',
          800: '#2532d1',
          900: '#242ea6',
          950: '#161a61',
        },
      },
    },
  },
  plugins: [],
}

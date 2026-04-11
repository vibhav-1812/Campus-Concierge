/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'vt-orange': '#CF4520',
        'vt-maroon': '#630031',
      }
    },
  },
  plugins: [],
}

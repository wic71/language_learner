/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './**/*.js',
    './**/*.py'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
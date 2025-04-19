/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#1976D2', // primary color
          600: '#0c5cad',
          700: '#064388',
          800: '#022a63',
          900: '#01173f',
        },
        toronto: {
          red: '#EE3337',
          blue: '#003DA6',
          gray: '#565A5C',
        }
      },
    },
  },
  plugins: [],
}
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.tsx'],
  theme: {
    spacing: {
      0: '0px',
      0.5: '2px',
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      6: '24px',
      8: '32px',
      12: '48px',
    },
    extend: {
      colors: {
        ink: '#12232e',
        sea: '#1f6f8b',
        shell: '#f2f6f7',
        alert: '#a3321f',
      },
    },
  },
}

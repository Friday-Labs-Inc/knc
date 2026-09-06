/** @type {import('tailwindcss').Config} */
// Design tokens transcribed from the Draft. brand guidelines (docs: "KNC (2).md").
// Dark, minimal, editorial: one true-black canvas, a gray ramp, zero accent colour.
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0A0A', // true black — the page canvas
        surface: { 1: '#111111', 2: '#181818' }, // cards / lifted inputs
        line: { DEFAULT: '#242424', hover: '#383838' }, // borders + dividers
        ink: {
          DEFAULT: '#FFFFFF', // headlines, active text
          soft: '#C0C0C0', // body copy (never pure white — too harsh)
          muted: '#707070', // labels, captions, placeholders, meta
          faint: '#404040', // disabled, very secondary
        },
        input: { bg: '#141414', border: '#2E2E2E', focus: '#505050' },
      },
      fontFamily: {
        // Söhne is the licensed original; Inter is the free fallback we ship.
        sans: ['Inter', 'ui-sans-serif', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      maxWidth: { page: '1120px', narrow: '680px' },
      borderRadius: { card: '12px', input: '16px', pill: '999px', tag: '6px' },
      letterSpacing: {
        hero: '-0.035em', // big hero type runs tight — this separates premium from generic
        head: '-0.025em', // section headlines
        tightish: '-0.015em', // card titles
      },
    },
  },
  plugins: [],
}

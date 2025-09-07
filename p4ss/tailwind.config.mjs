import typography from '@tailwindcss/typography'
import daisyui from 'daisyui'

/** @type {import('tailwindcss').Config} */
export default {
  important: false,
  content: ['./src/**/*.{vue,js,ts,jsx,tsx}'],
  plugins: [typography, daisyui],
  daisyui: {
    styled: true,
    themes: false,
    base: true,
    utils: true,
    logs: true,
    darkTheme: 'dark',
    prefix: '',
    themeRoot: ':root'
  }
}

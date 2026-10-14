/** @type {import('tailwindcss').Config} */
// Tokens per CLONE_SPEC.md §1.2 and §1.6.
// CommonJS on purpose: with "type":"module" on Node >=20.19, Tailwind 3 loads an
// ESM tailwind.config.js via require(esm), which it cannot invalidate, so the
// running dev server never sees config edits. A .cjs config reloads correctly.
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  // v4 wraps `hover:` in @media (hover:hover); match that.
  future: { hoverOnlyWhenSupported: true },
  theme: {
    extend: {
      colors: {
        text: { DEFAULT: '#1a1a18', muted: '#76766e', faint: '#a5a59c' },
        surface: { DEFAULT: '#f2f1ed', raised: '#fcfcfb', sunken: '#e9e8e3' },
        border: { DEFAULT: '#e1e0da', strong: '#c6c4bd' },
        accent: '#9ee86f',
        source: { linkedin: '#2d64bc', instagram: '#d6336c', x: '#1a1a18', note: '#76766e' },
        // "Other literal colours in use" (§1.2), named for use as tokens.
        swatch: {
          web: '#3fbf4a',
          ink: '#1c1c1a',
          mist: '#dfe4ee',
          sand: '#e2ded4',
          steel: '#e4e8f2',
          lilac: '#e6e2ec',
          sky: '#e8effa',
          linen: '#eae7df',
          peach: '#efe3d6',
        },
        // Fills baked into the tag SVG assets (MANIFEST.md).
        brand: { instagram: '#FF0069', youtube: '#FF0000', figma: '#F24E1E', x: '#000000' },
      },
      fontFamily: {
        sans: ['"Switzer"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        body: ['"Switzer"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"General Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      spacing: { 13: '3.25rem' },
      // v4 `transition` / `transition-colors` property lists (measured on the original).
      transitionProperty: {
        DEFAULT:
          'color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to, opacity, box-shadow, transform, translate, scale, rotate, filter, -webkit-backdrop-filter, backdrop-filter, display, content-visibility, overlay, pointer-events',
        colors:
          'color, background-color, border-color, outline-color, text-decoration-color, fill, stroke, --tw-gradient-from, --tw-gradient-via, --tw-gradient-to',
      },
      boxShadow: {
        palette: '0 18px 50px -24px rgba(26,26,24,0.22)',
      },
    },
  },
  plugins: [],
}

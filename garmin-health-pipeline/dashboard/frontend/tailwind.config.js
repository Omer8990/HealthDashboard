/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'cyber-pink': '#ff006e',
        'cyber-cyan': '#00f5ff',
        'cyber-purple': '#8b00ff',
        'neon-green': '#39ff14',
        'matrix-bg': '#0d1117',
        'matrix-surface': '#161b22',
        'matrix-border': '#30363d',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Monaco', 'Consolas', 'monospace'],
        'cyber': ['Orbitron', 'Exo 2', 'Rajdhani', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'matrix-rain': 'matrix-rain 3s linear infinite',
        'scan-line': 'scan-line 2s linear infinite',
        'flicker': 'flicker 0.15s infinite linear',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #00f5ff' },
          '100%': { boxShadow: '0 0 20px #00f5ff, 0 0 30px #00f5ff' },
        },
        'matrix-rain': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
        'scan-line': {
          '0%': { top: '0%' },
          '100%': { top: '100%' },
        },
        flicker: {
          '0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100%': { opacity: '0.99' },
          '20%, 21.999%, 63%, 63.999%, 65%, 69.999%': { opacity: '0.4' },
        },
      },
      backgroundImage: {
        'cyber-grid': 'linear-gradient(rgba(0,245,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,245,255,0.3) 1px, transparent 1px)',
      },
      backgroundSize: {
        'grid': '20px 20px',
      },
    },
  },
  plugins: [],
}
module.exports = {
  content: ['./app/**/*.{js,jsx}'],
  theme: {
    extend: {
      keyframes: {
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      animation: {
        'bounce-dot': 'bounce 0.8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

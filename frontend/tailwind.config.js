/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        serif: ['"Times New Roman"', "Times", "Georgia", "serif"],
      },
      colors: {
        cream: {
          50: "#FCFBF8",
          100: "#F6F3EC",
          200: "#EDE7DA",
          300: "#DDD4C2",
        },
        navy: {
          50: "#EEF1F5",
          100: "#D4DCE6",
          200: "#A7B7CB",
          300: "#7B93B0",
          400: "#526E92",
          500: "#35507A",
          600: "#273D5E",
          700: "#1C2E48",
          800: "#132135",
          900: "#0B1523",
        },
        steel: {
          100: "#EAECEE",
          200: "#CBD1D6",
          300: "#9BA5AE",
          400: "#6B7883",
        },
      },
      boxShadow: {
        card: "0 1px 2px rgba(11, 21, 35, 0.04), 0 6px 24px rgba(11, 21, 35, 0.05)",
      },
      letterSpacing: {
        eyebrow: "0.18em",
      },
    },
  },
  plugins: [],
};

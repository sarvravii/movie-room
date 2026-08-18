/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#121216",
          surface: "#1b1b21",
          raised: "#232329",
          border: "#2c2c34",
        },
        accent: {
          DEFAULT: "#6c5ce7",
          hover: "#7d6ff0",
          active: "#5b4bd6",
          subtle: "rgba(108, 92, 231, 0.14)",
        },
        ink: {
          DEFAULT: "#f5f5f7",
          secondary: "#a5a5b0",
          muted: "#6f6f7a",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "sans-serif",
        ],
      },
      borderRadius: {
        xl2: "1.25rem",
      },
      boxShadow: {
        panel: "0 8px 30px -12px rgba(0, 0, 0, 0.45)",
      },
    },
  },
  plugins: [],
}


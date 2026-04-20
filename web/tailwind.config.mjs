import typography from "@tailwindcss/typography";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#FAF5F0",
        ink: "#0F0F0F",
        terracotta: "#8B5A4A",
        coral: "#C94E3C",
        sand: "#D4C5B8",
        plum: "#4A2C3A",
        rose: "#C7A5A5",
      },
      fontFamily: {
        serif: ['"Fraunces"', "Georgia", "serif"],
        sans: ['"Inter"', "system-ui", "sans-serif"],
      },
      fontSize: {
        display: ["clamp(2.5rem, 6vw, 5.5rem)", { lineHeight: "0.95", letterSpacing: "-0.02em" }],
        hero: ["clamp(1.75rem, 3.5vw, 3rem)", { lineHeight: "1.05", letterSpacing: "-0.01em" }],
      },
      maxWidth: {
        reading: "68ch",
      },
      spacing: {
        section: "clamp(3rem, 8vw, 6rem)",
      },
    },
  },
  plugins: [typography],
};

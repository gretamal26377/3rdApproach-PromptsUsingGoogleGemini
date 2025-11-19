import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { fileURLToPath } from "url";

// ESM-compatible __dirname
const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => ({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      // Always import from 'shared-lib'
      "shared-lib":
        mode === "development"
          ? path.resolve(__dirname, "../shared-lib/src")
          : path.resolve(__dirname, "../shared-lib/dist"),
    },
  },
}));

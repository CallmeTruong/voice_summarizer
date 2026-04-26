import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath } from "node:url";

const envDir = fileURLToPath(new URL("../..", import.meta.url));

export default defineConfig({
  envDir,
  plugins: [react(), tailwindcss()],
});

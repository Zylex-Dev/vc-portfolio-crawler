import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Relative base so the static bundle works from any GitHub Pages subpath
// (https://user.github.io/<repo>/) without hardcoding the repo name.
export default defineConfig({
  base: "./",
  plugins: [react()],
  build: {
    outDir: "dist",
    assetsInlineLimit: 0,
  },
});

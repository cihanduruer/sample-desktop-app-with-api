import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The production build is emitted into the ASP.NET Core app's wwwroot so the BFF
// can serve the SPA. In dev we run on 5173 and call the BFF directly on 5080
// (which has CORS wide open - see docs/ for why that's a planted problem).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    outDir: "../wwwroot",
    emptyOutDir: true,
  },
});

import { defineConfig } from 'vite'
import react from "@vitejs/plugin-react";

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:5000',
        changeOrigin: true
      }
    }
  },
  plugins: [react()],
  optimizeDeps: {
    include: ["@mui/material", "@mui/system", "@mui/icons-material"],
  },
  build: {
    target: "esnext",
    minify: false,
    chunkSizeWarningLimit: 1000,
    commonjsOptions: {
      transformMixedEsModules: true, // Fix CommonJS issues
    },
  },
});

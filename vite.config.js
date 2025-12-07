import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from "@tailwindcss/vite"

export default defineConfig({
  root: 'assets',
  base: '/static/',
    plugins: [tailwindcss()],
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'assets/main.js')
      }
    }
  },
  server: {
    origin: 'http://localhost:5173'
  }
});
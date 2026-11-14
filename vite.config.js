import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  root: 'assets',
  base: '/static/dist/',
  plugins: [tailwindcss()],
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    manifest: true,
    rolldownOptions: {
      input: {
        main: resolve(import.meta.dirname, 'assets/main.js')
      }
    }
  }
});

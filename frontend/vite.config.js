import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/simulation': 'http://127.0.0.1:8000',
      '/agents': 'http://127.0.0.1:8000',
      '/optimize': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
      '/analytics': 'http://127.0.0.1:8000',
      '/monitoring': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
});

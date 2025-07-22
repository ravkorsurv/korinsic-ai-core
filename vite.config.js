import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Using non-standard port to avoid conflicts with common dev servers
const VITE_DEV_SERVER_PORT = 5174;

export default defineConfig({
  plugins: [react()],
  server: {
    port: VITE_DEV_SERVER_PORT,
  },
}); 
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// En desarrollo, el front llama a /api/... y Vite lo reenvía al backend. Así el navegador siempre habla con un único
// origen y no hay problemas de CORS. En Docker lo hace nginx (ver docker/)
const BACKEND = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: BACKEND,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
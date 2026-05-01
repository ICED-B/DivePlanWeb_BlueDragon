import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({   
  plugins: [react()],                 // , tailwindcss()
  server: {
    host: '0.0.0.0', // Důležité pro přístup z Dockeru/jiných strojů
    port: 5173,     // Port for Vite dev server
    proxy: {
      // prefix /api přesměrovány na backend
      '/api': {
        // název služby backendu a port v Docker Compose
        target: 'http://backend:8000',
        changeOrigin: true, // for virtual hosting
        secure: false,      // Pokud backend běží na HTTPS s self-signed certifikátem
        rewrite: (path) => path, //.replace(/^\/api/, ''), // Pokud nechcete /api v cílové URL
      }   // how frontend should be build send requests
    }
  }
})

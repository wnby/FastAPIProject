import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',   // 设置为 0.0.0.0 使得服务器在所有网络接口上监听
    port: 5186,         // 可选，指定一个固定端口
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 仍然代理到你的 FastAPI 后端
        changeOrigin: true,
        ws: true
      }
    }
  }
})

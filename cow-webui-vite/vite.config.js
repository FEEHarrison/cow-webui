// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://82.197.95.98:5002', // 确保这是你的后端服务器地址
        changeOrigin: true,
        timeout: 60000, // 设置超时时间为 60 秒
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});

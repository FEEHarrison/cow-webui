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
        target: 'https://wx.aigcboundless.cn', // 确保这是你的后端服务器地址
        changeOrigin: true,
        secure: true, // 添加此项以确保代理到 HTTPS 地址
        timeout: 60000, // 设置超时时间为 60 秒
        rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
  },
});

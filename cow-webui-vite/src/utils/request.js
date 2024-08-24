import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建 Axios 实例
const service = axios.create({
  baseURL: '/api', // 这里可以根据需要修改
  timeout: 20000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 在请求发送之前可以做一些处理，比如添加 token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    config.headers['Content-Type'] = 'application/json'; // 设置请求头为JSON格式
    return config;
  },
  (error) => {
    // 请求错误的处理
    console.error('请求错误：', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;

    // 检查自定义的 code 是否为 200
    if (res.code == 200 && res.success) {
      return res;
    } else {
      // 如果后端返回的 success 为 false，或者 code 不是 200，处理错误
      ElMessage.error(res.message || '请求失败');
      return Promise.reject(new Error(res.message || 'Error'));
    }
  },
  (error) => {
    // 响应错误的处理
    console.error('响应错误：', error);
    if (error.response) {
      // 服务器返回的错误
      const res = error.response.data;
      ElMessage.error(res.message || '请求失败');
    } else if (error.message.includes('timeout')) {
      // 请求超时
      ElMessage.error('请求超时，请稍后再试');
    } else {
      // 其他错误
      ElMessage.error('请求失败，请检查网络或稍后再试');
    }
    return Promise.reject(error);
  }
);

export default service;

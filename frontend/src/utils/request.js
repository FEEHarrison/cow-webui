import axios from 'axios';
import { ElMessage } from 'element-plus';
import { createApp } from 'vue';
import ErrorBoundary from '@/components/ErrorBoundary.vue'; // 假设您已创建此组件

// 创建 Axios 实例
const service = axios.create({
  baseURL: import.meta.env.VITE_BASE_API,
  timeout: 20000,
  withCredentials: true,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    config.headers['Content-Type'] = 'application/json';
    return config;
  },
  (error) => {
    console.error('请求错误：', error);
    return Promise.resolve({ error });
  }
);

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res.code == 200 && res.success) {
      return res;
    } else {
      ElMessage.error(res.message || '请求失败');
      return Promise.resolve({ error: new Error(res.message || 'Error') });
    }
  },
  error => {
    if (error.response && error.response.status === 401) {
      // 未授权，可能是 token 过期或未登录
      router.push('/login')
    }
    return Promise.reject(error)
  }
);

// 封装请求方法
const request = async (method, url, data = {}) => {
  try {
    const response = await service[method](url, method === 'get' ? { params: data } : data);
    return response;
  } catch (error) {
    console.error(`${method.toUpperCase()} 请求失败：`, error);
    return { error };
  }
};

// 封装 GET 请求
export const get = (url, params) => request('get', url, params);

// 封装 POST 请求
export const post = (url, data) => request('post', url, data);

// 封装 PUT 请求
export const put = (url, data) => request('put', url, data);

// 封装 DELETE 请求
export const del = (url) => request('delete', url);

export const login = async (data) => {
  const response = await post('/api/login', data);
  if (!response.error && response.data && response.data.token) {
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('role', response.data.role);
    const userInfo = {
      username: response.data.username,
      role: response.data.role
    };
    localStorage.setItem('user', JSON.stringify(userInfo));
  }
  return response;
};

export const logout = async () => {
  const response = await post('/api/logout');
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('role');
  return response;
};

export const clearUserData = async () => {
  return await post('/api/clear_user_data');
};

export const register = (data) => post('/api/register', data);
export const getUsers = () => get('/api/users');
export const deleteUser = (userId) => del(`/api/delete_user/${userId}`);
export const checkAdminSetup = () => get('/api/check_admin_setup');
export const checkLogin = () => get('/api/check_login');

// 创建错误边界组件
const ErrorBoundaryWrapper = createApp(ErrorBoundary).mount(document.createElement('div'));

// 包装 service 以使用错误边界
const serviceWithErrorBoundary = new Proxy(service, {
  get(target, prop) {
    if (typeof target[prop] === 'function') {
      return new Proxy(target[prop], {
        apply: (fn, thisArg, args) => {
          try {
            return fn.apply(thisArg, args);
          } catch (error) {
            ErrorBoundaryWrapper.captureError(error);
            return Promise.resolve({ error });
          }
        }
      });
    }
    return target[prop];
  }
});

export default serviceWithErrorBoundary;

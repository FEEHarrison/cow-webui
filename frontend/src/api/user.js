import { get, post, put, del } from '@/utils/request';

export const getUsers = () => get('/api/users');
export const addUser = (userData) => post('/api/users', userData);
export const updateUser = (userId, userData) => put(`/api/users/${userId}`, userData);
export const register = (userData) => post('/api/register', userData);
export const deleteUser = (userId) => del(`/api/users/${userId}`);
// 添加 setupAdmin 函数
export const setupAdmin = (password) => post('/api/setup_admin', { password });
export const checkAdminSetup = () => get('/api/check_admin_setup');
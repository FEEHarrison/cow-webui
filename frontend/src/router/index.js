import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Dashboard from '@/views/Dashboard.vue'
import AdminSetup from '@/views/AdminSetup.vue'
import { checkLogin } from '@/utils/request'

const routes = [
  { path: '/', name: 'Root', component: AdminSetup },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  
]


const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE),
  routes
})

router.beforeEach(async (to, from, next) => {
  const publicRoutes = ['/login', '/register', '/'];
  
  if (publicRoutes.includes(to.path)) {
    return next();
  }

  try {
    const response = await checkLogin();
    if (response.success) {
      return next();
    } else {
      return next('/login');
    }
  } catch (error) {
    console.error('检查登录状态失败', error);
    return next('/login');
  }
});


export function logout() {
  // 在这里实现删除登录数据的逻辑
  localStorage.removeItem('token'); // 假设使用 token 进行身份验证
  localStorage.removeItem('user');
  router.push('/login');
}


export default router
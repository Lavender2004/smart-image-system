import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Home from '../views/Home.vue';

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/', name: 'Home', component: Home },
  // 如果以后有 404 页面，可以加在这里
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ==========================================
// 🛡️ 路由守卫配置
// ==========================================

// 定义不需要登录就能访问的“白名单”页面
const whiteList = ['/login', '/register'];

router.beforeEach((to, from, next) => {
  // 获取 token
  const token = localStorage.getItem('token');

  // 1. 如果要去的是“白名单”页面 (登录/注册)
  if (whiteList.includes(to.path)) {
    if (token) {
      // 如果已登录，就不让他去登录页了，直接踢回首页
      next('/'); 
    } else {
      // 没登录，允许访问登录/注册页
      next(); 
    }
  } 
  // 2. 如果要去的是“受保护”页面 (首页、详情页等)
  else {
    if (token) {
      // 有 token，放行
      next(); 
    } else {
      // 没 token，强制重定向到登录页
      next('/login'); 
    }
  }
});

export default router;

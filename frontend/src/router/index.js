import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue'; // 【新增引入】
import Home from '../views/Home.vue';

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register }, // 【新增路由】
  { path: '/', name: 'Home', component: Home },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：没登录不许进主页，但可以去登录和注册
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  // 如果去登录页或注册页，直接放行
  if ((to.path === '/login' || to.path === '/register') && !token) {
    next();
  } 
  // 如果没 Token 且去的不是登录/注册页，强制跳去登录
  else if (!token && to.path !== '/login' && to.path !== '/register') {
    next('/login');
  } 
  else {
    next();
  }
});

export default router;

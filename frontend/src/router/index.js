import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Home from '../views/Home.vue';

const routes = [
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/', name: 'Home', component: Home },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const whiteList = ['/login', '/register'];

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');

  if (whiteList.includes(to.path)) {
    if (token) {
      next('/');
    } else {
      next();
    }
  } else {
    if (token) {
      next();
    } else {
      next('/login');
    }
  }
});

export default router;

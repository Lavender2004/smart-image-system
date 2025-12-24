import axios from 'axios';
import { showNotify } from 'vant';

// 创建 axios 实例
const service = axios.create({
  // ⚠️ 注意：这里一定要换成你自己的虚拟机 IP
  baseURL: 'http://192.168.126.130:8000', 
  timeout: 5000 
});

// 请求拦截器：每次发请求前，自动把 Token 塞进去
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器：如果有报错（比如 401 没权限），统一提示
service.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    const msg = error.response?.data?.detail || '请求失败';
    showNotify({ type: 'danger', message: msg });
    return Promise.reject(error);
  }
);

export default service;

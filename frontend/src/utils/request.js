import axios from 'axios';
// ❌ 1. 注释掉 showNotify，因为我们不想在顶部显示那个红色的报错条
// import { showNotify } from 'vant'; 

// 创建 axios 实例
const service = axios.create({
  // ⚠️ 保持你原来的 IP 配置
  baseURL: 'http://10.193.69.228:8000', 
  timeout: 5000 
});

// 请求拦截器
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

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // ========================================================
    // 🛑 核心修改：移除全局的 showNotify
    // ========================================================
    // 之前的代码会在这里拦截错误并弹窗，导致你看到“双重提示”和“英文报错”。
    // 现在我们把它注释掉，把错误直接抛给 .vue 组件，
    // 让你在组件里写的中文 showFailToast 生效。
    
    /* const msg = error.response?.data?.detail || '请求失败';
    showNotify({ type: 'danger', message: msg }); 
    */

    // ✅ 新增建议：处理 401 Token 过期情况
    // 如果 Token 失效或被后端拒绝，自动清除本地缓存
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // 可选：你也可以在这里强制跳转到登录页，或者由组件自己处理跳转
    }

    return Promise.reject(error);
  }
);

export default service;

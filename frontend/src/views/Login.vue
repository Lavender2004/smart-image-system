<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request'; 
import { showSuccessToast, showFailToast } from 'vant';

const username = ref('');
const password = ref('');
const router = useRouter();

const handleLogin = async () => {
  if (!username.value || !password.value) {
    showFailToast('请输入用户名和密码');
    return;
  }

  try {
    const formData = new FormData();
    formData.append('username', username.value);
    formData.append('password', password.value);

    const res = await request.post('/api/v1/auth/login', formData);
    
    localStorage.setItem('token', res.access_token);
    showSuccessToast('欢迎回来！');
    
    setTimeout(() => {
      router.push('/');
    }, 500);
    
  } catch (error) {
    console.error('Login Error:', error);
    const errorMsg = error.response?.data?.detail || '';
    
    if (error.response?.status === 401 || errorMsg.includes('Incorrect')) {
      showFailToast('用户名或密码错误');
    } else if (error.response?.status === 404) {
      showFailToast('该用户不存在');
    } else {
      showFailToast(errorMsg || '登录服务异常，请稍后重试');
    }
  }
};
</script>

<template>
  <div class="login-container">
    <div class="content-wrapper">
      <h2 class="title">云相册</h2>
      
      <van-cell-group inset>
        <van-field
          v-model="username"
          label="用户名"
          placeholder="请输入用户名"
        />
        <van-field
          v-model="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
        />
      </van-cell-group>
      
      <div class="btn-group">
        <van-button round block type="primary" @click="handleLogin">
          登录
        </van-button>

        <van-button 
          round block type="default" 
          class="text-btn"
          @click="router.push('/register')"
        >
          没有账号？去注册
        </van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-top: 100px;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  max-width: 480px; 
}

.title {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
  font-weight: 600;
}

.btn-group {
  margin: 20px;
}

.text-btn {
  margin-top: 15px;
  border: none;
  background: transparent;
  color: #1989fa;
}
</style>

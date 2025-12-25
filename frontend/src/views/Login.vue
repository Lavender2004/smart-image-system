<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request'; 
import { showSuccessToast } from 'vant';

const username = ref('');
const password = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const formData = new FormData();
    formData.append('username', username.value);
    formData.append('password', password.value);

    const res = await request.post('/api/v1/auth/login', formData);
    
    localStorage.setItem('token', res.access_token);
    showSuccessToast('登录成功');
    router.push('/');
    
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="login-container">
    <h2 class="title">Smart Image System</h2>
    
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
    
    <div style="margin: 20px;">
      <van-button round block type="primary" @click="handleLogin">
        登录
      </van-button>

      <van-button 
        round block type="default" 
        style="margin-top: 15px; border: none; background: transparent; color: #1989fa;" 
        @click="router.push('/register')"
      >
        没有账号？去注册
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  padding-top: 100px;
  background-color: #f7f8fa;
  min-height: 100vh;
}
.title {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
}
</style>

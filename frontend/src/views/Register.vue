<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '../utils/request';
import { showSuccessToast, showFailToast } from 'vant';

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');

// 提交注册
const handleRegister = async () => {
  // 1. 前端基础校验
  if (password.value !== confirmPassword.value) {
    showFailToast('两次输入的密码不一致');
    return;
  }
  if (password.value.length < 6) {
    showFailToast('密码长度不能少于6位');
    return;
  }

  try {
    // 2. 发送请求
    await request.post('/api/v1/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    });
    
    showSuccessToast('注册成功，请登录');
    // 3. 跳转回登录页
    setTimeout(() => {
      router.push('/login');
    }, 1000);
    
  } catch (error) {
    // 错误信息已经在 request.js 拦截器里弹出了，这里不用重复处理
    console.error(error);
  }
};
</script>

<template>
  <div class="register-container">
    <h2 class="title">注册账号</h2>
    
    <van-cell-group inset>
      <van-field
        v-model="username"
        label="用户名"
        placeholder="请输入用户名 (3位以上)"
        :rules="[{ required: true, message: '请填写用户名' }]"
      />
      <van-field
        v-model="email"
        label="邮箱"
        placeholder="请输入邮箱"
        :rules="[{ required: true, message: '请填写邮箱' }]"
      />
      <van-field
        v-model="password"
        type="password"
        label="密码"
        placeholder="设置密码 (6位以上)"
        :rules="[{ required: true, message: '请填写密码' }]"
      />
      <van-field
        v-model="confirmPassword"
        type="password"
        label="确认密码"
        placeholder="请再次输入密码"
        :rules="[{ required: true, message: '请确认密码' }]"
      />
    </van-cell-group>
    
    <div style="margin: 30px 20px;">
      <van-button round block type="primary" @click="handleRegister">
        立即注册
      </van-button>
      <van-button 
        round block type="default" 
        style="margin-top: 10px; border: none; background: transparent;" 
        @click="router.push('/login')"
      >
        已有账号？去登录
      </van-button>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  padding-top: 80px;
  background-color: #f7f8fa;
  min-height: 100vh;
}
.title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}
</style>

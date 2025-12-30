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
    
    // 稍微延迟跳转，让用户看清提示
    setTimeout(() => {
      router.push('/');
    }, 500);
    
  } catch (error) {
    console.error('Login Error:', error);
    // 尝试获取后端返回的具体错误信息
    const errorMsg = error.response?.data?.detail || '';
    
    // 针对常见的后端英文错误进行汉化 (假设后端是 FastAPI/Python)
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
  /* 关键布局：让内部内容水平居中 */
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  /* 限制最大宽度，防止在大屏上无限拉伸 */
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

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

const handleRegister = async () => {
  // ==========================================
  // 1. 前端基础校验
  // ==========================================
  
  // 🔴 新增：检查是否有没填的项
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    showFailToast('请填写完整信息');
    return;
  }

  // 检查两次密码是否一致
  if (password.value !== confirmPassword.value) {
    showFailToast('两次输入的密码不一致');
    return;
  }

  // 检查密码长度
  if (password.value.length < 6) {
    showFailToast('密码长度不能少于6位');
    return;
  }

  try {
    // ==========================================
    // 2. 发送注册请求
    // ==========================================
    await request.post('/api/v1/auth/register', {
      username: username.value,
      email: email.value,
      password: password.value
    });
    
    showSuccessToast('注册成功，正在跳转...');
    
    // 注册成功后延迟跳转回登录页
    setTimeout(() => {
      router.push('/login');
    }, 1500);
    
  } catch (error) {
    console.error('Register Error:', error);
    const errorMsg = error.response?.data?.detail || '';
    const status = error.response?.status;

    // ==========================================
    // 3. 错误处理逻辑优化
    // ==========================================
    
    // 这种情况通常是后端校验失败（比如邮箱格式不对、或者字段缺失）
    if (status === 422) {
         showFailToast('输入格式有误，请检查邮箱格式');
    } 
    // 用户名或邮箱已存在
    else if (errorMsg.includes('exist') || status === 400) {
      showFailToast('该用户名或邮箱已被注册');
    } 
    // 其他未知错误
    else {
      showFailToast('注册服务暂不可用，请检查网络');
    }
  }
};
</script>

<template>
  <div class="register-container">
    <div class="content-wrapper">
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
      
      <div class="btn-group">
        <van-button round block type="primary" @click="handleRegister">
          立即注册
        </van-button>
        <van-button 
          round block type="default" 
          class="text-btn"
          @click="router.push('/login')"
        >
          已有账号？去登录
        </van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-top: 80px;
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
  margin-bottom: 30px;
  color: #333;
  font-weight: 600;
}

.btn-group {
  margin: 30px 20px;
}

.text-btn {
  margin-top: 10px;
  border: none;
  background: transparent;
  color: #666;
}
</style>

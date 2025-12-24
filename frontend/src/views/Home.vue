<script setup>
import { ref, onMounted } from 'vue';
import request from '../utils/request';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();
const images = ref([]);
const searchValue = ref('');

// ⚠️ 重要：这里填你的后端地址，用于凭借图片 URL
// 因为后端返回的是 "static/uploads/..."，前端需要补全 "http://IP:8000/"
const API_BASE_URL = 'http://192.168.126.130:8000'; 

// 获取图片列表 (支持搜索)
const getImages = async () => {
  try {
    const res = await request.get('/api/v1/images', {
      params: { tag: searchValue.value } // 将搜索框的内容传给后端
    });
    images.value = res;
    if (res.length === 0 && searchValue.value) {
      showToast('没有找到相关图片');
    }
  } catch (error) {
    console.error(error);
  }
};

// 搜索事件
const onSearch = () => {
  getImages();
};

// 退出登录
const handleLogout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

// 页面加载时，先拉取一次所有图片
onMounted(() => {
  getImages();
});
</script>

<template>
  <div class="home-container">
    <van-nav-bar 
      title="我的云相册" 
      right-text="退出" 
      @click-right="handleLogout" 
      fixed
      placeholder
    />

    <van-search
      v-model="searchValue"
      placeholder="输入标签搜索 (如: travel)"
      show-action
      @search="onSearch"
    >
      <template #action>
        <div @click="onSearch">搜索</div>
      </template>
    </van-search>

    <van-grid :column-num="2" :gutter="10" style="padding: 10px">
      <van-grid-item v-for="img in images" :key="img.id">
        <van-image
          width="100%"
          height="150"
          fit="cover"
          :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`"
        />
        
        <div class="image-info">
          <div class="tags" v-if="img.tags && img.tags.length > 0">
            <van-tag 
              v-for="tag in img.tags" 
              :key="tag.id" 
              type="primary" 
              plain 
              style="margin-right: 4px"
            >
              {{ tag.name }}
            </van-tag>
          </div>
          <div class="tags" v-else>
            <span style="color: #999; font-size: 10px;">暂无标签</span>
          </div>
          
          <p class="filename">{{ img.filename.split('-')[0] }}...</p>
        </div>
      </van-grid-item>
    </van-grid>

    <van-empty v-if="images.length === 0" description="暂无图片，快去上传吧" />
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 20px;
}
.image-info {
  width: 100%;
  padding: 5px 0;
}
.tags {
  margin-bottom: 5px;
  height: 20px; /* 占位防止跳动 */
  overflow: hidden;
}
.filename {
  margin: 0;
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

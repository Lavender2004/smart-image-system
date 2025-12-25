<script setup>
import { ref, onMounted } from 'vue';
import request from '../utils/request';
import { useRouter } from 'vue-router';
import { showToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant';

const router = useRouter();
const images = ref([]);
const searchValue = ref('');
// ⚠️ 你的后端地址
const API_BASE_URL = 'http://192.168.126.130:8000'; 

// 状态变量
const showUploadDialog = ref(false);
const fileList = ref([]);
const showDetailDialog = ref(false);
const currentImage = ref({});
const newTag = ref('');


// 获取列表
const getImages = async () => {
  try {
    const res = await request.get('/api/v1/images', {
      params: { tag: searchValue.value }
    });
    images.value = res;
  } catch (error) {
    console.error(error);
  }
};

const onSearch = () => { getImages(); };

const handleLogout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

// 上传逻辑
const handleUpload = async () => {
  if (fileList.value.length === 0) {
    showToast('请先选择图片');
    return;
  }
  showToast({ message: '上传中...', type: 'loading', duration: 0 });
  try {
    const formData = new FormData();
    formData.append('file', fileList.value[0].file);
    await request.post('/api/v1/upload', formData);
    showSuccessToast('上传成功');
    showUploadDialog.value = false;
    fileList.value = [];
    getImages();
  } catch (error) {
    showFailToast('上传失败');
  }
};

// 详情页逻辑
const openDetail = (img) => {
  currentImage.value = img;
  newTag.value = '';
  showDetailDialog.value = true;
};

// 添加标签
const handleAddTag = async () => {
  if (!newTag.value.trim()) {
    showToast('请输入标签名');
    return;
  }
  try {
    const res = await request.post(`/api/v1/images/${currentImage.value.id}/tags`, null, {
      params: { tag_name: newTag.value }
    });
    showSuccessToast('标签添加成功');
    currentImage.value = res;
    const index = images.value.findIndex(i => i.id === res.id);
    if (index !== -1) images.value[index] = res;
    newTag.value = '';
  } catch (error) {
    console.error(error);
  }
};

// 【Week 4 新增】删除图片逻辑
const handleDelete = () => {
  showConfirmDialog({
    title: '确认删除',
    message: '删除后无法恢复，确定要删除这张图片吗？',
  })
    .then(async () => {
      // 用户点击了确认
      try {
        await request.delete(`/api/v1/images/${currentImage.value.id}`);
        showSuccessToast('删除成功');
        showDetailDialog.value = false; // 关闭弹窗
        getImages(); // 刷新列表
      } catch (error) {
        console.error(error);
      }
    })
    .catch(() => {
      // 用户点击了取消，什么都不做
    });
};

onMounted(() => { getImages(); });
</script>

<template>
  <div class="home-container">
    <van-nav-bar title="我的云相册" right-text="退出" @click-right="handleLogout" fixed placeholder />

    <van-search
      v-model="searchValue"
      placeholder="输入标签搜索 (如: travel)"
      show-action
      @search="onSearch"
    >
      <template #action><div @click="onSearch">搜索</div></template>
    </van-search>

    <van-grid :column-num="2" :gutter="10" style="padding: 10px">
      <van-grid-item v-for="img in images" :key="img.id" @click="openDetail(img)">
        <van-image
          width="100%"
          height="150"
          fit="cover"
          :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`"
        />
        <div class="image-info">
          <div class="tags" v-if="img.tags && img.tags.length > 0">
            <van-tag v-for="tag in img.tags" :key="tag.id" type="primary" plain style="margin-right: 4px">{{ tag.name }}</van-tag>
          </div>
          <div class="tags" v-else><span style="color: #999; font-size: 10px;">暂无标签</span></div>
        </div>
      </van-grid-item>
    </van-grid>
    
    <van-empty v-if="images.length === 0" description="暂无图片，快去上传吧" />

    <div class="float-btn" @click="showUploadDialog = true">
      <van-icon name="plus" size="24" color="#fff" />
    </div>

    <van-dialog v-model:show="showUploadDialog" title="上传图片" show-cancel-button @confirm="handleUpload">
      <div style="padding: 20px; text-align: center;">
        <van-uploader v-model="fileList" max-count="1" preview-size="200px"/>
        <p style="color: #999; font-size: 12px; margin-top: 10px;">点击上方区域选择图片</p>
      </div>
    </van-dialog>

    <van-dialog 
      v-model:show="showDetailDialog" 
      :title="currentImage.filename ? currentImage.filename.split('-')[0] : '图片详情'"
      show-confirm-button
      confirm-button-text="关闭"
      close-on-click-overlay
    >
      <div class="detail-content">
        <van-image
          v-if="currentImage.file_path"
          width="100%"
          fit="contain"
          :src="`${API_BASE_URL}/${currentImage.file_path}`"
          style="max-height: 400px; background: #000;"
        />
        
        <div style="margin: 15px 0;">
            <p style="font-size: 14px; color: #666; margin-bottom: 8px;">已有标签：</p>
            <div v-if="currentImage.tags && currentImage.tags.length > 0">
                <van-tag v-for="tag in currentImage.tags" :key="tag.id" type="primary" size="medium" style="margin-right: 6px; margin-bottom: 6px;">{{ tag.name }}</van-tag>
            </div>
            <div v-else style="color: #999; font-size: 12px;">暂无标签</div>
        </div>

        <van-field v-model="newTag" center clearable label="新标签" placeholder="输入标签名">
            <template #button>
                <van-button size="small" type="primary" @click="handleAddTag">添加</van-button>
            </template>
        </van-field>

        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;">
            <van-button type="danger" block plain @click="handleDelete">删除这张图片</van-button>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<style scoped>
.home-container { min-height: 100vh; background: #f7f8fa; padding-bottom: 80px; }
.image-info { width: 100%; padding: 5px 0; }
.tags { margin-bottom: 5px; height: 20px; overflow: hidden; }
.float-btn { position: fixed; bottom: 30px; right: 30px; width: 50px; height: 50px; background-color: #1989fa; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 100; cursor: pointer; transition: transform 0.2s; }
.float-btn:active { transform: scale(0.9); }
.detail-content { padding: 10px 20px 20px 20px; }
</style>

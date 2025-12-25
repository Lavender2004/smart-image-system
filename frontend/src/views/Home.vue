<script setup>
import { ref, onMounted, reactive } from 'vue';
import request from '../utils/request';
import { useRouter } from 'vue-router';
import { showToast, showSuccessToast, showFailToast, showConfirmDialog } from 'vant';
import 'vue-cropper/dist/index.css'
import { VueCropper }  from "vue-cropper";

const router = useRouter();
const images = ref([]);           
const topImages = ref([]);        
const searchValue = ref('');
// ⚠️ 请确认 IP 地址是否正确
const API_BASE_URL = 'http://192.168.126.130:8000'; 

// 排序
const sortValue = ref('date_desc');
const sortOptions = [
  { text: '按时间倒序', value: 'date_desc' },
  { text: '按时间正序', value: 'date_asc' },
  { text: '按热度排序', value: 'view_desc' },
  { text: '按名称排序', value: 'name_asc' },
];

// 状态变量
const showUploadDialog = ref(false);
const fileList = ref([]);
const showDetailDialog = ref(false);
const currentImage = ref({});
const newTag = ref('');

// === 信息编辑模式相关 ===
const isInfoEditing = ref(false); 
const editForm = ref({ filename: '', location: '', category: '', capture_date: '' });
const showCategoryPicker = ref(false);
const categoryOptions = [
  { text: '人像', value: '人像' },
  { text: '风景', value: '风景' },
  { text: '美食', value: '美食' },
  { text: '文字', value: '文字' },
  { text: '其他', value: '其他' },
];

// === 图片裁剪编辑器相关 ===
const showCropperDialog = ref(false); 
const cropperRef = ref(null);         
const cropOption = reactive({
  img: '',             
  outputSize: 1,       
  outputType: 'jpeg',  
  canMove: true,       
  canMoveBox: true,    
  original: false,     
  viewport: true,      
  centerBox: true,     
  high: true,          
  mode: 'contain',     
});


// =======================
// 数据获取
// =======================
const getImages = async () => {
  try {
    const res = await request.get('/api/v1/images', {
      params: { tag: searchValue.value, sort_by: sortValue.value }
    });
    images.value = res;
  } catch (error) { console.error(error); }
};

const getTopImages = async () => {
  try {
    const res = await request.get('/api/v1/images', { params: { sort_by: 'view_desc' } });
    topImages.value = res.slice(0, 5);
  } catch (error) { console.error(error); }
};

const onSearch = () => { getImages(); };
const onSortChange = () => { getImages(); };

// =======================
// 详情与信息编辑
// =======================
const openDetail = async (img) => {
  try {
    const res = await request.get(`/api/v1/images/${img.id}`);
    currentImage.value = res;
    showDetailDialog.value = true;
    newTag.value = '';
    isInfoEditing.value = false;
  } catch(e) { console.error(e); }
};

const startInfoEdit = () => {
  editForm.value = {
    filename: currentImage.value.filename,
    location: currentImage.value.location || '',
    category: currentImage.value.category || '其他',
    capture_date: currentImage.value.capture_date 
  };
  isInfoEditing.value = true;
};

const saveInfoEdit = async () => {
  try {
    const payload = {
      filename: editForm.value.filename,
      location: editForm.value.location,
      category: editForm.value.category,
      capture_date: currentImage.value.capture_date 
    };
    const res = await request.put(`/api/v1/images/${currentImage.value.id}`, payload);
    showSuccessToast('修改成功');
    currentImage.value = res;
    isInfoEditing.value = false;
    getImages();
  } catch (error) { console.error(error); }
};

const onCategoryConfirm = ({ selectedOptions }) => {
  editForm.value.category = selectedOptions[0].text;
  showCategoryPicker.value = false;
};

// =======================
// 图片裁剪逻辑
// =======================

const openEditor = () => {
  // 添加时间戳，防止浏览器缓存旧的跨域状态
  const timestamp = new Date().getTime();
  cropOption.img = `${API_BASE_URL}/${currentImage.value.file_path}?t=${timestamp}`;
  showCropperDialog.value = true;
};

const rotateLeft = () => { cropperRef.value.rotateLeft(); };
const rotateRight = () => { cropperRef.value.rotateRight(); };

const finishCrop = () => {
  showToast({ message: '处理中...', type: 'loading', duration: 0 });
  
  // 此时因为配置了 crossorigin，getCropBlob 应该能正常工作
  cropperRef.value.getCropBlob(async (data) => {
    try {
      const newFileName = `edited_${currentImage.value.filename}`;
      const file = new File([data], newFileName, { type: "image/jpeg" });
      const formData = new FormData();
      formData.append('file', file);
      
      await request.post('/api/v1/upload', formData);
      
      showSuccessToast('编辑并保存为新图成功');
      showCropperDialog.value = false; 
      showDetailDialog.value = false;  
      getImages();     
      getTopImages();  
    } catch (error) {
      showFailToast('保存失败');
      console.error(error);
    }
  });
};


// =======================
// 标签与通用逻辑
// =======================
const handleAddTag = async () => {
  if (!newTag.value.trim()) { showToast('请输入标签名'); return; }
  try {
    const res = await request.post(`/api/v1/images/${currentImage.value.id}/tags`, null, { params: { tag_name: newTag.value } });
    showSuccessToast('已添加');
    currentImage.value = res;
    const index = images.value.findIndex(i => i.id === res.id);
    if (index !== -1) images.value[index] = res;
    newTag.value = '';
  } catch (error) { console.error(error); }
};

const removeTag = async (tagId) => {
  try {
    await request.delete(`/api/v1/images/${currentImage.value.id}/tags/${tagId}`);
    showSuccessToast('标签已删除');
    currentImage.value.tags = currentImage.value.tags.filter(t => t.id !== tagId);
    const index = images.value.findIndex(i => i.id === currentImage.value.id);
    if (index !== -1) images.value[index].tags = currentImage.value.tags;
  } catch (error) { console.error(error); }
};

const handleUpload = async () => {
  if (fileList.value.length === 0) { showToast('请选图'); return; }
  showToast({ message: '上传中...', type: 'loading', duration: 0 });
  try {
    const formData = new FormData();
    formData.append('file', fileList.value[0].file);
    await request.post('/api/v1/upload', formData);
    showSuccessToast('上传成功');
    showUploadDialog.value = false;
    fileList.value = [];
    getImages(); getTopImages();
  } catch (error) { showFailToast('上传失败'); }
};

const handleDelete = () => {
  showConfirmDialog({ title: '确认删除', message: '确定要删除这张图片吗？' })
    .then(async () => {
      await request.delete(`/api/v1/images/${currentImage.value.id}`);
      showSuccessToast('删除成功');
      showDetailDialog.value = false;
      getImages(); getTopImages();
    }).catch(() => {});
};

const handleLogout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => { getImages(); getTopImages(); });
</script>

<template>
  <div class="home-container">
    <van-nav-bar title="我的云相册" right-text="退出" @click-right="handleLogout" fixed placeholder />

    <div v-if="topImages.length > 0" class="swiper-area">
      <van-swipe :autoplay="3000" indicator-color="white" style="height: 200px">
        <van-swipe-item v-for="img in topImages" :key="img.id" @click="openDetail(img)">
          <van-image width="100%" height="100%" fit="cover" :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`" />
          <div class="swiper-title">{{ img.filename }} (热度: {{ img.view_count }})</div>
        </van-swipe-item>
      </van-swipe>
    </div>

    <van-sticky :offset-top="46">
      <div class="search-bar-wrapper">
        <van-search v-model="searchValue" placeholder="搜标签/地点/名称" @search="onSearch" style="flex: 1" />
        <van-dropdown-menu>
          <van-dropdown-item v-model="sortValue" :options="sortOptions" @change="onSortChange" />
        </van-dropdown-menu>
      </div>
    </van-sticky>

    <van-grid :column-num="2" :gutter="10" style="padding: 10px">
      <van-grid-item v-for="img in images" :key="img.id" @click="openDetail(img)">
        <van-image width="100%" height="150" fit="cover" :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`" />
        <div class="image-info">
          <div class="tags">
             <van-tag v-if="img.location" type="warning" plain style="margin-right:4px">{{ img.location }}</van-tag>
             <van-tag v-for="tag in img.tags" :key="tag.id" type="primary" plain style="margin-right: 4px">{{ tag.name }}</van-tag>
          </div>
          <p class="meta-info">{{ img.view_count }}次浏览 | {{ img.category }}</p>
        </div>
      </van-grid-item>
    </van-grid>
    <van-empty v-if="images.length === 0" description="暂无图片" />

    <div class="float-btn" @click="showUploadDialog = true"><van-icon name="plus" size="24" color="#fff" /></div>

    <van-dialog v-model:show="showUploadDialog" title="上传图片" show-cancel-button @confirm="handleUpload">
      <div style="padding: 20px; text-align: center;">
        <van-uploader v-model="fileList" max-count="1" preview-size="200px"/>
      </div>
    </van-dialog>

    <van-dialog 
      v-model:show="showDetailDialog" 
      :title="isInfoEditing ? '编辑信息' : '图片详情'"
      :show-confirm-button="false"
      close-on-click-overlay
    >
      <div class="detail-content">
        <van-image v-if="currentImage.file_path" width="100%" fit="contain" :src="`${API_BASE_URL}/${currentImage.file_path}`" style="max-height: 300px; background: #000;" />
        
        <div v-if="!isInfoEditing" style="margin-top: 15px;">
            <h3 style="margin:0; font-size:16px;">{{ currentImage.filename }}</h3>
            <div class="info-block">
                <p>📅 {{ currentImage.capture_date ? currentImage.capture_date.replace('T', ' ') : '未知' }}</p>
                <p>📍 {{ currentImage.location || '未设置地点' }}</p>
                <p>📂 {{ currentImage.category || '未分类' }}</p>
                <p>🔥 {{ currentImage.view_count }} 次浏览</p>
            </div>

            <div style="margin: 10px 0;">
                <span style="font-size:12px; color:#999;">标签: </span>
                <van-tag 
                  v-for="tag in currentImage.tags" 
                  :key="tag.id" 
                  closeable
                  size="medium" 
                  type="primary" 
                  plain
                  style="margin-right:6px; margin-bottom:4px;"
                  @close="removeTag(tag.id)"
                >
                  {{ tag.name }}
                </van-tag>
            </div>
            
             <van-field v-model="newTag" center clearable placeholder="输入新标签" style="padding:0; margin-bottom:10px;">
                <template #button><van-button size="small" type="primary" @click="handleAddTag">贴标签</van-button></template>
            </van-field>

            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <van-button icon="photograph" block type="warning" size="small" @click="openEditor">修图 / 裁剪</van-button>
                <van-button icon="edit" block type="primary" plain size="small" @click="startInfoEdit">编辑信息</van-button>
                <van-button icon="delete" block type="danger" plain size="small" @click="handleDelete">删除图片</van-button>
            </div>
        </div>

        <div v-else style="margin-top: 15px;">
            <van-cell-group inset>
                <van-field v-model="editForm.filename" label="名称" />
                <van-field v-model="editForm.location" label="地点" />
                <van-field 
                   v-model="editForm.category" 
                   is-link readonly 
                   label="分类" 
                   @click="showCategoryPicker = true" 
                />
            </van-cell-group>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <van-button block type="default" size="small" @click="isInfoEditing = false">取消</van-button>
                <van-button block type="primary" size="small" @click="saveInfoEdit">保存修改</van-button>
            </div>
        </div>
      </div>
    </van-dialog>

    <van-popup v-model:show="showCategoryPicker" round position="bottom">
      <van-picker :columns="categoryOptions" @cancel="showCategoryPicker = false" @confirm="onCategoryConfirm" />
    </van-popup>

    <van-dialog 
      v-model:show="showCropperDialog" 
      title="图片编辑器" 
      :show-confirm-button="false"
      close-on-click-overlay
      style="width: 95%; max-width: 600px;"
    >
      <div class="editor-container" v-if="showCropperDialog">
        <div class="cropper-wrapper">
          <vue-cropper
            ref="cropperRef"
            :img="cropOption.img"
            :outputSize="cropOption.outputSize"
            :outputType="cropOption.outputType"
            :canMove="cropOption.canMove"
            :canMoveBox="cropOption.canMoveBox"
            :original="cropOption.original"
            :autoCrop="true"
            :fixed="false"
            :centerBox="cropOption.centerBox"
            :img-props="{ crossorigin: 'anonymous' }"
          ></vue-cropper>
        </div>

        <div class="editor-toolbar">
          <van-button icon="replay" size="small" @click="rotateLeft">左旋</van-button>
          
          <van-button size="small" @click="rotateRight">
             <van-icon name="replay" class="icon-flip" style="margin-right: 4px;" />
             右旋
          </van-button>
          
          <div style="flex: 1;"></div>
          <van-button type="primary" size="small" @click="finishCrop">保存为新图</van-button>
        </div>
      </div>
    </van-dialog>

  </div>
</template>

<style scoped>
.home-container { min-height: 100vh; background: #f7f8fa; padding-bottom: 80px; }
.search-bar-wrapper { display: flex; align-items: center; background: #fff; }
.swiper-area { background: #333; margin-bottom: 10px; position: relative; }
.swiper-title { position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.5); color: #fff; padding: 5px 10px; font-size: 12px; box-sizing: border-box; }
.image-info { padding: 5px 0; }
.tags { height: 20px; overflow: hidden; margin-bottom: 2px; }
.meta-info { font-size: 10px; color: #999; margin: 0; }
.info-block p { margin: 4px 0; font-size: 13px; color: #666; }
.float-btn { position: fixed; bottom: 30px; right: 30px; width: 50px; height: 50px; background-color: #1989fa; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 100; cursor: pointer; transition: transform 0.2s; }
.detail-content { padding: 10px 20px 20px 20px; }

/* 编辑器样式 */
.editor-container { height: 500px; display: flex; flex-direction: column; }
.cropper-wrapper { flex: 1; width: 100%; background: #333; position: relative; }
.editor-toolbar { height: 60px; display: flex; align-items: center; padding: 0 15px; gap: 10px; background: #fff; border-top: 1px solid #eee; }

/* 水平翻转图标 */
.icon-flip {
  transform: scaleX(-1);
  display: inline-block; /* 确保 transform 生效 */
}
</style>

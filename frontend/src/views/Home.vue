<script setup>
import { ref, reactive, nextTick, onMounted, watch } from 'vue';
import request from '../utils/request';
import { useRouter } from 'vue-router';
import { 
  showToast, showSuccessToast, showFailToast, showConfirmDialog, showImagePreview 
} from 'vant';
import 'vue-cropper/dist/index.css'
import { VueCropper }  from "vue-cropper";

const router = useRouter();
const API_BASE_URL = ''; 

const activeTab = ref('gallery'); 
const isDarkMode = ref(false);    
const isSearchSticky = ref(false);

const images = ref([]);             
const topImages = ref([]);        
const searchValue = ref('');

const showUploadDialog = ref(false);
const fileList = ref([]); 

const showDetailDialog = ref(false);
const currentImage = ref({});
const isInfoEditing = ref(false);
const editForm = ref({ filename: '', location: '', category: '', capture_date: '' });
const tempExtension = ref(''); 
const newTag = ref('');
const showCategoryPicker = ref(false);
const categoryOptions = [
  { text: '人像', value: '人像' }, { text: '风景', value: '风景' }, 
  { text: '美食', value: '美食' }, { text: '文字', value: '文字' }, { text: '其他', value: '其他' }
];

const showCloudAlbumPicker = ref(false); 

const showCropperDialog = ref(false);
const editorStep = ref(1); 
const cropperRef = ref(null);
const canvasRef = ref(null);
const cropKey = ref(0); 

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
  autoCrop: true,            
  fixedBox: false,
  full: true,      
  infoTrue: true    
});

const editConfig = reactive({
  brightness: 100, 
  contrast: 100,   
  saturate: 100,   
});

let tempCroppedImg = null;    

const openEditor = () => {
  showCropperDialog.value = true;
  editorStep.value = 1;
  editConfig.brightness = 100;
  editConfig.contrast = 100;
  editConfig.saturate = 100;
  
  setTimeout(() => {
    cropKey.value++; 
    const timestamp = new Date().getTime();
    cropOption.img = `${API_BASE_URL}/${currentImage.value.file_path}?t=${timestamp}`;
  }, 200);
};

const confirmCropToEdit = () => {
  if (!cropperRef.value) {
      showFailToast('编辑器未就绪，请重试');
      return;
  }

  const loadingToast = showToast({ message: '准备画布中...', type: 'loading', duration: 0 });

  cropperRef.value.getCropBlob((data) => {
    if (!data) {
      loadingToast.close();
      showFailToast('裁剪失败：检测到跨域或图片错误');
      return;
    }

    const blobUrl = URL.createObjectURL(data);
    const img = new Image();
    
    img.onerror = (err) => {
      loadingToast.close();
      showFailToast('无法加载裁剪结果');
      URL.revokeObjectURL(blobUrl); 
    };

    img.onload = () => {
      tempCroppedImg = img;
      editorStep.value = 2; 
      loadingToast.close();
      
      nextTick(() => {
        renderCanvas();
        URL.revokeObjectURL(blobUrl); 
      });
    };

    img.src = blobUrl;
  });
};

const renderCanvas = () => {
  const canvas = canvasRef.value;
  if (!canvas || !tempCroppedImg) return;
  const ctx = canvas.getContext('2d');

  if (canvas.width !== tempCroppedImg.width || canvas.height !== tempCroppedImg.height) {
     canvas.width = tempCroppedImg.width;
     canvas.height = tempCroppedImg.height;
  }

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.filter = `brightness(${editConfig.brightness}%) contrast(${editConfig.contrast}%) saturate(${editConfig.saturate}%)`;
  ctx.drawImage(tempCroppedImg, 0, 0);
  ctx.filter = 'none'; 
};

const saveFinalImage = () => {
  const canvas = canvasRef.value;
  canvas.toBlob(async (blob) => {
      try {
        const loadingToast = showToast({ message: '上传中...', type: 'loading', duration: 0 });
        const newFileName = `edited_${currentImage.value.filename}`;
        const file = new File([blob], newFileName, { type: "image/jpeg" });
        const formData = new FormData();
        formData.append('file', file);
        await request.post('/api/v1/upload', formData);
        loadingToast.close();
        showSuccessToast('保存成功');
        showCropperDialog.value = false; 
        showDetailDialog.value = false; 
        getImages();
      } catch (e) { 
          showFailToast('保存失败'); 
      }
  }, 'image/jpeg', 0.9);
};

watch(() => [editConfig.brightness, editConfig.contrast, editConfig.saturate], () => {
    renderCanvas();
});

const rotateLeft = () => {
  if (!cropperRef.value) return;
  cropperRef.value.rotateLeft();
  nextTick(() => { cropperRef.value.goAutoCrop(); });
};

const rotateRight = () => {
  if (!cropperRef.value) return;
  cropperRef.value.rotateRight();
  nextTick(() => { cropperRef.value.goAutoCrop(); });
};

const stripExt = (filename) => {
  if (!filename) return '';
  return filename.replace(/\.[^/.]+$/, "");
};

const syncImageToList = (updatedImg) => {
    if (!updatedImg || !updatedImg.id) return;
    const idx = images.value.findIndex(i => i.id === updatedImg.id);
    if (idx !== -1) {
        images.value[idx] = { ...images.value[idx], ...updatedImg };
    }
    const topIdx = topImages.value.findIndex(i => i.id === updatedImg.id);
    if (topIdx !== -1) {
        topImages.value[topIdx] = { ...topImages.value[topIdx], ...updatedImg };
    }
};

watch(isDarkMode, (newVal) => {
  if (newVal) {
    document.body.style.backgroundColor = '#1c1c1e';
    document.body.classList.add('dark-mode-body');
  } else {
    document.body.style.backgroundColor = '#f7f8fa';
    document.body.classList.remove('dark-mode-body');
  }
}, { immediate: true });

const chatInput = ref('');
const chatListRef = ref(null);
const initialAiMsg = { 
    type: 'ai', 
    content: '你好！我是你的智能相册助手。\n你可以描述图片内容，或者点击左侧图标从相册选一张图让我分析。', 
    images: [] 
};
const chatHistory = ref([ initialAiMsg ]);
const searchResultCache = ref([]); 
const currentCacheIndex = ref(0);

const handleClearChat = () => {
    showConfirmDialog({
        title: '清空对话',
        message: '确定要清空当前的聊天记录吗？'
    }).then(() => {
        chatHistory.value = [ initialAiMsg ];
        showSuccessToast('已清空');
    }).catch(() => {});
};

const scrollToBottom = () => {
  nextTick(() => {
    if (chatListRef.value) {
      chatListRef.value.scrollTop = chatListRef.value.scrollHeight;
    }
  });
};

const handleSendMessage = async () => {
  const text = chatInput.value.trim();
  if (!text) return;

  chatHistory.value.push({ type: 'user', content: text });
  chatInput.value = '';
  scrollToBottom();

  const isMoreRequest = /再|更多|还有|不|换一批/.test(text);

  if (isMoreRequest && searchResultCache.value.length > 0) {
    chatHistory.value.push({ type: 'ai', content: '好的，正在挖掘更多结果...', loading: true });
    scrollToBottom();
    setTimeout(() => {
       const lastMsg = chatHistory.value[chatHistory.value.length - 1];
       lastMsg.loading = false;
       const hasMore = loadNextBatchToChat(lastMsg);
       if (!hasMore) lastMsg.content = '库里相关的图片已经全部展示完啦！';
       else lastMsg.content = '看看这些是否符合你的要求？';
    }, 600); 
  } else {
    chatHistory.value.push({ type: 'ai', content: '正在思考并检索中...', loading: true });
    scrollToBottom();
    try {
      const res = await request.get('/api/v1/search/smart', { params: { query: text } });
      const lastMsg = chatHistory.value[chatHistory.value.length - 1];
      lastMsg.loading = false;
      if (res && res.length > 0) {
        searchResultCache.value = res;
        currentCacheIndex.value = 0; 
        lastMsg.content = `找到了 ${res.length} 张相关图片：`;
        loadNextBatchToChat(lastMsg); 
      } else {
        lastMsg.content = '抱歉，没有找到符合条件的图片，换个关键词试试？';
      }
    } catch (error) {
      const lastMsg = chatHistory.value[chatHistory.value.length - 1];
      lastMsg.loading = false;
      lastMsg.content = 'AI 大脑暂时连不上了，请稍后再试 🤯';
    }
  }
};

const loadNextBatchToChat = (messageObj) => {
  const BATCH_SIZE = 4; 
  if (currentCacheIndex.value >= searchResultCache.value.length) return false;
  const batch = searchResultCache.value.slice(currentCacheIndex.value, currentCacheIndex.value + BATCH_SIZE);
  currentCacheIndex.value += BATCH_SIZE;
  messageObj.images = batch;
  scrollToBottom();
  return true;
};

const handleSelectFromPicker = async (img) => {
  showCloudAlbumPicker.value = false; 

  chatHistory.value.push({ 
    type: 'user-image', 
    content: `${API_BASE_URL}/${img.file_path}` 
  });
  scrollToBottom();

  chatHistory.value.push({ 
    type: 'ai', 
    content: '正在分析云端原图...', 
    loading: true 
  });
  scrollToBottom();

  try {
    const res = await request.post(`/api/v1/chat/describe/${img.id}`, null, {
      timeout: 60000 
    });

    const lastMsg = chatHistory.value[chatHistory.value.length - 1];
    lastMsg.loading = false;
    lastMsg.content = res.description || '分析完成。';
    scrollToBottom();
  } catch (error) {
    const lastMsg = chatHistory.value[chatHistory.value.length - 1];
    lastMsg.loading = false;
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        lastMsg.content = 'AI 思考时间过长，请稍后再试。';
    } else {
        lastMsg.content = '分析失败，请检查网络或后端状态。';
    }
  }
};

const showPreview = (url) => {
    showImagePreview([url]);
};

const handleBatchUpload = async () => {
  if (fileList.value.length === 0) { showToast('请至少选择一张图片'); return; }
  const total = fileList.value.length;
  const loading = showToast({ message: `正在上传 0/${total}`, type: 'loading', duration: 0 });
  let successCount = 0;
  try {
    const uploadPromises = fileList.value.map(async (item) => {
      const formData = new FormData();
      formData.append('file', item.file);
      try {
        await request.post('/api/v1/upload', formData);
        successCount++;
        loading.message = `正在上传 ${successCount}/${total}`;
      } catch (e) { console.error("Single Upload failed", e); }
    });
    await Promise.all(uploadPromises);
    if (successCount === 0) {
        showFailToast('上传失败，请检查网络或图片格式');
    } else if (successCount < total) {
        showToast(`部分成功：${successCount}/${total} 张`);
    } else {
        showSuccessToast(`成功上传 ${successCount} 张，AI 分析中...`);
    }
    showUploadDialog.value = false;
    fileList.value = [];
    setTimeout(() => { getImages(); getTopImages(); }, 2000);
  } catch (error) { showFailToast('上传服务异常'); } 
  finally { loading.clear(); }
};

const toggleTheme = () => { isDarkMode.value = !isDarkMode.value; };

const getImages = async () => {
  try {
    const res = await request.get('/api/v1/images', {
      params: { tag: searchValue.value, sort_by: 'date_desc' }
    });
    images.value = res || [];
  } catch (error) { console.error('加载列表失败', error); }
};

const getTopImages = async () => {
  try {
    const res = await request.get('/api/v1/images', { params: { sort_by: 'view_desc' } });
    topImages.value = res.slice(0, 10);
  } catch (error) { console.error(error); }
};

const openDetail = async (img) => {
  try {
    const res = await request.get(`/api/v1/images/${img.id}`);
    currentImage.value = res;
    showDetailDialog.value = true;
    isInfoEditing.value = false;
    newTag.value = ''; 
  } catch(e) { showFailToast('无法获取图片详情'); }
};

const handleAddTag = async () => {
    if(!newTag.value.trim()) return;
    try {
      const res = await request.post(`/api/v1/images/${currentImage.value.id}/tags`, null, { params: { tag_name: newTag.value }});
      currentImage.value = res; 
      syncImageToList(res);
      newTag.value = '';
      showSuccessToast('已添加');
    } catch(e) { showFailToast('添加标签失败'); }
}

const removeTag = async (tid) => {
    try {
        await request.delete(`/api/v1/images/${currentImage.value.id}/tags/${tid}`);
        const updatedTags = currentImage.value.tags.filter(t=>t.id!==tid);
        currentImage.value.tags = updatedTags;
        syncImageToList({ ...currentImage.value, tags: updatedTags });
        showSuccessToast('已删除');
    } catch(e) { showFailToast('删除标签失败'); }
}

const handleDelete = () => {
    showConfirmDialog({title:'删除', message:'确认删除这张图片?'}).then(async()=>{
        try {
            await request.delete(`/api/v1/images/${currentImage.value.id}`);
            showSuccessToast('删除成功');
            showDetailDialog.value=false; 
            getImages(); 
        } catch(e) { showFailToast('删除失败，请重试'); }
    }).catch(()=>{});
}

const startInfoEdit = () => {
  const fullFilename = currentImage.value.filename || '';
  const lastDotIndex = fullFilename.lastIndexOf('.');
  if (lastDotIndex !== -1) {
      tempExtension.value = fullFilename.substring(lastDotIndex);
      editForm.value = { 
          ...currentImage.value, 
          filename: fullFilename.substring(0, lastDotIndex),
          category: currentImage.value.category || '其他' 
      };
  } else {
      tempExtension.value = '';
      editForm.value = { ...currentImage.value, category: currentImage.value.category || '其他' };
  }
  isInfoEditing.value = true;
};

const saveInfoEdit = async () => {
  try {
      const payload = { ...editForm.value };
      payload.filename = payload.filename + tempExtension.value;
      const res = await request.put(`/api/v1/images/${currentImage.value.id}`, payload);
      currentImage.value = res; 
      syncImageToList(res);
      isInfoEditing.value = false; 
      getImages();
      showSuccessToast('信息已更新');
  } catch(e) { showFailToast('更新失败'); }
};

const onCategoryConfirm = ({ selectedOptions }) => {
  editForm.value.category = selectedOptions[0].text; showCategoryPicker.value=false;
};

const handleLogout = () => { 
    showConfirmDialog({ title: '提示', message: '确定要退出登录吗？' }).then(() => {
        localStorage.removeItem('token'); 
        router.push('/login'); 
    }).catch(() => {});
};

onMounted(() => { getImages(); getTopImages(); });
</script>

<template>
  <div class="app-wrapper" :class="{ 'dark-mode': isDarkMode }">
    <van-nav-bar 
        :title="activeTab === 'gallery' ? '我的云相册' : 'AI 助手'" 
        fixed placeholder z-index="99" :border="false" class="glass-nav"
    >
      <template #right>
         <van-icon 
            :name="isDarkMode ? 'bulb-o' : 'closed-eye'" size="22" @click="toggleTheme" 
            style="margin-right: 16px; cursor: pointer" :color="isDarkMode ? '#ffd21e' : '#333'"
         />
         <span v-if="activeTab === 'gallery'" @click="handleLogout" class="logout-btn">退出</span>
         <van-icon 
            v-else-if="activeTab === 'chat'" name="delete-o" size="20" @click="handleClearChat" 
            :color="isDarkMode ? '#fff' : '#333'" style="cursor: pointer"
         />
      </template>
    </van-nav-bar>

    <div class="main-content">
      <div v-show="activeTab === 'gallery'" class="gallery-view">
        <div v-if="topImages.length > 0" class="swiper-box">
          <van-swipe :autoplay="5000" indicator-color="#fff" class="my-swipe" :key="topImages.length">
            <van-swipe-item v-for="(img, index) in topImages" :key="img.id" @click="openDetail(img)" class="custom-swipe-item">
              <div class="banner-image-container">
                  <van-image width="100%" height="100%" fit="contain" :src="`${API_BASE_URL}/${img.file_path}`" class="banner-image" style="background-color: #000;"/>
                  <div class="gradient-overlay"></div>
                  <div class="swiper-desc"><span class="title">{{ stripExt(img.filename) }}</span></div>
              </div>
            </van-swipe-item>
          </van-swipe>
        </div>

        <van-sticky :offset-top="46" @change="(isFixed) => isSearchSticky = isFixed">
          <div class="filter-bar" :class="{ 'sticky-active': isSearchSticky }">
            <van-search v-model="searchValue" placeholder="搜索图片 / 标签 / 地点..." @search="getImages" shape="round" background="transparent" class="flex-search"/>
          </div>
        </van-sticky>

        <div class="grid-box">
          <van-grid :column-num="3" :gutter="10" :border="false">
            <van-grid-item v-for="img in images" :key="img.id" class="grid-card" @click="openDetail(img)">
              <div class="card-inner">
                  <div class="card-img-wrap">
                      <van-image width="100%" height="100%" fit="cover" :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`" />
                      <div class="card-badge" v-if="img.category">{{ img.category }}</div>
                  </div>
                  <div class="card-info">
                    <div class="info-tags" v-if="img.location || img.tags.length">
                        <van-tag v-if="img.location" color="#ff976a" plain size="mini" class="mini-tag">📍{{ img.location }}</van-tag>
                        <van-tag v-for="t in img.tags.slice(0,3)" :key="t.id" type="primary" plain size="mini" class="mini-tag">#{{t.name}}</van-tag>
                    </div>
                    <div v-else class="info-placeholder"></div>
                  </div>
              </div>
            </van-grid-item>
          </van-grid>
          <van-empty v-if="images.length === 0" description="空空如也" image="search" />
        </div>

        <div class="fab-btn" @click="showUploadDialog = true">
           <van-icon name="plus" size="24" color="#fff"/>
        </div>
      </div>

      <div v-show="activeTab === 'chat'" class="chat-view">
        <div class="chat-list" ref="chatListRef">
           <div v-for="(msg, idx) in chatHistory" :key="idx" class="chat-item" :class="msg.type === 'user-image' ? 'user' : msg.type">
             <div class="content-wrapper">
                 
                 <div v-if="msg.type !== 'user-image'" class="bubble">
                    <div v-if="msg.loading" class="typing-indicator"><span>.</span><span>.</span><span>.</span></div>
                    <span v-else>{{ msg.content }}</span>
                 </div>

                 <div v-else class="chat-user-image">
                    <van-image 
                      :src="msg.content" 
                      width="120" 
                      height="120" 
                      fit="cover" 
                      radius="12"
                      @click="showPreview(msg.content)"
                      style="border: 2px solid #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.1);"
                    />
                 </div>

                 <div v-if="msg.images && msg.images.length > 0" class="chat-images">
                    <div v-for="img in msg.images" :key="img.id" class="chat-img-card" @click="openDetail(img)">
                       <van-image width="100%" height="80" fit="cover" :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`" radius="6" />
                       <div class="score-tag">{{ stripExt(img.filename) }}</div>
                    </div>
                 </div>

             </div>
           </div>
        </div>

        <div class="chat-input-area">
           <div class="icon-btn" @click="showCloudAlbumPicker = true">
              <van-icon name="photo-o" size="24" color="#666"/>
           </div>

           <van-field 
             v-model="chatInput" 
             center 
             clearable 
             placeholder="描述你想找的图片..." 
             @keydown.enter="handleSendMessage"
             class="chat-input-field"
           >
             <template #button>
                 <van-button size="small" type="primary" @click="handleSendMessage" :disabled="!chatInput" round>发送</van-button>
             </template>
           </van-field>
        </div>
      </div>
    </div>

    <van-popup v-model:show="showCloudAlbumPicker" position="bottom" round :style="{ height: '70%' }" class="cloud-picker-popup">
        <div class="picker-header">
            <span>选择一张云端图片</span>
            <van-icon name="cross" @click="showCloudAlbumPicker = false" />
        </div>
        <div class="picker-content">
            <van-grid :column-num="3" :gutter="8" square>
                <van-grid-item v-for="img in images" :key="img.id" @click="handleSelectFromPicker(img)">
                    <van-image 
                        width="100%" 
                        height="100%" 
                        fit="cover" 
                        :src="`${API_BASE_URL}/${img.thumbnail_path || img.file_path}`" 
                        radius="4" 
                    />
                </van-grid-item>
            </van-grid>
            <van-empty v-if="images.length === 0" description="暂无云端图片" />
        </div>
    </van-popup>

    <van-tabbar v-model="activeTab" fixed safe-area-inset-bottom :border="false" class="glass-tabbar" z-index="1000">
      <van-tabbar-item name="gallery" icon="photo-o">相册</van-tabbar-item>
      <van-tabbar-item name="chat" icon="chat-o">AI</van-tabbar-item>
    </van-tabbar>

    <van-dialog v-model:show="showUploadDialog" title="上传图片" show-cancel-button @confirm="handleBatchUpload" confirm-button-color="#1989fa" z-index="2000">
      <div class="upload-box">
        <van-uploader v-model="fileList" multiple :max-count="9" preview-size="80px" />
        <p class="hint">支持多选，上传后 AI 自动分析内容</p>
      </div>
    </van-dialog>

    <van-dialog v-model:show="showDetailDialog" :show-confirm-button="false" close-on-click-overlay class="detail-dialog">
       <div class="detail-body">
         <div class="detail-img-box">
           <van-image v-if="currentImage.file_path" width="100%" :src="`${API_BASE_URL}/${currentImage.file_path}`" fit="widthFix" />
         </div>
         
         <div v-if="!isInfoEditing" class="info-panel">
             <div class="meta-header">
                <span class="date">{{ currentImage.capture_date?.split('T')[0] || '未知日期' }}</span>
                <span class="views"><van-icon name="eye-o" /> {{ currentImage.view_count }}</span>
             </div>
             <div class="image-title">{{ stripExt(currentImage.filename) }}</div>
             <div class="tags-container">
                <van-tag v-if="currentImage.location" type="warning" size="medium" class="tag-item">
                   <van-icon name="location-o" style="margin-right:2px"/> {{ currentImage.location }}
                </van-tag>
                <van-tag v-for="t in currentImage.tags" :key="t.id" type="primary" plain size="medium" class="tag-item" closeable @close="removeTag(t.id)">#{{t.name}}</van-tag>
                <div class="new-tag-input">
                   <input v-model="newTag" type="text" placeholder="添加标签..." @keydown.enter="handleAddTag"/>
                   <span class="add-btn" @click="handleAddTag"><van-icon name="plus" /></span>
                </div>
             </div>
             <div class="action-bar">
                <div class="action-btn" @click="startInfoEdit">
                   <div class="icon-circle edit"><van-icon name="edit" /></div>
                   <span>编辑</span>
                </div>
                <div class="action-btn" @click="openEditor">
                   <div class="icon-circle crop"><van-icon name="photograph" /></div>
                   <span>修图</span>
                </div>
                <div class="action-btn" @click="handleDelete">
                   <div class="icon-circle delete"><van-icon name="delete" /></div>
                   <span>删除</span>
                </div>
             </div>
         </div>

         <div v-else class="edit-panel">
             <van-field v-model="editForm.filename" label="标题" placeholder="请输入标题" />
             <van-field v-model="editForm.location" label="地点" placeholder="请输入拍摄地" />
             <van-field v-model="editForm.category" label="分类" readonly @click="showCategoryPicker=true" />
             <div class="btn-row">
                <van-button size="small" block round @click="isInfoEditing=false">取消</van-button>
                <van-button size="small" type="primary" block round @click="saveInfoEdit">保存修改</van-button>
             </div>
         </div>
       </div>
    </van-dialog>

    <van-popup v-model:show="showCategoryPicker" round position="bottom">
      <van-picker :columns="categoryOptions" @confirm="onCategoryConfirm" @cancel="showCategoryPicker=false"/>
    </van-popup>

    <van-dialog 
      v-model:show="showCropperDialog" 
      :show-confirm-button="false" 
      class="cropper-dialog" 
      :close-on-click-overlay="true"
    >
       <div class="cropper-wrapper-box">
         
         <div v-if="editorStep === 1" class="editor-stage">
            <div class="editor-canvas-area">
               <vue-cropper 
                  ref="cropperRef" 
                  :key="cropKey"
                  v-bind="cropOption" 
                  :autoCropWidth="300"
                  :autoCropHeight="300"
                  :img-props="{ crossorigin: 'anonymous' }" 
               />
            </div>
            <div class="editor-toolbar">
               <div class="tool-row">
                  <van-button size="small" @click="rotateLeft">左旋</van-button>
                  <van-button size="small" @click="rotateRight">右旋</van-button>
               </div>
               <van-button type="primary" block round @click="confirmCropToEdit">下一步：美化</van-button>
            </div>
         </div>

         <div v-else class="editor-stage">
            <div class="editor-canvas-area centered-canvas">
               <canvas 
                  ref="canvasRef" 
                  class="drawing-canvas"
               ></canvas>
            </div>
            
            <div class="editor-toolbar scrollable-tools">
               
               <div class="tool-section">
                  <div class="slider-row">
                     <span class="label">亮度</span>
                     <van-slider v-model="editConfig.brightness" :min="50" :max="150" bar-height="4px" active-color="#fff">
                        <template #button><div class="custom-button">{{ editConfig.brightness }}</div></template>
                     </van-slider>
                  </div>
                  <div class="slider-row">
                     <span class="label">对比</span>
                     <van-slider v-model="editConfig.contrast" :min="50" :max="150" bar-height="4px" active-color="#fff">
                        <template #button><div class="custom-button">{{ editConfig.contrast }}</div></template>
                     </van-slider>
                  </div>
                  <div class="slider-row">
                     <span class="label">饱和</span>
                     <van-slider v-model="editConfig.saturate" :min="0" :max="200" bar-height="4px" active-color="#fff">
                        <template #button><div class="custom-button">{{ editConfig.saturate }}</div></template>
                     </van-slider>
                  </div>
               </div>

               <div class="action-row">
                  <van-button size="small" round @click="editorStep = 1">返回裁剪</van-button>
                  <van-button size="small" type="primary" round @click="saveFinalImage">保存图片</van-button>
               </div>
            </div>
         </div>

       </div>
    </van-dialog>

  </div>
</template>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  padding-bottom: 50px; 
  padding-top: 46px;    
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  width: 100vw;
  max-width: 100%;
  overflow-x: hidden; 
  margin: 0 auto;
}

.app-wrapper.dark-mode {
  color: #f5f5f5;
  --van-nav-bar-background: rgba(28, 28, 30, 0.8);
  --van-nav-bar-title-text-color: #fff;
  --van-tabbar-background: rgba(28, 28, 30, 0.95);
  --van-tabbar-item-active-background: transparent;
  --van-tabbar-item-text-color: #888888;
  --van-tabbar-item-active-color: #ffffff;
  --van-search-content-background: #2c2c2e;
  --van-search-label-color: #fff;
  --van-text-color: #fff;
  --van-cell-background: #2c2c2e;
  --van-cell-text-color: #fff;
  --van-dialog-background: #2c2c2e;
  --van-popup-background: #2c2c2e;
}

.logout-btn { font-size: 14px; color: #1989fa; cursor: pointer; font-weight: 500; }
.dark-mode .logout-btn { color: #5aaaff; }

.glass-nav :deep(.van-nav-bar__content),
.glass-tabbar {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(0,0,0,0.05);
}
.dark-mode .glass-nav :deep(.van-nav-bar__content),
.dark-mode .glass-tabbar {
    background: rgba(28, 28, 30, 0.85);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    border-top: 1px solid rgba(255,255,255,0.05);
}

.gallery-view { width: 100%; overflow: hidden; }
.swiper-box { margin: 16px; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,0.12); background: #000; position: relative; width: auto; max-width: calc(100vw - 32px); min-height: 200px; }
.my-swipe { height: 260px; }
.custom-swipe-item { height: 100%; flex-shrink: 0; display: flex; align-items: center; justify-content: center; background: #000; }
.banner-image-container { position: relative; width: 100%; height: 100%; }
.banner-image :deep(img) { display: block; width: 100% !important; height: 100% !important; object-fit: contain; }
.gradient-overlay { position: absolute; bottom: 0; left: 0; right: 0; height: 50%; background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%); pointer-events: none; }
.swiper-desc { position: absolute; bottom: 12px; left: 16px; right: 16px; color: #fff; z-index: 2; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
.title { font-weight: 600; font-size: 16px; letter-spacing: 0.5px; }

.filter-bar { display: flex; align-items: center; padding: 10px 16px; background: transparent; box-shadow: none; }
.dark-mode .filter-bar { background: transparent; }
:deep(.van-search__content) { background-color: #ffffff; box-shadow: 0 2px 6px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02); }
.dark-mode :deep(.van-search__content) { background-color: #2c2c2e; box-shadow: none; border: 1px solid rgba(255,255,255,0.05); }
.flex-search { flex: 1; padding: 0; margin-right: 0; }

.grid-box { padding: 8px 16px; margin-bottom: 20px;}
.grid-card { overflow: visible; }
.card-inner { width: 100%; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: transform 0.2s; }
.card-inner:active { transform: scale(0.98); }
.dark-mode .card-inner { background: #2c2c2e; box-shadow: none; border: 1px solid rgba(255,255,255,0.05); }
:deep(.van-grid-item__content) { padding: 0 !important; background: transparent !important; } 
.card-img-wrap { position: relative; width: 100%; padding-top: 100%; background: #f0f0f0; }
.dark-mode .card-img-wrap { background: #3a3a3c; }
.card-img-wrap .van-image { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
.card-badge { position: absolute; top: 6px; right: 6px; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 6px; font-weight: 500; }
.card-info { padding: 8px; height: 40px; display: flex; align-items: center; }
.info-tags { display: flex; flex-wrap: wrap; gap: 4px; width: 100%; }
.info-placeholder { height: 16px; }
.mini-tag { border-radius: 4px; }

.fab-btn { position: fixed; bottom: 80px; right: 24px; width: 56px; height: 56px; background: linear-gradient(135deg, #2979ff, #1565c0); border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 20px rgba(41, 121, 255, 0.4); z-index: 90; }
.fab-btn:active { transform: scale(0.9); }
.dark-mode .fab-btn { background: linear-gradient(135deg, #0a84ff, #0056b3); }

.chat-view { position: fixed; top: 46px; bottom: 50px; left: 0; right: 0; display: flex; flex-direction: column; background: #fff; z-index: 10; }
.dark-mode .chat-view { background: #1c1c1e; }
.chat-list { flex: 1; overflow-y: auto; padding: 20px 16px; scroll-behavior: smooth; }
.chat-item { display: flex; margin-bottom: 24px; width: 100%; }
.chat-item.ai { justify-content: flex-start; }
.chat-item.user { justify-content: flex-end; }
.content-wrapper { max-width: 80%; display: flex; flex-direction: column; }
.chat-item.user .content-wrapper { align-items: flex-end; }
.chat-item.ai .content-wrapper { align-items: flex-start; }
.bubble { padding: 12px 16px; border-radius: 16px; font-size: 15px; line-height: 1.5; background: #f2f3f5; color: #333; }
.user .bubble { background: #1989fa; color: #fff; border-bottom-right-radius: 4px; }
.ai .bubble { background: #fff; border-bottom-left-radius: 4px; border: 1px solid #eee; }
.dark-mode .ai .bubble { background: #2c2c2e; color: #eee; border-color: #3a3a3c; }
.chat-input-area { flex-shrink: 0; padding: 12px 16px; border-top: 1px solid #f0f0f0; background: #fff; z-index: 10; }
.dark-mode .chat-input-area { background: #1c1c1e; border-color: #2c2c2e; }
.dark-mode :deep(.van-field__control) { color: #fff; caret-color: #1989fa; }
.score-tag { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6); color: #fff; font-size: 11px; padding: 4px 6px; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.detail-img-box { background: #000; display: flex; justify-content: center; align-items: flex-start; width: 100%; max-height: 60vh; overflow-y: auto; overflow-x: hidden; }
.info-panel { padding: 24px 20px; }
.meta-header { display: flex; justify-content: space-between; font-size: 13px; color: #999; margin-bottom: 12px; }
.image-title { font-size: 20px; font-weight: 700; margin-bottom: 16px; color: #333; }
.dark-mode .image-title { color: #fff; }
.tags-container { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 30px; align-items: center; }
.new-tag-input { display: inline-flex; align-items: center; background-color: #f2f3f5; border-radius: 16px; padding: 4px 8px 4px 12px; height: 28px; }
.dark-mode .new-tag-input { background-color: #3a3a3c; }
.new-tag-input input { border: none; background: transparent; font-size: 12px; width: 60px; color: #333; }
.dark-mode .new-tag-input input { color: #fff; }
.new-tag-input .add-btn { color: #1989fa; margin-left: 4px; cursor: pointer; display: flex;}
.action-bar { display: flex; justify-content: space-between; padding: 0 10px; }
.action-btn { display: flex; flex-direction: column; align-items: center; gap: 8px; cursor: pointer; transition: opacity 0.2s;}
.action-btn:active { opacity: 0.7; }
.icon-circle { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 22px; }
.edit { background: #e8f3ff; color: #1989fa; }
.crop { background: #fff7e6; color: #ff976a; }
.delete { background: #ffebeb; color: #ee0a24; }
.dark-mode .edit { background: rgba(25, 137, 250, 0.15); }
.dark-mode .crop { background: rgba(255, 151, 106, 0.15); }
.dark-mode .delete { background: rgba(238, 10, 36, 0.15); }
.edit-panel { padding: 20px; }
.btn-row { margin-top: 20px; display: flex; gap: 12px; }
.typing-indicator span { animation: blink 1.4s infinite both; font-size: 20px; line-height: 10px; margin: 0 1px;}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0% { opacity: .2; } 20% { opacity: 1; } 100% { opacity: .2; } }
.icon-flip { transform: scaleX(-1); display: inline-block; }
.upload-box { padding: 20px; display: flex; flex-direction: column; align-items: center; }
.hint { margin-top: 12px; font-size: 13px; color: #999; }
.dark-mode .edit-panel :deep(.van-field__label) { color: #e5e5e5 !important; }
.dark-mode .edit-panel :deep(.van-field__control) { color: #ffffff !important; }
.dark-mode .edit-panel :deep(.van-cell) { background-color: #2c2c2e; color: #fff; }
.dark-mode .edit-panel :deep(input::placeholder) { color: #666; }

.chat-uploader, .icon-btn {
  margin-right: 10px;
  display: flex;
  align-items: center;
}

.icon-btn {
  width: 38px;
  height: 38px;
  background: #f7f8fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  border: 1px solid #ebedf0;
  cursor: pointer;
}
.icon-btn:active {
  background: #e0e0e0;
  transform: scale(0.95);
}
.dark-mode .icon-btn {
  background: #2c2c2e;
  border-color: #3a3a3c;
}
.dark-mode .icon-btn .van-icon {
  color: #fff !important;
}

.chat-input-field {
  background: #f7f8fa;
  border-radius: 24px;
  padding: 4px 12px; 
}
.dark-mode .chat-input-field {
  background: #2c2c2e;
}
.chat-user-image {
  margin-bottom: 8px;
  display: flex;
  justify-content: flex-end; 
}

.picker-header {
    padding: 16px;
    font-weight: bold;
    font-size: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
}
.dark-mode .picker-header {
    border-color: #333;
    color: #fff;
}
.picker-content {
    padding: 10px;
    height: calc(100% - 50px);
    overflow-y: auto;
}
.cloud-picker-popup {
    background: #f7f8fa;
}
.dark-mode .cloud-picker-popup {
    background: #1c1c1e;
}

.cropper-dialog {
   width: 90vw !important; 
   max-width: 600px;
   background: #1c1c1e !important; 
   overflow: hidden;
}

.cropper-wrapper-box {
   width: 100%;
   height: 70vh; 
   display: flex;
   flex-direction: column;
}

.editor-stage {
   flex: 1;
   display: flex;
   flex-direction: column;
   height: 100%;
   overflow: hidden;
}

.editor-canvas-area {
   flex: 1; 
   position: relative;
   width: 100%;
   background: #000;
   overflow: hidden;
   min-height: 200px; 
}

.centered-canvas {
   display: flex;
   justify-content: center;
   align-items: center;
   width: 100%;
   height: 100%;
}
.drawing-canvas {
   display: block;
   max-width: 100%;
   max-height: 100%;
}

.editor-toolbar {
   flex-shrink: 0; 
   background: #1c1c1e;
   padding: 16px;
   border-top: 1px solid rgba(255,255,255,0.1);
   z-index: 10;
}

.scrollable-tools {
   max-height: 40vh;
   overflow-y: auto;
}

.tool-row {
   display: flex;
   justify-content: space-between;
   margin-bottom: 16px;
}
.tool-section {
   margin-bottom: 20px;
   padding-bottom: 10px;
   border-bottom: 1px solid rgba(255,255,255,0.05);
}
.section-title {
   color: #fff;
   font-size: 14px;
   margin-bottom: 10px;
   display: flex;
   justify-content: space-between;
   align-items: center;
}
.slider-row {
   display: flex;
   align-items: center;
   margin-bottom: 12px;
}
.slider-row .label {
   width: 40px;
   color: #999;
   font-size: 12px;
}
.slider-row .van-slider {
   flex: 1;
   margin: 0 10px;
}
.custom-button {
   width: 26px;
   color: #fff;
   font-size: 10px;
   line-height: 18px;
   text-align: center;
   background-color: #1989fa;
   border-radius: 100px;
}
.action-row {
   display: flex;
   justify-content: space-between;
   margin-top: 10px;
}
</style>

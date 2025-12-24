import { createApp } from 'vue'
import Vant from 'vant'

// 引入 Vant 的样式文件 (非常重要，否则组件没有颜色)
import 'vant/lib/index.css'

import './style.css'
import App from './App.vue'

const app = createApp(App)

// 启用 Vant
app.use(Vant)

app.mount('#app')

import { createApp } from 'vue'
import Vant from 'vant'
import 'vant/lib/index.css'
import './style.css'
import App from './App.vue'
import router from './router' // 新增

const app = createApp(App)
app.use(Vant)
app.use(router) // 新增
app.mount('#app')

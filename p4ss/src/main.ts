import { createApp } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import ElementPlus from 'element-plus'
// @ts-ignore
import locale from 'element-plus/dist/locale/zh-cn'
import * as ElementPlusIcons from '@element-plus/icons-vue'
import store from './store'
import router from './router'
import App from './App.vue'
import './tailwindcss.scss'
import './element.scss'

dayjs.locale('zh-cn')

const app = createApp(App)
app.use(store)
app.use(router)
app.use(ElementPlus, { locale, size: 'default' })
app.mount('#app')

for (const [name, component] of Object.entries(ElementPlusIcons)) {
  app.component(name, component)
}

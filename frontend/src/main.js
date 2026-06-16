import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import {
  Aim,
  Bell,
  Calendar,
  Check,
  DataAnalysis,
  Edit,
  Lock,
  Medal,
  Plus,
  Refresh,
  SwitchButton,
  User
} from '@element-plus/icons-vue'
import App from './App.vue'
import './assets/styles.css'

const app = createApp(App)
app.use(ElementPlus)
for (const icon of [Aim, Bell, Calendar, Check, DataAnalysis, Edit, Lock, Medal, Plus, Refresh, SwitchButton, User]) {
  app.component(icon.name, icon)
}
app.mount('#app')

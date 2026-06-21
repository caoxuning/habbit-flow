import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('habitflow_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    // 导出等二进制流请求跳过拦截器
    if (response.config.__skipIntercept) {
      return response.data
    }
    const body = response.data
    if (body.code !== 200) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return body.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络异常'
    ElMessage.error(message)
    if (error.response?.status === 401 || error.response?.data?.code === 401) {
      localStorage.removeItem('habitflow_token')
      localStorage.removeItem('habitflow_profile')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export default http

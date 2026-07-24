import axios, { AxiosInstance } from 'axios'

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 技能相关API
export const skillAPI = {
  list: (category?: string) => 
    apiClient.get('/pipeline/skills', { params: { category } }),
  
  execute: (skillName: string, inputs: Record<string, any>, config: Record<string, any> = {}) =>
    apiClient.post('/pipeline/skills/execute', { skill_name: skillName, inputs, config })
}

// 流水线相关API
export const pipelineAPI = {
  create: (data: any) => apiClient.post('/pipeline/create', data),
  execute: (pipelineId: string, context: Record<string, any> = {}) =>
    apiClient.post('/pipeline/execute', { pipeline_id: pipelineId, context }),
  status: (executionId: string) => apiClient.get(`/pipeline/status/${executionId}`),
  quickGenerate: (topic: string, style: string, duration: number) =>
    apiClient.post('/pipeline/quick/generate-video', { topic, style, duration })
}

// 模型相关API
export const modelAPI = {
  list: () => apiClient.get('/pipeline/models'),
  chat: (messages: any[], model?: string) =>
    apiClient.post('/pipeline/models/chat', { messages, model })
}

// 健康检查
export const healthAPI = {
  check: () => apiClient.get('/health')
}

export default apiClient

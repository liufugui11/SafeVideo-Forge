<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card">
          <el-icon :size="32" :color="stat.color">
            <component :is="stat.icon" />
          </el-icon>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-title">{{ stat.title }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🚀 快速开始</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" size="large" @click="createProject">
              <el-icon><VideoCamera /></el-icon>
              创建视频项目
            </el-button>
            <el-button size="large" @click="analyzeVideo">
              <el-icon><DataAnalysis /></el-icon>
              解析现有视频
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📊 系统状态</span>
            </div>
          </template>
          <div class="system-status">
            <div class="status-item">
              <span>后端服务</span>
              <el-tag type="success" v-if="backendOk">运行中</el-tag>
              <el-tag type="danger" v-else>未启动</el-tag>
            </div>
            <div class="status-item">
              <span>已加载技能</span>
              <el-tag>{{ skillCount }} 个</el-tag>
            </div>
            <div class="status-item">
              <span>已配置模型</span>
              <el-tag>{{ modelCount }} 个</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row class="mt-4">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📖 使用指南</span>
            </div>
          </template>
          <el-steps :active="1" finish-status="success">
            <el-step title="输入主题" description="输入安全生产主题或关键词" />
            <el-step title="选择技能" description="从技能库选择所需功能模块" />
            <el-step title="配置参数" description="调整各技能的配置参数" />
            <el-step title="执行流水线" description="一键生成完整视频" />
            <el-step title="质检发布" description="质量检测后发布到视频号" />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { healthAPI, skillAPI, modelAPI } from '@/api'

const router = useRouter()
const backendOk = ref(false)
const skillCount = ref(0)
const modelCount = ref(0)

const stats = ref([
  { title: '本月生成', value: '0', icon: 'VideoPlay', color: '#409eff' },
  { title: '技能数量', value: '0', icon: 'MagicStick', color: '#67c23a' },
  { title: '解析视频', value: '0', icon: 'DataAnalysis', color: '#e6a23c' },
  { title: '项目总数', value: '0', icon: 'FolderOpened', color: '#f56c6c' }
])

const createProject = () => {
  router.push('/pipeline')
}

const analyzeVideo = () => {
  router.push('/analyzer')
}

onMounted(async () => {
  try {
    await healthAPI.check()
    backendOk.value = true
    
    const skillsRes = await skillAPI.list()
    skillCount.value = skillsRes.total || 0
    stats.value[1].value = String(skillCount.value)
    
    const modelsRes = await modelAPI.list()
    modelCount.value = modelsRes.models?.length || 0
  } catch (e) {
    console.warn('后端连接失败，部分功能不可用')
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  .stat-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    
    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: var(--text-primary);
      }
      
      .stat-title {
        font-size: 14px;
        color: var(--text-secondary);
        margin-top: 4px;
      }
    }
  }
  
  .mt-4 {
    margin-top: 20px;
  }
  
  .quick-actions {
    display: flex;
    gap: 16px;
    padding: 20px 0;
  }
  
  .system-status {
    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid var(--border-color);
      
      &:last-child {
        border-bottom: none;
      }
    }
  }
  
  .card-header {
    font-weight: 600;
    font-size: 16px;
  }
}
</style>

<template>
  <div class="pipeline-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🎬 视频生成流水线</span>
          <el-button type="primary" @click="runPipeline">
            <el-icon><VideoPlay /></el-icon>
            执行流水线
          </el-button>
        </div>
      </template>
      
      <el-steps :active="activeStep" finish-status="success" simple>
        <el-step title="文案生成" />
        <el-step title="脚本拆分" />
        <el-step title="画面生成" />
        <el-step title="语音合成" />
        <el-step title="视频合成" />
        <el-step title="质检" />
        <el-step title="分发" />
      </el-steps>
      
      <div class="pipeline-config mt-4">
        <el-form :model="form" label-width="120px">
          <el-form-item label="视频主题">
            <el-input v-model="form.topic" placeholder="输入安全生产主题，如：高空作业安全" />
          </el-form-item>
          <el-form-item label="视频风格">
            <el-select v-model="form.style" placeholder="选择风格">
              <el-option label="警示教育" value="警示" />
              <el-option label="科普知识" value="科普" />
              <el-option label="真实案例" value="案例" />
              <el-option label="操作规程" value="规程" />
            </el-select>
          </el-form-item>
          <el-form-item label="视频时长">
            <el-slider v-model="form.duration" :min="15" :max="180" :step="5" show-stops />
            <span class="duration-label">{{ form.duration }} 秒</span>
          </el-form-item>
          <el-form-item label="目标受众">
            <el-radio-group v-model="form.audience">
              <el-radio label="一线工人">一线工人</el-radio>
              <el-radio label="管理人员">管理人员</el-radio>
              <el-radio label="全员">全员</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
      
      <el-divider />
      
      <div class="pipeline-nodes">
        <h4>流水线节点配置</h4>
        <el-timeline>
          <el-timeline-item
            v-for="node in pipelineNodes"
            :key="node.id"
            :type="node.status === 'active' ? 'primary' : 'info'"
            :icon="node.icon"
          >
            <el-card class="node-card">
              <div class="node-header">
                <span class="node-name">{{ node.name }}</span>
                <el-tag size="small" :type="node.status === 'completed' ? 'success' : 'info'">
                  {{ node.statusText }}
                </el-tag>
              </div>
              <div class="node-desc">{{ node.description }}</div>
              <el-progress v-if="node.progress > 0" :percentage="node.progress" />
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { pipelineAPI } from '@/api'

const activeStep = ref(0)

const form = reactive({
  topic: '',
  style: '警示',
  duration: 60,
  audience: '一线工人'
})

const pipelineNodes = ref([
  { id: 'script', name: '文案生成器', icon: 'Document', description: '根据主题自动生成安全生产文案', status: 'pending', statusText: '待执行', progress: 0 },
  { id: 'split', name: '脚本拆分器', icon: 'Scissor', description: '将文案拆分为结构化分镜', status: 'pending', statusText: '待执行', progress: 0 },
  { id: 'visual', name: '画面生成器', icon: 'Picture', description: '调用AI生成画面素材', status: 'pending', statusText: '待执行', progress: 0 },
  { id: 'tts', name: '语音合成器', icon: 'Microphone', description: '生成旁白配音', status: 'pending', statusText: '待执行', progress: 0 },
  { id: 'compose', name: '视频合成器', icon: 'Film', description: '合成最终视频', status: 'pending', statusText: '待执行', progress: 0 },
  { id: 'quality', name: '质量检测器', icon: 'CircleCheck', description: '检查视频质量', status: 'pending', statusText: '待执行', progress: 0 }
])

const runPipeline = async () => {
  if (!form.topic) {
    ElMessage.warning('请输入视频主题')
    return
  }
  
  try {
    activeStep.value = 1
    const res = await pipelineAPI.quickGenerate(form.topic, form.style, form.duration)
    ElMessage.success('流水线已启动')
    console.log(res)
  } catch (e) {
    ElMessage.error('流水线启动失败')
  }
}
</script>

<style scoped lang="scss">
.pipeline-view {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
  
  .duration-label {
    margin-left: 16px;
    color: var(--text-secondary);
  }
  
  .pipeline-nodes {
    margin-top: 20px;
    
    h4 {
      margin-bottom: 16px;
    }
    
    .node-card {
      .node-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        
        .node-name {
          font-weight: 600;
        }
      }
      
      .node-desc {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 12px;
      }
    }
  }
}
</style>

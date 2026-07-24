<template>
  <div class="analyzer-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔍 视频解析分析</span>
        </div>
      </template>
      
      <el-upload
        class="upload-area"
        drag
        action="/api/v1/upload"
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".mp4,.mov,.avi,.mkv"
      >
        <el-icon class="el-icon--upload" size="60"><Upload /></el-icon>
        <div class="el-upload__text">
          拖拽视频文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持格式: MP4, MOV, AVI, MKV | 最大 500MB
          </div>
        </template>
      </el-upload>
      
      <el-divider v-if="analyzing || analysisResult" />
      
      <div v-if="analyzing" class="analyzing">
        <el-progress :percentage="analysisProgress" :status="analysisProgress === 100 ? 'success' : ''" />
        <p>正在分析视频中...</p>
      </div>
      
      <div v-if="analysisResult" class="analysis-result">
        <el-descriptions title="📊 分析报告" :column="2" border>
          <el-descriptions-item label="语言风格">
            {{ analysisResult.language_style || '分析中...' }}
          </el-descriptions-item>
          <el-descriptions-item label="画面风格">
            {{ analysisResult.visual_style || '分析中...' }}
          </el-descriptions-item>
          <el-descriptions-item label="视觉冲击力">
            <el-rate :model-value="analysisResult.impact_score || 0" disabled show-score />
          </el-descriptions-item>
          <el-descriptions-item label="信息密度">
            {{ analysisResult.info_density || '中等' }}
          </el-descriptions-item>
          <el-descriptions-item label="专业度评级">
            <el-tag :type="getRatingType(analysisResult.professional_rating)">
              {{ analysisResult.professional_rating || 'B' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="完播率预测">
            {{ analysisResult.completion_rate || '65%' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider />
        
        <h4>💡 优化建议</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(suggestion, index) in analysisResult.suggestions"
            :key="index"
            type="primary"
          >
            {{ suggestion }}
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const analyzing = ref(false)
const analysisProgress = ref(0)
const analysisResult = ref<any>(null)

const handleFileChange = (file: any) => {
  ElMessage.success(`已选择文件: ${file.name}`)
  startAnalysis()
}

const startAnalysis = () => {
  analyzing.value = true
  analysisProgress.value = 0
  
  // 模拟分析过程
  const interval = setInterval(() => {
    analysisProgress.value += 10
    if (analysisProgress.value >= 100) {
      clearInterval(interval)
      analyzing.value = false
      analysisResult.value = {
        language_style: '警示性强，节奏紧凑，适合短视频传播',
        visual_style: '工业写实风格，色调偏冷，构图稳定',
        impact_score: 4.2,
        info_density: '高',
        professional_rating: 'A-',
        completion_rate: '72%',
        suggestions: [
          '建议在前3秒增加更强烈的视觉冲击（Hook）',
          '画面转场可以更加流畅，减少硬切',
          '背景音乐音量建议降低至15%以下',
          '字幕字体建议增大，提高可读性',
          '结尾可添加明确的行动号召（CTA）'
        ]
      }
    }
  }, 500)
}

const getRatingType = (rating: string) => {
  if (!rating) return 'info'
  if (rating.startsWith('A')) return 'success'
  if (rating.startsWith('B')) return 'warning'
  return 'danger'
}
</script>

<style scoped lang="scss">
.analyzer-view {
  .upload-area {
    :deep(.el-upload-dragger) {
      background-color: var(--bg-secondary);
      border-color: var(--border-color);
      
      &:hover {
        border-color: var(--primary-color);
      }
    }
  }
  
  .analyzing {
    text-align: center;
    padding: 40px;
  }
  
  .analysis-result {
    padding: 20px 0;
  }
}
</style>

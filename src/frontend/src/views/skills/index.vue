<template>
  <div class="skills-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🧩 技能库 (SKII)</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索技能..."
            prefix-icon="Search"
            clearable
            style="width: 300px"
          />
        </div>
      </template>
      
      <el-tabs v-model="activeCategory">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="内容生成" name="content" />
        <el-tab-pane label="视觉生成" name="visual" />
        <el-tab-pane label="音频处理" name="audio" />
        <el-tab-pane label="视频编辑" name="edit" />
        <el-tab-pane label="视频分析" name="analyze" />
        <el-tab-pane label="质量检测" name="quality" />
      </el-tabs>
      
      <el-row :gutter="16">
        <el-col :span="8" v-for="skill in filteredSkills" :key="skill.name">
          <el-card class="skill-card" shadow="hover">
            <div class="skill-header">
              <el-icon size="24"><MagicStick /></el-icon>
              <div class="skill-info">
                <div class="skill-name">{{ skill.name }}</div>
                <el-tag size="small" type="info">{{ skill.category }}</el-tag>
              </div>
            </div>
            <div class="skill-desc">{{ skill.description }}</div>
            <div class="skill-meta">
              <span>v{{ skill.version }}</span>
              <span>作者: {{ skill.author || '系统' }}</span>
            </div>
            <div class="skill-actions">
              <el-button type="primary" size="small" @click="executeSkill(skill)">
                执行
              </el-button>
              <el-button size="small" @click="viewDetails(skill)">
                详情
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { skillAPI } from '@/api'

const searchQuery = ref('')
const activeCategory = ref('all')
const skills = ref<any[]>([])

const filteredSkills = computed(() => {
  let result = skills.value
  
  if (activeCategory.value !== 'all') {
    result = result.filter(s => s.category === activeCategory.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(s => 
      s.name.toLowerCase().includes(query) ||
      s.description?.toLowerCase().includes(query)
    )
  }
  
  return result
})

const executeSkill = (skill: any) => {
  ElMessage.info(`准备执行技能: ${skill.name}`)
}

const viewDetails = (skill: any) => {
  console.log('Skill details:', skill)
}

onMounted(async () => {
  try {
    const res = await skillAPI.list()
    skills.value = res.skills || []
  } catch (e) {
    // 使用模拟数据
    skills.value = [
      { name: '文案生成器', category: 'content', version: '1.0.0', description: '根据关键词自动生成安全生产文案' },
      { name: '脚本拆分器', category: 'content', version: '1.0.0', description: '将文案拆分为结构化分镜脚本' },
      { name: '画面提示词生成器', category: 'visual', version: '1.0.0', description: '生成AI绘图/视频提示词' },
      { name: '画面生成器', category: 'visual', version: '1.0.0', description: '调用AI模型生成画面素材' },
      { name: '语音合成器', category: 'audio', version: '1.0.0', description: '自动生成旁白配音' },
      { name: '视频合成器', category: 'edit', version: '1.0.0', description: '合成最终视频' },
      { name: '视频解析器', category: 'analyze', version: '1.0.0', description: '全面解析视频各维度' },
      { name: '质量检测器', category: 'quality', version: '1.0.0', description: '自动检查视频质量' }
    ]
  }
})
</script>

<style scoped lang="scss">
.skills-view {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
  
  .skill-card {
    margin-bottom: 16px;
    
    .skill-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 12px;
      
      .skill-info {
        .skill-name {
          font-weight: 600;
          font-size: 15px;
          margin-bottom: 4px;
        }
      }
    }
    
    .skill-desc {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 12px;
      min-height: 40px;
    }
    
    .skill-meta {
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 12px;
    }
    
    .skill-actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>

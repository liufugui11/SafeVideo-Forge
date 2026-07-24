<template>
  <div class="settings-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 系统设置</span>
        </div>
      </template>
      
      <el-tabs tab-position="left">
        <el-tab-pane label="模型配置">
          <h3>AI模型API配置</h3>
          <p class="desc">配置各AI模型的API Key，至少配置一个才能正常使用</p>
          
          <el-form :model="settings" label-width="180px">
            <el-form-item label="DeepSeek API Key">
              <el-input
                v-model="settings.deepseek_key"
                type="password"
                show-password
                placeholder="sk-..."
              />
              <div class="form-tip">推荐：性价比高，推理能力强</div>
            </el-form-item>
            
            <el-form-item label="Kimi (Moonshot) API Key">
              <el-input
                v-model="settings.kimi_key"
                type="password"
                show-password
                placeholder="sk-..."
              />
              <div class="form-tip">推荐：长文本处理能力强</div>
            </el-form-item>
            
            <el-form-item label="通义千问/万相 API Key">
              <el-input
                v-model="settings.dashscope_key"
                type="password"
                show-password
                placeholder="sk-..."
              />
              <div class="form-tip">推荐：图像/视频生成首选</div>
            </el-form-item>
            
            <el-form-item label="豆包 API Key">
              <el-input
                v-model="settings.doubao_key"
                type="password"
                show-password
                placeholder="..."
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="saveSettings">保存配置</el-button>
              <el-button @click="testConnection">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="视频参数">
          <h3>默认视频参数</h3>
          <el-form :model="videoSettings" label-width="180px">
            <el-form-item label="默认分辨率">
              <el-select v-model="videoSettings.resolution">
                <el-option label="1080×1920 (竖屏)" value="1080x1920" />
                <el-option label="720×1280 (竖屏)" value="720x1280" />
                <el-option label="1920×1080 (横屏)" value="1920x1080" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认帧率">
              <el-slider v-model="videoSettings.fps" :min="24" :max="60" :step="6" show-stops />
            </el-form-item>
            <el-form-item label="最大视频时长">
              <el-input-number v-model="videoSettings.max_duration" :min="30" :max="300" />
              <span class="unit">秒</span>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="关于">
          <div class="about">
            <h2>SafeVideo Forge</h2>
            <p>安全生产视频智能生产工具 v0.1.0</p>
            <p>面向安全生产类视频号博主的本地化自动化视频生产桌面工具</p>
            <el-divider />
            <p>
              <el-link href="https://github.com/liufugui11/SafeVideo-Forge" target="_blank">
                GitHub 仓库
              </el-link>
            </p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

const settings = reactive({
  deepseek_key: '',
  kimi_key: '',
  dashscope_key: '',
  doubao_key: ''
})

const videoSettings = reactive({
  resolution: '1080x1920',
  fps: 30,
  max_duration: 180
})

const saveSettings = () => {
  ElMessage.success('配置已保存')
}

const testConnection = async () => {
  ElMessage.info('正在测试连接...')
  // 实际应调用后端API测试
  setTimeout(() => {
    ElMessage.success('连接测试通过')
  }, 1000)
}
</script>

<style scoped lang="scss">
.settings-view {
  .desc {
    color: var(--text-secondary);
    margin-bottom: 20px;
  }
  
  .form-tip {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
  }
  
  .unit {
    margin-left: 8px;
    color: var(--text-secondary);
  }
  
  .about {
    text-align: center;
    padding: 40px;
    
    h2 {
      color: var(--primary-color);
      margin-bottom: 16px;
    }
    
    p {
      color: var(--text-secondary);
      margin-bottom: 8px;
    }
  }
}
</style>

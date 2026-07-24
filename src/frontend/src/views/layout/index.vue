<template>
  <el-container class="layout-container">
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <el-icon size="28" color="#409eff"><VideoPlay /></el-icon>
        <span class="logo-text">SafeVideo</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#16213e"
        text-color="#a0a0a0"
        active-text-color="#409eff"
        class="sidebar-menu"
      >
        <el-menu-item v-for="route in menuRoutes" :key="route.path" :index="route.path">
          <el-icon>
            <component :is="route.meta?.icon" />
          </el-icon>
          <span>{{ route.meta?.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>{{ pageTitle }}</h2>
        </div>
        <div class="header-right">
          <el-tag type="success" v-if="backendConnected">后端已连接</el-tag>
          <el-tag type="danger" v-else>后端未连接</el-tag>
          <el-button circle @click="goToSettings">
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { healthAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const backendConnected = ref(false)

const menuRoutes = computed(() => {
  const layout = router.getRoutes().find(r => r.name === 'Layout')
  return layout?.children || []
})

const pageTitle = computed(() => {
  return route.meta?.title || 'SafeVideo Forge'
})

const goToSettings = () => {
  router.push('/settings')
}

// 检查后端连接
onMounted(async () => {
  try {
    await healthAPI.check()
    backendConnected.value = true
  } catch {
    backendConnected.value = false
  }
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  
  .sidebar {
    background-color: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    
    .logo {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      border-bottom: 1px solid var(--border-color);
      
      .logo-text {
        font-size: 18px;
        font-weight: 600;
        color: var(--primary-color);
      }
    }
    
    .sidebar-menu {
      border-right: none;
    }
  }
  
  .header {
    background-color: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }
  
  .main-content {
    background-color: var(--bg-primary);
    padding: 20px;
    overflow-y: auto;
  }
}
</style>

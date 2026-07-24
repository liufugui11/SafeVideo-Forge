import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '工作台', icon: 'HomeFilled' }
      },
      {
        path: 'pipeline',
        name: 'Pipeline',
        component: () => import('@/views/pipeline/index.vue'),
        meta: { title: '流水线', icon: 'VideoPlay' }
      },
      {
        path: 'skills',
        name: 'Skills',
        component: () => import('@/views/skills/index.vue'),
        meta: { title: '技能库', icon: 'MagicStick' }
      },
      {
        path: 'analyzer',
        name: 'Analyzer',
        component: () => import('@/views/analyzer/index.vue'),
        meta: { title: '视频解析', icon: 'DataAnalysis' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/projects/index.vue'),
        meta: { title: '项目管理', icon: 'FolderOpened' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/index.vue'),
        meta: { title: '设置', icon: 'Setting' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

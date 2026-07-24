<template>
  <div class="projects-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📁 项目管理</span>
          <el-button type="primary">
            <el-icon><Plus /></el-icon>
            新建项目
          </el-button>
        </div>
      </template>
      
      <el-empty description="暂无项目，点击右上角创建">
        <el-button type="primary">创建第一个项目</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.projects-view {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}
</style>

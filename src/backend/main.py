"""
SafeVideo Forge - 后端主入口
安全生产视频智能生产工具后端服务
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.router import api_router
from app.core.database import init_db
from app.core.pipeline.engine import PipelineEngine
from app.skills.registry import SkillRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("🚀 SafeVideo Forge 后端服务启动中...")
    
    # 初始化数据库
    await init_db()
    
    # 初始化技能注册表
    app.state.skill_registry = SkillRegistry()
    await app.state.skill_registry.load_skills()
    
    # 初始化流水线引擎
    app.state.pipeline_engine = PipelineEngine()
    
    logger.info("✅ 所有核心组件初始化完成")
    yield
    
    # 关闭
    logger.info("🛑 后端服务关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="SafeVideo Forge API",
    description="安全生产视频智能生产工具后端API",
    version="0.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "service": "SafeVideo Forge"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

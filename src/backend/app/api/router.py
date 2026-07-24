"""
API路由聚合
"""

from fastapi import APIRouter
from app.api.pipeline import router as pipeline_router

api_router = APIRouter()

api_router.include_router(pipeline_router, prefix="/pipeline")

# 健康检查在main.py中直接注册

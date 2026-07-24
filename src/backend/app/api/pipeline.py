"""
API路由 - 核心接口
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from app.core.pipeline.engine import PipelineDefinition, PipelineNode, PipelineEngine
from app.skills.base import SkillCategory
from app.core.ai.router import model_router

router = APIRouter(prefix="/pipeline", tags=["流水线"])


# ========== 请求/响应模型 ==========

class PipelineCreateRequest(BaseModel):
    name: str
    description: str = ""
    nodes: List[Dict[str, Any]]
    connections: List[Dict[str, str]]  # [{"from": "node1", "to": "node2"}]
    global_config: Dict[str, Any] = Field(default_factory=dict)


class PipelineExecuteRequest(BaseModel):
    pipeline_id: str
    context: Dict[str, Any] = Field(default_factory=dict)


class SkillExecuteRequest(BaseModel):
    skill_name: str
    inputs: Dict[str, Any]
    config: Dict[str, Any] = Field(default_factory=dict)


# ========== 流水线接口 ==========

@router.post("/create")
async def create_pipeline(request: PipelineCreateRequest):
    """创建流水线定义"""
    try:
        # 构建节点
        nodes = {}
        for node_data in request.nodes:
            node = PipelineNode(
                id=node_data["id"],
                skill_name=node_data["skill_name"],
                config=node_data.get("config", {}),
                inputs_mapping=node_data.get("inputs_mapping", {}),
                outputs_mapping=node_data.get("outputs_mapping", {})
            )
            nodes[node.id] = node
        
        # 构建流水线
        definition = PipelineDefinition(
            id="",  # 自动生成
            name=request.name,
            description=request.description,
            nodes=nodes,
            global_config=request.global_config
        )
        
        # 连接节点
        for conn in request.connections:
            definition.connect(conn["from"], conn["to"])
        
        # 验证
        error = definition.validate()
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        return {
            "success": True,
            "pipeline_id": definition.id,
            "execution_order": definition.get_execution_order()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_pipeline(request: PipelineExecuteRequest):
    """执行流水线"""
    # 这里需要从存储中加载流水线定义
    # 简化实现：直接返回提示
    return {
        "success": True,
        "message": "流水线执行已提交",
        "execution_id": "demo_execution_id"
    }


@router.get("/status/{execution_id}")
async def get_execution_status(execution_id: str):
    """获取执行状态"""
    return {
        "execution_id": execution_id,
        "status": "running",
        "progress": 0.5,
        "nodes": {}
    }


# ========== 技能接口 ==========

@router.get("/skills")
async def list_skills(category: Optional[str] = None):
    """列出所有可用技能"""
    from app.main import app
    registry = app.state.skill_registry
    
    cat = SkillCategory(category) if category else None
    skills = registry.list_skills(category=cat)
    
    return {
        "skills": skills,
        "categories": registry.get_categories(),
        "total": len(skills)
    }


@router.post("/skills/execute")
async def execute_skill(request: SkillExecuteRequest):
    """直接执行单个技能"""
    from app.main import app
    from app.skills.base import SkillContext
    
    registry = app.state.skill_registry
    skill_class = registry.get(request.skill_name)
    
    if not skill_class:
        raise HTTPException(status_code=404, detail=f"技能 '{request.skill_name}' 不存在")
    
    skill = skill_class(request.config)
    context = SkillContext(
        project_id="direct_execution",
        inputs=request.inputs
    )
    
    result = await skill.execute(context)
    
    return {
        "success": result.success,
        "data": result.data,
        "message": result.message,
        "error": result.error
    }


# ========== 模型接口 ==========

@router.get("/models")
async def list_models():
    """列出所有可用AI模型"""
    return {
        "models": model_router.list_available_models(),
        "recommendations": {
            "text_generation": model_router.get_recommendation("text_generation"),
            "script_writing": model_router.get_recommendation("script_writing"),
            "image_generation": model_router.get_recommendation("image_generation"),
            "video_generation": model_router.get_recommendation("video_generation"),
        }
    }


@router.post("/models/chat")
async def chat_completion(request: Dict[str, Any]):
    """通用对话接口"""
    messages = request.get("messages", [])
    model = request.get("model")
    
    try:
        response = await model_router.chat(messages, model=model)
        return {"success": True, "content": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 快捷流水线 ==========

@router.post("/quick/generate-video")
async def quick_generate_video(request: Dict[str, Any]):
    """一键生成视频 - 完整流水线"""
    topic = request.get("topic", "安全生产")
    style = request.get("style", "警示")
    duration = request.get("duration", 60)
    
    # 构建完整流水线
    definition = PipelineDefinition(
        id="",
        name=f"自动生成: {topic}",
        description="从文案到视频的完整自动化流水线"
    )
    
    # 节点1: 文案生成
    node_script = PipelineNode(
        id="script_gen",
        skill_name="文案生成器",
        inputs_mapping={"topic": "context.topic", "style": "context.style", "duration": "context.duration"},
        outputs_mapping={"script": "script", "title": "title", "hashtags": "hashtags"}
    )
    definition.add_node(node_script)
    
    # 节点2: 脚本拆分
    node_split = PipelineNode(
        id="script_split",
        skill_name="脚本拆分器",
        inputs_mapping={"script": "node.script_gen.script", "duration": "context.duration"},
        outputs_mapping={"storyboard": "storyboard", "total_scenes": "total_scenes"}
    )
    definition.add_node(node_split)
    definition.connect("script_gen", "script_split")
    
    return {
        "success": True,
        "message": "流水线已创建，请在桌面端执行",
        "pipeline": {
            "id": definition.id,
            "name": definition.name,
            "nodes": list(definition.nodes.keys())
        }
    }

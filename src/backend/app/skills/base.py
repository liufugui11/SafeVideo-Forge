"""
技能库系统 (SKII - Skill Interface & Implementation)
基于插件化架构的可复用技能系统
"""

import asyncio
import importlib
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Callable
from loguru import logger


class SkillCategory(str, Enum):
    """技能分类"""
    CONTENT = "content"          # 内容生成
    VISUAL = "visual"            # 视觉生成
    AUDIO = "audio"              # 音频处理
    EDIT = "edit"                # 视频编辑
    ANALYZE = "analyze"          # 视频分析
    QUALITY = "quality"          # 质量检测
    PUBLISH = "publish"          # 发布分发
    UTILITY = "utility"          # 通用工具


class SkillStatus(str, Enum):
    """技能状态"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillContext:
    """技能执行上下文"""
    project_id: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.inputs.get(key, default)
    
    def set_output(self, key: str, value: Any):
        self.outputs[key] = value


@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def ok(cls, data: Any = None, message: str = "") -> "SkillResult":
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def fail(cls, error: str, message: str = "") -> "SkillResult":
        return cls(success=False, error=error, message=message)


class BaseSkill(ABC):
    """技能基类"""
    
    # 技能元数据 (子类必须覆盖)
    name: str = ""
    category: SkillCategory = SkillCategory.UTILITY
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    
    # 输入输出定义
    inputs: Dict[str, type] = {}
    outputs: Dict[str, type] = {}
    
    # 配置项定义
    config_schema: Dict[str, Any] = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.status = SkillStatus.IDLE
        self.progress = 0.0
        self._cancelled = False
    
    @abstractmethod
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行技能"""
        pass
    
    async def validate_inputs(self, context: SkillContext) -> Optional[str]:
        """验证输入参数"""
        for key, expected_type in self.inputs.items():
            if key not in context.inputs:
                return f"缺少必需参数: {key}"
            if not isinstance(context.inputs[key], expected_type):
                return f"参数类型错误: {key} 期望 {expected_type.__name__}"
        return None
    
    def update_progress(self, progress: float):
        """更新进度 (0.0 - 1.0)"""
        self.progress = min(max(progress, 0.0), 1.0)
    
    def cancel(self):
        """取消执行"""
        self._cancelled = True
        self.status = SkillStatus.CANCELLED
    
    def is_cancelled(self) -> bool:
        return self._cancelled
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "name": self.name,
            "category": self.category.value,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "inputs": {k: v.__name__ for k, v in self.inputs.items()},
            "outputs": {k: v.__name__ for k, v in self.outputs.items()},
            "config_schema": self.config_schema,
            "status": self.status.value,
            "progress": self.progress
        }


def skill(
    name: str,
    category: SkillCategory = SkillCategory.UTILITY,
    version: str = "1.0.0",
    description: str = "",
    author: str = "",
    inputs: Optional[Dict[str, type]] = None,
    outputs: Optional[Dict[str, type]] = None,
    config_schema: Optional[Dict[str, Any]] = None
):
    """技能装饰器"""
    def decorator(cls: Type[BaseSkill]) -> Type[BaseSkill]:
        cls.name = name
        cls.category = category
        cls.version = version
        cls.description = description
        cls.author = author
        cls.inputs = inputs or {}
        cls.outputs = outputs or {}
        cls.config_schema = config_schema or {}
        return cls
    return decorator


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self):
        self._skills: Dict[str, Type[BaseSkill]] = {}
        self._instances: Dict[str, BaseSkill] = {}
    
    def register(self, skill_class: Type[BaseSkill]) -> None:
        """注册技能"""
        if not issubclass(skill_class, BaseSkill):
            raise ValueError(f"{skill_class} 不是 BaseSkill 的子类")
        
        skill_name = skill_class.name
        if not skill_name:
            raise ValueError("技能名称不能为空")
        
        self._skills[skill_name] = skill_class
        logger.info(f"✅ 技能已注册: {skill_name} v{skill_class.version}")
    
    def unregister(self, skill_name: str) -> None:
        """注销技能"""
        if skill_name in self._skills:
            del self._skills[skill_name]
            self._instances.pop(skill_name, None)
            logger.info(f"🗑️ 技能已注销: {skill_name}")
    
    def get(self, skill_name: str) -> Optional[Type[BaseSkill]]:
        """获取技能类"""
        return self._skills.get(skill_name)
    
    def create_instance(self, skill_name: str, config: Optional[Dict] = None) -> Optional[BaseSkill]:
        """创建技能实例"""
        skill_class = self._skills.get(skill_name)
        if not skill_class:
            return None
        return skill_class(config)
    
    def list_skills(self, category: Optional[SkillCategory] = None) -> List[Dict[str, Any]]:
        """列出所有技能"""
        skills = []
        for name, skill_class in self._skills.items():
            if category and skill_class.category != category:
                continue
            # 创建临时实例获取元数据
            instance = skill_class()
            skills.append(instance.to_dict())
        return skills
    
    def get_categories(self) -> List[str]:
        """获取所有技能分类"""
        categories = set()
        for skill_class in self._skills.values():
            categories.add(skill_class.category.value)
        return sorted(list(categories))
    
    async def load_skills(self, skills_dir: Optional[Path] = None) -> None:
        """从目录加载技能模块"""
        if skills_dir is None:
            skills_dir = Path(__file__).parent / "builtin"
        
        if not skills_dir.exists():
            logger.warning(f"技能目录不存在: {skills_dir}")
            return
        
        logger.info(f"📂 正在加载技能模块: {skills_dir}")
        
        for file_path in skills_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                module_name = f"app.skills.builtin.{file_path.stem}"
                module = importlib.import_module(module_name)
                
                # 自动注册所有BaseSkill子类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseSkill) and 
                        obj is not BaseSkill and
                        obj.name):  # 确保已设置name
                        self.register(obj)
                        
            except Exception as e:
                logger.error(f"❌ 加载技能模块失败 {file_path}: {e}")
        
        logger.info(f"📊 共加载 {len(self._skills)} 个技能")
    
    def __contains__(self, skill_name: str) -> bool:
        return skill_name in self._skills
    
    def __len__(self) -> int:
        return len(self._skills)


# 全局注册表实例
skill_registry = SkillRegistry()

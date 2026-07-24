"""
流水线引擎 - 基于DAG的任务调度系统
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Callable
from loguru import logger

from app.skills.base import BaseSkill, SkillContext, SkillResult, SkillStatus, skill_registry


class PipelineStatus(str, Enum):
    """流水线状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """节点状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class PipelineNode:
    """流水线节点"""
    id: str
    skill_name: str
    config: Dict[str, Any] = field(default_factory=dict)
    inputs_mapping: Dict[str, str] = field(default_factory=dict)  # 输入映射: {参数名: 来源}
    outputs_mapping: Dict[str, str] = field(default_factory=dict)  # 输出映射
    
    # 执行状态
    status: NodeStatus = NodeStatus.PENDING
    result: Optional[SkillResult] = None
    progress: float = 0.0
    error: Optional[str] = None
    
    # 依赖关系
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class PipelineDefinition:
    """流水线定义"""
    id: str
    name: str
    description: str = ""
    nodes: Dict[str, PipelineNode] = field(default_factory=dict)
    global_config: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
    
    def add_node(self, node: PipelineNode) -> "PipelineDefinition":
        """添加节点"""
        self.nodes[node.id] = node
        return self
    
    def connect(self, from_id: str, to_id: str) -> "PipelineDefinition":
        """连接节点"""
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[to_id].dependencies.add(from_id)
            self.nodes[from_id].dependents.add(to_id)
        return self
    
    def validate(self) -> Optional[str]:
        """验证流水线定义"""
        # 检查是否存在环
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep_id in self.nodes[node_id].dependencies:
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for node_id in self.nodes:
            if node_id not in visited:
                if has_cycle(node_id):
                    return "流水线存在循环依赖"
        
        # 检查技能是否存在
        for node in self.nodes.values():
            if node.skill_name not in skill_registry:
                return f"节点 {node.id} 引用的技能 '{node.skill_name}' 不存在"
        
        return None
    
    def get_execution_order(self) -> List[List[str]]:
        """获取执行顺序 (分层，同一层可并行)"""
        in_degree = {nid: len(node.dependencies) for nid, node in self.nodes.items()}
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        levels = []
        
        while queue:
            levels.append(queue[:])
            next_queue = []
            for nid in queue:
                for dependent in self.nodes[nid].dependents:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue
        
        return levels


@dataclass
class PipelineExecution:
    """流水线执行实例"""
    id: str
    definition: PipelineDefinition
    status: PipelineStatus = PipelineStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, SkillResult] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:12]


class PipelineEngine:
    """流水线引擎"""
    
    def __init__(self):
        self._executions: Dict[str, PipelineExecution] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._callbacks: Dict[str, List[Callable]] = {
            "on_node_start": [],
            "on_node_complete": [],
            "on_pipeline_complete": [],
            "on_error": []
        }
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调函数"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def _trigger(self, event: str, *args, **kwargs):
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")
    
    async def execute(self, definition: PipelineDefinition, 
                     initial_context: Optional[Dict[str, Any]] = None) -> PipelineExecution:
        """执行流水线"""
        # 验证流水线
        validation_error = definition.validate()
        if validation_error:
            raise ValueError(f"流水线验证失败: {validation_error}")
        
        # 创建执行实例
        execution = PipelineExecution(
            definition=definition,
            context=initial_context or {}
        )
        self._executions[execution.id] = execution
        
        execution.status = PipelineStatus.RUNNING
        execution.start_time = asyncio.get_event_loop().time()
        
        logger.info(f"🚀 流水线开始执行: {execution.id} - {definition.name}")
        
        try:
            # 获取执行顺序
            levels = definition.get_execution_order()
            
            for level_idx, level in enumerate(levels):
                logger.info(f"📌 执行第 {level_idx + 1} 层, 节点: {level}")
                
                # 同层节点并行执行
                tasks = []
                for node_id in level:
                    node = definition.nodes[node_id]
                    task = asyncio.create_task(
                        self._execute_node(execution, node),
                        name=f"node_{node_id}"
                    )
                    tasks.append((node_id, task))
                    self._running_tasks[f"{execution.id}:{node_id}"] = task
                
                # 等待本层完成
                for node_id, task in tasks:
                    try:
                        await task
                    except asyncio.CancelledError:
                        execution.status = PipelineStatus.CANCELLED
                        raise
                    finally:
                        self._running_tasks.pop(f"{execution.id}:{node_id}", None)
                
                # 检查是否有失败
                failed_nodes = [
                    nid for nid in level 
                    if definition.nodes[nid].status == NodeStatus.FAILED
                ]
                if failed_nodes:
                    execution.status = PipelineStatus.FAILED
                    execution.error = f"节点执行失败: {failed_nodes}"
                    break
            
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.COMPLETED
                logger.info(f"✅ 流水线执行完成: {execution.id}")
                await self._trigger("on_pipeline_complete", execution)
            
        except asyncio.CancelledError:
            execution.status = PipelineStatus.CANCELLED
            logger.warning(f"⏹️ 流水线已取消: {execution.id}")
            raise
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error = str(e)
            logger.error(f"❌ 流水线执行失败: {execution.id} - {e}")
            await self._trigger("on_error", execution, e)
        finally:
            execution.end_time = asyncio.get_event_loop().time()
        
        return execution
    
    async def _execute_node(self, execution: PipelineExecution, node: PipelineNode):
        """执行单个节点"""
        await self._trigger("on_node_start", execution, node)
        
        node.status = NodeStatus.RUNNING
        node.progress = 0.0
        
        try:
            # 获取技能实例
            skill = skill_registry.create_instance(node.skill_name, node.config)
            if not skill:
                raise ValueError(f"技能 '{node.skill_name}' 未找到")
            
            # 构建执行上下文
            context = SkillContext(
                project_id=execution.id,
                inputs={},
                metadata=execution.context
            )
            
            # 解析输入映射
            for param_name, source in node.inputs_mapping.items():
                if source.startswith("context."):
                    key = source[8:]
                    context.inputs[param_name] = execution.context.get(key)
                elif source.startswith("node."):
                    parts = source[5:].split(".")
                    src_node_id = parts[0]
                    src_output = parts[1] if len(parts) > 1 else "data"
                    if src_node_id in execution.results:
                        result = execution.results[src_node_id]
                        if isinstance(result.data, dict):
                            context.inputs[param_name] = result.data.get(src_output)
                        else:
                            context.inputs[param_name] = result.data
            
            # 执行技能
            result = await skill.execute(context)
            
            node.result = result
            node.status = NodeStatus.SUCCESS if result.success else NodeStatus.FAILED
            node.progress = 1.0
            
            # 保存结果
            execution.results[node.id] = result
            
            # 更新全局上下文
            if result.success and result.data:
                for output_key, mapped_key in node.outputs_mapping.items():
                    if isinstance(result.data, dict) and output_key in result.data:
                        execution.context[mapped_key] = result.data[output_key]
            
            await self._trigger("on_node_complete", execution, node, result)
            
            if not result.success:
                logger.warning(f"⚠️ 节点执行失败: {node.id} - {result.error}")
            else:
                logger.info(f"✅ 节点执行完成: {node.id}")
                
        except Exception as e:
            node.status = NodeStatus.FAILED
            node.error = str(e)
            logger.error(f"❌ 节点执行异常: {node.id} - {e}")
    
    async def cancel(self, execution_id: str):
        """取消流水线执行"""
        execution = self._executions.get(execution_id)
        if not execution:
            return
        
        execution.status = PipelineStatus.CANCELLED
        
        # 取消所有运行中的任务
        for key, task in list(self._running_tasks.items()):
            if key.startswith(f"{execution_id}:"):
                task.cancel()
    
    def get_execution(self, execution_id: str) -> Optional[PipelineExecution]:
        """获取执行实例"""
        return self._executions.get(execution_id)
    
    def get_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        execution = self._executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "id": execution.id,
            "status": execution.status.value,
            "progress": self._calculate_progress(execution),
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "error": execution.error,
            "nodes": {
                nid: {
                    "status": node.status.value,
                    "progress": node.progress,
                    "error": node.error
                }
                for nid, node in execution.definition.nodes.items()
            }
        }
    
    def _calculate_progress(self, execution: PipelineExecution) -> float:
        """计算整体进度"""
        if not execution.definition.nodes:
            return 0.0
        total = sum(node.progress for node in execution.definition.nodes.values())
        return total / len(execution.definition.nodes)

"""
AI模型路由层 - 多模型统一接口
智能路由、负载均衡、成本优化
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from loguru import logger

import httpx
from openai import AsyncOpenAI

from app.config import settings


class ModelCapability(str, Enum):
    """模型能力"""
    TEXT = "text"                # 文本生成
    CHAT = "chat"                # 对话
    CODE = "code"                # 代码
    IMAGE_GEN = "image_gen"      # 文生图
    IMAGE_UNDERSTAND = "image_understand"  # 图像理解
    VIDEO_GEN = "video_gen"      # 文生视频/图生视频
    AUDIO_TTS = "audio_tts"      # 文本转语音
    AUDIO_ASR = "audio_asr"      # 语音转文本


class ModelProvider(str, Enum):
    """模型提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    MOONSHOT = "moonshot"        # Kimi
    DASHSCOPE = "dashscope"      # 通义千问/万相
    DOUBAO = "doubao"            # 豆包
    ZHIPU = "zhipu"              # 智谱


@dataclass
class ModelConfig:
    """模型配置"""
    provider: ModelProvider
    model_id: str
    capabilities: List[ModelCapability]
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    priority: int = 0            # 优先级 (数字越小越优先)
    cost_per_1k_tokens: float = 0.0
    max_tokens: int = 4096
    supports_streaming: bool = True


# 预设模型配置
DEFAULT_MODELS: List[ModelConfig] = [
    # DeepSeek (推荐：推理能力+性价比高)
    ModelConfig(
        provider=ModelProvider.DEEPSEEK,
        model_id="deepseek-chat",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT, ModelCapability.CODE],
        base_url="https://api.deepseek.com/v1",
        api_key=settings.DEEPSEEK_API_KEY,
        priority=1,
        cost_per_1k_tokens=0.001,
        max_tokens=8192
    ),
    ModelConfig(
        provider=ModelProvider.DEEPSEEK,
        model_id="deepseek-reasoner",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT, ModelCapability.CODE],
        base_url="https://api.deepseek.com/v1",
        api_key=settings.DEEPSEEK_API_KEY,
        priority=2,
        cost_per_1k_tokens=0.003,
        max_tokens=8192
    ),
    # Moonshot / Kimi (推荐：长文本处理)
    ModelConfig(
        provider=ModelProvider.MOONSHOT,
        model_id="moonshot-v1-128k",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT, ModelCapability.CODE],
        base_url="https://api.moonshot.cn/v1",
        api_key=settings.KIMI_API_KEY,
        priority=3,
        cost_per_1k_tokens=0.006,
        max_tokens=128000
    ),
    # 通义千问 (推荐：图像/视频生成)
    ModelConfig(
        provider=ModelProvider.DASHSCOPE,
        model_id="qwen-max",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT],
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key=settings.DASHSCOPE_API_KEY,
        priority=4,
        max_tokens=8192
    ),
    ModelConfig(
        provider=ModelProvider.DASHSCOPE,
        model_id="wanx-v1",
        capabilities=[ModelCapability.IMAGE_GEN],
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key=settings.DASHSCOPE_API_KEY,
        priority=1,
    ),
    ModelConfig(
        provider=ModelProvider.DASHSCOPE,
        model_id="wanx2.1-t2v-plus",
        capabilities=[ModelCapability.VIDEO_GEN],
        base_url="https://dashscope.aliyuncs.com/api/v1",
        api_key=settings.DASHSCOPE_API_KEY,
        priority=1,
    ),
    # 豆包
    ModelConfig(
        provider=ModelProvider.DOUBAO,
        model_id="doubao-pro-128k",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT],
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=settings.DOUBAO_API_KEY,
        priority=5,
        max_tokens=128000
    ),
    # OpenAI (备选)
    ModelConfig(
        provider=ModelProvider.OPENAI,
        model_id="gpt-4o",
        capabilities=[ModelCapability.TEXT, ModelCapability.CHAT, ModelCapability.IMAGE_UNDERSTAND],
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
        priority=10,
        cost_per_1k_tokens=0.005,
        max_tokens=8192
    ),
]


class BaseModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = None
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """对话接口"""
        pass
    
    @abstractmethod
    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """流式对话接口"""
        pass
    
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> str:
        """生成图片，返回URL或base64"""
        pass
    
    @abstractmethod
    async def generate_video(self, prompt: str, **kwargs) -> str:
        """生成视频，返回URL"""
        pass


class OpenAICompatibleAdapter(BaseModelAdapter):
    """OpenAI兼容接口适配器 (支持DeepSeek/Moonshot/Kimi/Doubao等)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.config.model_id,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", 0.7),
            stream=False
        )
        return response.choices[0].message.content
    
    async def chat_stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        stream = await self.client.chat.completions.create(
            model=self.config.model_id,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            temperature=kwargs.get("temperature", 0.7),
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def generate_image(self, prompt: str, **kwargs) -> str:
        # 通义万相特殊处理
        if self.config.provider == ModelProvider.DASHSCOPE:
            return await self._call_dashscope_image(prompt, **kwargs)
        
        response = await self.client.images.generate(
            model=self.config.model_id,
            prompt=prompt,
            size=kwargs.get("size", "1024x1024"),
            quality=kwargs.get("quality", "standard"),
            n=1
        )
        return response.data[0].url or response.data[0].b64_json
    
    async def generate_video(self, prompt: str, **kwargs) -> str:
        if self.config.provider == ModelProvider.DASHSCOPE:
            return await self._call_dashscope_video(prompt, **kwargs)
        raise NotImplementedError(f"{self.config.provider} 暂不支持视频生成")
    
    async def _call_dashscope_image(self, prompt: str, **kwargs) -> str:
        """调用通义万相生成图片"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.base_url}/services/aigc/text2image/image-synthesis",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                json={
                    "model": self.config.model_id,
                    "input": {"prompt": prompt},
                    "parameters": {
                        "size": kwargs.get("size", "1024*1024"),
                        "n": 1
                    }
                },
                timeout=60
            )
            data = response.json()
            # 异步任务，需要轮询
            task_id = data.get("output", {}).get("task_id")
            return await self._poll_task(client, task_id, self.config.api_key, is_image=True)
    
    async def _call_dashscope_video(self, prompt: str, **kwargs) -> str:
        """调用万相生成视频"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.base_url}/services/aigc/video-generation/video-synthesis",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                json={
                    "model": self.config.model_id,
                    "input": {
                        "prompt": prompt,
                        **({"img_url": kwargs["image_url"]} if "image_url" in kwargs else {})
                    },
                    "parameters": {
                        "size": kwargs.get("size", "1280*720"),
                        "duration": kwargs.get("duration", 5)
                    }
                },
                timeout=60
            )
            data = response.json()
            task_id = data.get("output", {}).get("task_id")
            return await self._poll_task(client, task_id, self.config.api_key, is_image=False)
    
    async def _poll_task(self, client: httpx.AsyncClient, task_id: str, api_key: str, 
                         is_image: bool, max_retries: int = 60) -> str:
        """轮询异步任务结果"""
        endpoint = "image-synthesis" if is_image else "video-synthesis"
        for _ in range(max_retries):
            response = await client.get(
                f"{self.config.base_url}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
            data = response.json()
            status = data.get("output", {}).get("task_status")
            
            if status == "SUCCEEDED":
                results = data.get("output", {}).get("results", [])
                return results[0].get("url") if results else ""
            elif status == "FAILED":
                raise RuntimeError(f"任务失败: {data}")
            
            await asyncio.sleep(2)
        
        raise TimeoutError("轮询超时")


class ModelRouter:
    """模型路由器"""
    
    def __init__(self):
        self._models: Dict[str, ModelConfig] = {}
        self._adapters: Dict[str, BaseModelAdapter] = {}
        self._load_models()
    
    def _load_models(self):
        """加载模型配置"""
        for config in DEFAULT_MODELS:
            if not config.api_key:
                logger.debug(f"跳过未配置API Key的模型: {config.model_id}")
                continue
            
            self._models[config.model_id] = config
            
            # 创建适配器
            if config.provider in [ModelProvider.DEEPSEEK, ModelProvider.MOONSHOT, 
                                   ModelProvider.DOUBAO, ModelProvider.DASHSCOPE,
                                   ModelProvider.OPENAI]:
                self._adapters[config.model_id] = OpenAICompatibleAdapter(config)
            
            logger.info(f"✅ 模型已加载: {config.model_id} ({config.provider.value})")
    
    def select_model(self, capability: ModelCapability, 
                     preferred: Optional[str] = None) -> Optional[ModelConfig]:
        """根据能力选择最优模型"""
        if preferred and preferred in self._models:
            config = self._models[preferred]
            if capability in config.capabilities:
                return config
        
        # 按优先级排序
        candidates = [
            config for config in self._models.values()
            if capability in config.capabilities
        ]
        candidates.sort(key=lambda c: c.priority)
        
        return candidates[0] if candidates else None
    
    async def chat(self, messages: List[Dict[str, str]], 
                   model: Optional[str] = None, **kwargs) -> str:
        """统一对话接口"""
        config = self.select_model(ModelCapability.CHAT, model)
        if not config:
            raise ValueError("没有可用的对话模型，请检查API Key配置")
        
        adapter = self._adapters[config.model_id]
        return await adapter.chat(messages, **kwargs)
    
    async def chat_stream(self, messages: List[Dict[str, str]], 
                          model: Optional[str] = None, **kwargs) -> AsyncGenerator[str, None]:
        """统一流式对话接口"""
        config = self.select_model(ModelCapability.CHAT, model)
        if not config:
            raise ValueError("没有可用的对话模型")
        
        adapter = self._adapters[config.model_id]
        async for chunk in adapter.chat_stream(messages, **kwargs):
            yield chunk
    
    async def generate_image(self, prompt: str, 
                             model: Optional[str] = None, **kwargs) -> str:
        """统一图片生成接口"""
        config = self.select_model(ModelCapability.IMAGE_GEN, model)
        if not config:
            raise ValueError("没有可用的图像生成模型")
        
        adapter = self._adapters[config.model_id]
        return await adapter.generate_image(prompt, **kwargs)
    
    async def generate_video(self, prompt: str, image_url: Optional[str] = None,
                             model: Optional[str] = None, **kwargs) -> str:
        """统一视频生成接口"""
        config = self.select_model(ModelCapability.VIDEO_GEN, model)
        if not config:
            raise ValueError("没有可用的视频生成模型")
        
        adapter = self._adapters[config.model_id]
        if image_url:
            kwargs["image_url"] = image_url
        return await adapter.generate_video(prompt, **kwargs)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """列出所有可用模型"""
        return [
            {
                "id": config.model_id,
                "provider": config.provider.value,
                "capabilities": [c.value for c in config.capabilities],
                "priority": config.priority,
                "max_tokens": config.max_tokens
            }
            for config in self._models.values()
        ]
    
    def get_recommendation(self, task_type: str) -> Dict[str, str]:
        """获取模型推荐方案"""
        recommendations = {
            "text_generation": {
                "primary": "deepseek-chat",
                "backup": "moonshot-v1-128k",
                "reasoning": "deepseek-reasoner"
            },
            "script_writing": {
                "primary": "moonshot-v1-128k",
                "backup": "deepseek-chat",
                "reason": "长上下文支持完整脚本"
            },
            "image_generation": {
                "primary": "wanx-v1",
                "backup": "dall-e-3",
                "reason": "万相中文理解更好，风格适配国内平台"
            },
            "video_generation": {
                "primary": "wanx2.1-t2v-plus",
                "backup": None,
                "reason": "万相2.1是目前国内领先的文生视频模型"
            },
            "code_task": {
                "primary": "deepseek-reasoner",
                "backup": "deepseek-chat",
                "reason": "DeepSeek推理能力最强"
            }
        }
        return recommendations.get(task_type, {"primary": "deepseek-chat"})


# 全局路由器实例
model_router = ModelRouter()

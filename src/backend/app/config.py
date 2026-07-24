"""
应用配置管理
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class Settings(BaseSettings):
    # 基础配置
    APP_NAME: str = "SafeVideo Forge"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, alias="DEBUG")
    
    # 服务配置
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # 数据库
    DATABASE_URL: str = f"sqlite+aiosqlite:///{PROJECT_ROOT}/data/safevideo.db"
    
    # 存储路径
    ASSETS_DIR: Path = PROJECT_ROOT / "assets"
    TEMP_DIR: Path = PROJECT_ROOT / "assets" / "temp"
    CACHE_DIR: Path = PROJECT_ROOT / "assets" / "cache"
    SKILLS_DIR: Path = PROJECT_ROOT / "skills"
    
    # AI模型配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    ANTHROPIC_API_KEY: str = ""
    
    # 国内模型 (可选)
    DASHSCOPE_API_KEY: str = ""      # 通义千问/万相
    ZHIPU_API_KEY: str = ""           # 智谱
    DOUBAO_API_KEY: str = ""          # 豆包
    DEEPSEEK_API_KEY: str = ""        # DeepSeek
    KIMI_API_KEY: str = ""            # Kimi (Moonshot)
    
    # 模型路由配置
    DEFAULT_TEXT_MODEL: str = "deepseek-chat"
    DEFAULT_IMAGE_MODEL: str = "wanx-v1"
    DEFAULT_VIDEO_MODEL: str = "wanx2.1-t2v-plus"
    
    # 视频处理配置
    FFMPEG_PATH: str = "ffmpeg"
    MAX_VIDEO_DURATION: int = 180     # 最大视频时长(秒)
    DEFAULT_VIDEO_FPS: int = 30
    DEFAULT_VIDEO_RESOLUTION: tuple = (1080, 1920)  # 竖屏 9:16
    
    # 音频配置
    DEFAULT_TTS_VOICE: str = "zh-CN-XiaoxiaoNeural"  # Edge TTS默认语音
    DEFAULT_BGM_VOLUME: float = 0.15
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
settings = Settings()

# 确保必要目录存在
for path in [settings.ASSETS_DIR, settings.TEMP_DIR, settings.CACHE_DIR, settings.SKILLS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

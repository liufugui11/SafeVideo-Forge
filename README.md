# 🎬 SafeVideo Forge — 安全生产视频智能生产工具

> **面向安全生产类视频号博主的本地化自动化视频生产桌面工具**
>
> 从文案输入到成品分发，实现全流程自动化；支持视频解析与技能库系统，集成多模型AI能力。

---

## 📋 功能总览

### 一、自动化视频生成流水线

| 步骤 | 功能 | 技术方案 |
|------|------|---------|
| 1. 文案生成 | 根据关键词/主题自动生成文案，素材库智能检索 | 多模型LLM + RAG检索 |
| 2. 脚本拆分 | 按场景/镜头自动拆分为结构化脚本 | LLM + 规则引擎 |
| 3. 画面构想 | 为每个分镜生成画面描述及AI绘图/视频提示词 | 多模态模型 |
| 4. 画面生成 | 调用大模型生成工业级、现实3D渲染风格画面 | 文生图/图生视频API |
| 5. 语音音乐 | 自动生成旁白配音及背景音乐 | TTS + BGM合成 |
| 6. 质检合成 | 自动检查各元素质量并合成最终视频 | FFmpeg + 质量检测 |
| 7. 一键分发 | 支持发布到视频号等平台 | 平台API集成 |

### 二、视频解析功能

- **语言风格分析**：语气、节奏、表达方式
- **画面风格分析**：色调、构图、转场风格
- **呈现效果评估**：视觉冲击力、信息密度
- **质量标准评级**：清晰度、专业度
- **传播效果预测**：完播率预测、互动潜力评估

### 三、技能库系统（SKII）

将各功能模块化为可复用技能，按类型分类管理，支持自定义技能编排。

### 四、多模型接口集成

| 厂商 | 模型 | 能力 | 推荐场景 |
|------|------|------|---------|
| 字节跳动 | 豆包/即梦 | 文生图、图生视频 | 画面生成 |
| Moonshot | Kimi | 长文本处理、脚本生成 | 文案、脚本 |
| DeepSeek | DeepSeek-V3/R1 | 推理、代码、文本 | 脚本拆分、质检 |
| 阿里 | 通义千问/万相 | 文生视频、图生视频 | 画面生成（主力） |
| 其他 | Stable Diffusion / ComfyUI | 本地图像生成 | 备选方案 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron + Vue3 桌面端                    │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ 项目管理 │ │ 技能编排 │ │ 视频预览 │ │ 设置中心 │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└────────────────────────┬────────────────────────────────────┘
                         │ IPC / HTTP
┌────────────────────────▼────────────────────────────────────┐
│              Python FastAPI 后端服务                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 流水线引擎 │ │ 技能管理器 │ │ 模型路由层 │ │ 媒体处理器 │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 核心依赖

| 模块 | 主要依赖 |
|------|---------|
| 桌面端 | Electron 33+, Vue3, TypeScript, Vite |
| 后端 | Python 3.10+, FastAPI, Celery, SQLAlchemy |
| 视频处理 | FFmpeg, MoviePy, OpenCV |
| AI模型 | openai, anthropic, 各厂商SDK |
| 数据库 | SQLite (本地), PostgreSQL (可选) |

---

## 🚀 快速开始

### 环境要求

- **Node.js** >= 18
- **Python** >= 3.10
- **FFmpeg** >= 5.0 (必须)
- **CUDA** >= 11.8 (GPU加速可选)

### 1. 克隆项目

```bash
git clone https://github.com/liufugui11/SafeVideo-Forge.git
cd SafeVideo-Forge
```

### 2. 安装后端依赖

```bash
cd src/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd src/frontend
npm install
```

### 4. 启动开发环境

```bash
# 终端1：启动后端
python src/backend/main.py

# 终端2：启动前端
cd src/frontend
npm run dev
```

### 5. 打包构建

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

---

## 📁 项目结构

```
SafeVideo-Forge/
├── docs/                    # 项目文档
│   ├── architecture.md      # 架构设计文档
│   ├── api.md               # API接口文档
│   ├── skills.md            # 技能开发指南
│   └── deployment.md        # 部署指南
├── src/
│   ├── backend/             # Python后端服务
│   │   ├── app/             # FastAPI应用
│   │   ├── core/            # 核心引擎
│   │   ├── skills/          # 技能库实现
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务服务
│   │   └── utils/           # 工具函数
│   ├── frontend/            # Electron+Vue3前端
│   │   ├── src/
│   │   │   ├── components/  # 公共组件
│   │   │   ├── views/       # 页面视图
│   │   │   ├── stores/      # Pinia状态管理
│   │   │   └── api/         # 后端接口封装
│   └── shared/              # 前后端共享类型定义
├── skills/                  # 用户自定义技能目录
├── assets/                  # 默认素材资源
├── configs/                 # 配置文件
├── tests/                   # 测试用例
├── scripts/                 # 构建/部署脚本
└── README.md
```

---

## 🔧 核心模块说明

### 流水线引擎 (Pipeline Engine)

基于有向无环图(DAG)的任务调度引擎，支持：
- 可视化节点编排
- 并行/串行执行
- 断点续传
- 任务回滚

### 技能库系统 (SKII)

```python
# 技能定义示例
@skill(
    name="文案生成器",
    category="content",
    version="1.0.0",
    inputs={"topic": str, "style": str},
    outputs={"script": str}
)
class ScriptGeneratorSkill(BaseSkill):
    async def execute(self, context: SkillContext) -> SkillResult:
        # 技能实现
        ...
```

### 模型路由层

智能模型选择和负载均衡：
- 按能力自动路由到最优模型
- API密钥管理
- 请求限流与重试
- 成本优化

---

## 📊 视频号发布规格

| 参数 | 规格 |
|------|------|
| 分辨率 | 1080×1920 (9:16) |
| 码率 | 推荐 8-15 Mbps |
| 帧率 | 30/60 fps |
| 时长 | 15s - 3min |
| 格式 | MP4 (H.264) |
| 音频 | AAC, 128kbps+ |

---

## 🤝 开源参考

本项目在以下优秀开源项目的基础上构建：

| 项目 | 用途 |
|------|------|
| [Toonflow-app](https://github.com/HBAI-Ltd/Toonflow-app) | 桌面端架构参考 |
| [MoneyPrinterAICreate](https://github.com/q1uki/MoneyPrinterAICreate) | 视频生成流水线 |
| [autoclip](https://github.com/zhouxiaoka/autoclip) | 视频剪辑自动化 |
| [KrillinAI](https://github.com/krillinai/KrillinAI) | 视频翻译配音 |
| [Jellyfish](https://github.com/Forget-C/Jellyfish) | 短剧生产工作流 |

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🙏 致谢

感谢所有开源社区贡献者的辛勤工作，让AI视频生成技术更加普及和易用。

---

<p align="center">
  Made with ❤️ for 安全生产内容创作者
</p>

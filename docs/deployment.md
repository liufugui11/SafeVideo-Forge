# 🚀 本地部署指南

## 系统要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 / macOS 12 / Ubuntu 20.04 | Windows 11 / macOS 14 / Ubuntu 22.04 |
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| 硬盘 | 10GB SSD | 50GB+ SSD |
| GPU | 可选 | NVIDIA RTX 3060+ |
| 网络 | 宽带 | 稳定的高速网络 |

## 前置依赖

### 1. 安装 Node.js (>= 18)

```bash
# Windows/macOS: 从官网下载安装
# https://nodejs.org/

# 或使用 nvm
nvm install 20
nvm use 20

node -v  # v20.x.x
npm -v   # 10.x.x
```

### 2. 安装 Python (>= 3.10)

```bash
# Windows: 从官网下载安装
# https://www.python.org/downloads/

# macOS
brew install python@3.11

# Ubuntu
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip

python --version  # Python 3.11.x
```

### 3. 安装 FFmpeg (>= 5.0)

```bash
# Windows: 下载并添加到 PATH
# https://ffmpeg.org/download.html

# macOS
brew install ffmpeg

# Ubuntu
sudo apt update
sudo apt install ffmpeg

ffmpeg -version
```

### 4. 安装 Git

```bash
# 所有平台: https://git-scm.com/downloads
git --version
```

## 项目安装

### 1. 克隆项目

```bash
git clone https://github.com/liufugui11/SafeVideo-Forge.git
cd SafeVideo-Forge
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，填入你的API Key
nano .env
```

`.env` 文件内容示例：

```env
# 服务配置
DEBUG=true
HOST=127.0.0.1
PORT=8000

# AI模型API Key (至少配置一个)
DEEPSEEK_API_KEY=sk-your-deepseek-key
KIMI_API_KEY=sk-your-moonshot-key
DASHSCOPE_API_KEY=sk-your-dashscope-key
DOUBAO_API_KEY=your-doubao-key

# OpenAI (可选)
OPENAI_API_KEY=sk-your-openai-key
```

> ⚠️ **重要**: 国内模型推荐配置顺序：DeepSeek > Kimi > 通义千问 > 豆包

### 3. 安装后端依赖

```bash
cd src/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 安装前端依赖

```bash
cd src/frontend

npm install

# 或使用 pnpm (推荐)
pnpm install
```

## 启动开发环境

### 方法1: 分别启动前后端

```bash
# 终端1: 启动后端
cd src/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py

# 终端2: 启动前端
cd src/frontend
npm run dev
```

### 方法2: 使用脚本一键启动

```bash
# 创建启动脚本 (项目根目录)
# Windows: start-dev.bat
@echo off
start cmd /k "cd src/backend && venv\Scripts\activate && python main.py"
start cmd /k "cd src/frontend && npm run dev"

# macOS/Linux: start-dev.sh
#!/bin/bash
cd src/backend && source venv/bin/activate && python main.py &
cd src/frontend && npm run dev
```

## 生产环境打包

### 构建前端

```bash
cd src/frontend
npm run build
```

### 打包桌面应用

```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux

# 所有平台
npm run build:electron
```

打包后的应用位于 `src/frontend/release/` 目录下。

## API Key 获取指南

### DeepSeek (推荐首选)

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号
3. 创建 API Key
4. 新用户有免费额度

### Kimi (Moonshot)

1. 访问 [Moonshot 开放平台](https://platform.moonshot.cn/)
2. 注册账号
3. 创建 API Key
4. 新用户有 15 元免费额度

### 通义千问/万相 (推荐视频生成)

1. 访问 [DashScope 灵积平台](https://dashscope.aliyun.com/)
2. 使用阿里云账号登录
3. 创建 API Key
4. 新用户有免费额度

### 豆包

1. 访问 [火山引擎](https://www.volcengine.com/)
2. 注册并创建推理接入点
3. 获取 API Key

## 常见问题

### Q1: FFmpeg 找不到？

```bash
# Windows: 添加到系统PATH后重启终端
# 或手动指定路径
set FFMPEG_PATH=C:\ffmpeg\bin\ffmpeg.exe

# macOS/Linux
export FFMPEG_PATH=/usr/local/bin/ffmpeg
```

### Q2: Python 包安装失败？

```bash
# 更新 pip
pip install --upgrade pip setuptools wheel

# 单独安装有问题的包
pip install moviepy --no-cache-dir
```

### Q3: Node 模块安装失败？

```bash
# 清除缓存并重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Q4: 后端启动报错？

```bash
# 检查Python版本
python --version  # 必须 >= 3.10

# 检查依赖
pip list | grep fastapi

# 查看详细日志
python main.py --log-level debug
```

## 更新项目

```bash
git pull origin main

# 更新后端依赖
cd src/backend
pip install -r requirements.txt --upgrade

# 更新前端依赖
cd src/frontend
npm update
```

## 调试技巧

### 后端调试

```bash
# 启用详细日志
LOG_LEVEL=debug python main.py

# 使用VSCode调试
# 配置 .vscode/launch.json
```

### 前端调试

```bash
# 打开开发者工具
npm run dev
# 在Electron窗口按 Ctrl+Shift+I (Windows) 或 Cmd+Option+I (macOS)
```

---

> 💡 **提示**: 首次运行建议先测试单个技能是否正常，再运行完整流水线。

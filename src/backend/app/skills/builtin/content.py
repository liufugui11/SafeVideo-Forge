"""
内置技能实现 - 内容生成类
"""

import json
from typing import Dict, Any, Optional
from app.skills.base import BaseSkill, SkillContext, SkillResult, SkillCategory, skill
from app.core.ai.router import model_router


@skill(
    name="文案生成器",
    category=SkillCategory.CONTENT,
    version="1.0.0",
    description="根据关键词或主题自动生成安全生产类视频文案，支持多种风格",
    author="SafeVideo Forge",
    inputs={"topic": str, "style": str, "duration": int, "audience": str},
    outputs={"script": str, "title": str, "hashtags": list},
    config_schema={
        "tone": {"type": "string", "enum": ["严肃", "警示", "科普", "故事化"], "default": "警示"},
        "language": {"type": "string", "default": "zh-CN"},
        "include_case": {"type": "boolean", "default": True},
        "case_source": {"type": "string", "enum": ["自动生成", "素材库"], "default": "自动生成"}
    }
)
class ScriptGeneratorSkill(BaseSkill):
    """文案生成技能"""
    
    SYSTEM_PROMPT = """你是一位专业的安全生产教育内容创作者。
请根据用户提供的主题，创作适合短视频平台的文案。

要求：
1. 开头3秒必须有强吸引力的钩子（Hook）
2. 内容要真实、有警示意义
3. 使用口语化表达，适合视频朗读
4. 每段不要太长，适合分镜拆分
5. 结尾要有明确的行动号召（CTA）

请按以下JSON格式输出：
{
    "title": "视频标题",
    "hook": "开头钩子（3秒内）",
    "script": "完整文案",
    "segments": [
        {"scene": "场景1", "text": "文案内容", "duration": 5},
        ...
    ],
    "hashtags": ["#标签1", "#标签2"],
    "bgm_suggestion": "背景音乐风格建议"
}"""

    async def execute(self, context: SkillContext) -> SkillResult:
        topic = context.get("topic", "安全生产")
        style = context.get("style", "警示")
        duration = context.get("duration", 60)
        audience = context.get("audience", "一线工人")
        tone = self.config.get("tone", "警示")
        include_case = self.config.get("include_case", True)
        
        user_prompt = f"""请创作一个关于"{topic}"的安全生产短视频文案。

要求：
- 风格: {style}
- 目标受众: {audience}
- 预期时长: {duration}秒
- 语气: {tone}
- {"需要包含真实案例分析" if include_case else "不需要案例"}

请直接输出JSON格式结果。"""
        
        try:
            response = await model_router.chat([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ])
            
            # 解析JSON
            # 尝试从响应中提取JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result_data = json.loads(response[json_start:json_end])
            else:
                # 无法解析，返回原始文本
                result_data = {"script": response, "title": topic, "hashtags": []}
            
            return SkillResult.ok(
                data=result_data,
                message="文案生成成功"
            )
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="文案生成失败"
            )


@skill(
    name="脚本拆分器",
    category=SkillCategory.CONTENT,
    version="1.0.0",
    description="将文案按场景/镜头自动拆分为结构化分镜脚本",
    author="SafeVideo Forge",
    inputs={"script": str, "duration": int},
    outputs={"storyboard": list, "total_scenes": int},
    config_schema={
        "min_scene_duration": {"type": "integer", "default": 3},
        "max_scene_duration": {"type": "integer", "default": 15},
        "split_by": {"type": "string", "enum": ["语义", "时间", "混合"], "default": "混合"}
    }
)
class ScriptSplitterSkill(BaseSkill):
    """脚本拆分技能"""
    
    SYSTEM_PROMPT = """你是一位专业的短视频分镜师。
请将提供的文案拆分为详细的分镜脚本，每个分镜包含：

1. 场景编号
2. 画面描述（详细的视觉描述，适合AI绘图）
3. 旁白/台词
4. 时长（秒）
5. 景别（特写/近景/中景/全景）
6. 镜头运动（固定/推/拉/摇/移）
7. 画面风格提示词（英文，适合AI生成）

注意：
- 画面风格要统一，建议使用"industrial safety, realistic 3D render, photorealistic"等关键词
- 每个分镜时长3-15秒
- 总时长控制在要求范围内"""

    async def execute(self, context: SkillContext) -> SkillResult:
        script = context.get("script", "")
        duration = context.get("duration", 60)
        split_by = self.config.get("split_by", "混合")
        
        user_prompt = f"""请将以下文案拆分为分镜脚本：

文案内容：
{script}

要求：
- 总时长: {duration}秒
- 拆分方式: {split_by}

请输出JSON格式，格式如下：
{{
    "storyboard": [
        {{
            "scene_number": 1,
            "visual_description": "画面描述",
            "narration": "旁白内容",
            "duration": 5,
            "shot_type": "中景",
            "camera_movement": "固定",
            "ai_prompt": "English prompt for AI generation"
        }}
    ],
    "total_scenes": 5,
    "total_duration": 60
}}"""
        
        try:
            response = await model_router.chat([
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ])
            
            # 解析JSON
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            result_data = json.loads(response[json_start:json_end])
            
            return SkillResult.ok(
                data=result_data,
                message=f"脚本拆分完成，共 {result_data.get('total_scenes', 0)} 个场景"
            )
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="脚本拆分失败"
            )


@skill(
    name="画面提示词生成器",
    category=SkillCategory.VISUAL,
    version="1.0.0",
    description="为每个分镜生成详细的AI绘图/视频生成提示词",
    author="SafeVideo Forge",
    inputs={"scene_description": str, "style": str},
    outputs={"prompt": str, "negative_prompt": str, "parameters": dict},
    config_schema={
        "style_preset": {"type": "string", "enum": ["工业写实", "3D渲染", "纪录片", "警示教育"], "default": "工业写实"},
        "consistency_mode": {"type": "boolean", "default": True}
    }
)
class PromptGeneratorSkill(BaseSkill):
    """提示词生成技能"""
    
    STYLE_TEMPLATES = {
        "工业写实": "industrial workplace, photorealistic, safety equipment, realistic lighting, documentary style",
        "3D渲染": "3D render, CGI, industrial safety, Unreal Engine 5, cinematic lighting, highly detailed",
        "纪录片": "documentary footage, real workplace, natural lighting, handheld camera style",
        "警示教育": "dramatic lighting, warning atmosphere, high contrast, safety warning visuals"
    }
    
    async def execute(self, context: SkillContext) -> SkillResult:
        scene_desc = context.get("scene_description", "")
        style = self.config.get("style_preset", "工业写实")
        consistency = self.config.get("consistency_mode", True)
        
        base_style = self.STYLE_TEMPLATES.get(style, self.STYLE_TEMPLATES["工业写实"])
        
        # 一致性角色/场景描述
        consistency_prompt = ""
        if consistency:
            consistency_prompt = "consistent characters, same industrial setting, uniform safety gear, "
        
        negative = "cartoon, anime, blurry, low quality, deformed, text, watermark, logo, unrealistic proportions"
        
        prompt = f"{scene_desc}, {consistency_prompt}{base_style}, 8k uhd, professional photography"
        
        return SkillResult.ok(
            data={
                "prompt": prompt,
                "negative_prompt": negative,
                "parameters": {
                    "width": 1080,
                    "height": 1920,
                    "seed": -1,
                    "steps": 30,
                    "cfg_scale": 7.0
                }
            },
            message="提示词生成成功"
        )


@skill(
    name="画面生成器",
    category=SkillCategory.VISUAL,
    version="1.0.0",
    description="调用AI模型生成画面（文生图/图生视频）",
    author="SafeVideo Forge",
    inputs={"prompt": str, "image_url": str},
    outputs={"media_url": str, "media_type": str},
    config_schema={
        "model": {"type": "string", "default": "wanx-v1"},
        "size": {"type": "string", "default": "1080x1920"},
        "generate_video": {"type": "boolean", "default": False}
    }
)
class MediaGeneratorSkill(BaseSkill):
    """媒体生成技能"""
    
    async def execute(self, context: SkillContext) -> SkillResult:
        prompt = context.get("prompt", "")
        image_url = context.get("image_url", None)
        generate_video = self.config.get("generate_video", False)
        
        try:
            if generate_video and image_url:
                # 图生视频
                url = await model_router.generate_video(
                    prompt=prompt,
                    image_url=image_url,
                    model=self.config.get("model", "wanx2.1-t2v-plus"),
                    duration=5
                )
                media_type = "video"
            else:
                # 文生图
                url = await model_router.generate_image(
                    prompt=prompt,
                    model=self.config.get("model", "wanx-v1"),
                    size=self.config.get("size", "1024x1024")
                )
                media_type = "image"
            
            return SkillResult.ok(
                data={
                    "media_url": url,
                    "media_type": media_type,
                    "prompt": prompt
                },
                message=f"{media_type}生成成功"
            )
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="媒体生成失败"
            )


@skill(
    name="语音合成器",
    category=SkillCategory.AUDIO,
    version="1.0.0",
    description="自动生成旁白配音",
    author="SafeVideo Forge",
    inputs={"text": str, "voice_id": str},
    outputs={"audio_url": str, "duration": float},
    config_schema={
        "engine": {"type": "string", "enum": ["edge-tts", "gtts"], "default": "edge-tts"},
        "speed": {"type": "number", "default": 1.0},
        "pitch": {"type": "number", "default": 0.0}
    }
)
class TTSGeneratorSkill(BaseSkill):
    """TTS语音合成技能"""
    
    DEFAULT_VOICES = {
        "zh-CN-XiaoxiaoNeural": "晓晓 - 年轻女声",
        "zh-CN-YunxiNeural": "云希 - 年轻男声",
        "zh-CN-YunjianNeural": "云健 - 成熟男声",
        "zh-CN-XiaoyiNeural": "晓伊 - 温柔女声"
    }
    
    async def execute(self, context: SkillContext) -> SkillResult:
        text = context.get("text", "")
        voice_id = context.get("voice_id", "zh-CN-XiaoxiaoNeural")
        engine = self.config.get("engine", "edge-tts")
        
        try:
            import edge_tts
            import asyncio
            
            output_path = f"assets/temp/tts_{id(context)}.mp3"
            
            communicate = edge_tts.Communicate(text, voice_id)
            await communicate.save(output_path)
            
            # 获取时长
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(output_path)
            duration = len(audio) / 1000.0
            
            return SkillResult.ok(
                data={
                    "audio_url": output_path,
                    "duration": duration,
                    "voice": self.DEFAULT_VOICES.get(voice_id, voice_id)
                },
                message="语音合成成功"
            )
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="语音合成失败"
            )


@skill(
    name="视频合成器",
    category=SkillCategory.EDIT,
    version="1.0.0",
    description="将画面、语音、音乐合成为最终视频",
    author="SafeVideo Forge",
    inputs={"scenes": list, "audio_tracks": list, "bgm_url": str},
    outputs={"video_url": str, "duration": float},
    config_schema={
        "resolution": {"type": "string", "default": "1080x1920"},
        "fps": {"type": "integer", "default": 30},
        "bgm_volume": {"type": "number", "default": 0.15},
        "transition": {"type": "string", "enum": ["fade", "slide", "none"], "default": "fade"}
    }
)
class VideoComposerSkill(BaseSkill):
    """视频合成技能"""
    
    async def execute(self, context: SkillContext) -> SkillResult:
        scenes = context.get("scenes", [])
        audio_tracks = context.get("audio_tracks", [])
        bgm_url = context.get("bgm_url", None)
        
        resolution = self.config.get("resolution", "1080x1920")
        fps = self.config.get("fps", 30)
        bgm_volume = self.config.get("bgm_volume", 0.15)
        
        try:
            from moviepy.editor import (ImageClip, AudioFileClip, concatenate_videoclips,
                                       CompositeAudioClip, ColorClip)
            import os
            
            w, h = map(int, resolution.split("x"))
            
            # 构建视频片段
            video_clips = []
            for scene in scenes:
                media_url = scene.get("media_url", "")
                duration = scene.get("duration", 5)
                
                if media_url.endswith((".mp4", ".mov", ".avi")):
                    clip = VideoFileClip(media_url).resize((w, h))
                else:
                    # 图片
                    clip = ImageClip(media_url).set_duration(duration).resize((w, h))
                
                video_clips.append(clip)
            
            # 合成视频
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # 添加音频
            audio_clips = []
            
            # 旁白
            for track in audio_tracks:
                if os.path.exists(track.get("url", "")):
                    audio = AudioFileClip(track["url"])
                    audio_clips.append(audio)
            
            # 背景音乐
            if bgm_url and os.path.exists(bgm_url):
                bgm = AudioFileClip(bgm_url).volumex(bgm_volume)
                # 循环BGM以匹配视频长度
                if bgm.duration < final_video.duration:
                    n_loops = int(final_video.duration / bgm.duration) + 1
                    bgm = concatenate_audioclips([bgm] * n_loops).subclip(0, final_video.duration)
                else:
                    bgm = bgm.subclip(0, final_video.duration)
                audio_clips.append(bgm)
            
            if audio_clips:
                final_audio = CompositeAudioClip(audio_clips)
                final_video = final_video.set_audio(final_audio)
            
            # 输出
            output_path = f"assets/temp/final_{id(context)}.mp4"
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio_codec="aac",
                threads=4,
                preset="medium"
            )
            
            return SkillResult.ok(
                data={
                    "video_url": output_path,
                    "duration": final_video.duration,
                    "resolution": resolution
                },
                message="视频合成成功"
            )
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="视频合成失败"
            )

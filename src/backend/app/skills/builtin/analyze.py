"""
内置技能实现 - 视频分析与解析类
"""

import json
from typing import Dict, Any, List
from app.skills.base import BaseSkill, SkillContext, SkillResult, SkillCategory, skill
from app.core.ai.router import model_router


@skill(
    name="视频解析器",
    category=SkillCategory.ANALYZE,
    version="1.0.0",
    description="全面解析视频的语言风格、画面风格、呈现效果等维度",
    author="SafeVideo Forge",
    inputs={"video_url": str},
    outputs={"report": dict},
    config_schema={
        "analyze_dimensions": {"type": "array", "default": ["language", "visual", "impact", "quality", "viral_potential"]},
        "sample_frames": {"type": "integer", "default": 10},
        "extract_audio": {"type": "boolean", "default": True}
    }
)
class VideoAnalyzerSkill(BaseSkill):
    """视频综合分析技能"""
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_url = context.get("video_url", "")
        dimensions = self.config.get("analyze_dimensions", 
                                    ["language", "visual", "impact", "quality", "viral_potential"])
        sample_frames = self.config.get("sample_frames", 10)
        
        try:
            # 1. 提取视频基础信息
            from moviepy.editor import VideoFileClip
            import cv2
            import numpy as np
            
            clip = VideoFileClip(video_url)
            
            # 基础信息
            duration = clip.duration
            fps = clip.fps
            width, height = clip.size
            
            # 2. 提取关键帧
            frames_info = []
            frame_times = [i * duration / (sample_frames + 1) for i in range(1, sample_frames + 1)]
            
            for t in frame_times:
                frame = clip.get_frame(t)
                
                # 颜色分析
                avg_color = np.mean(frame, axis=(0, 1))
                color_std = np.std(frame, axis=(0, 1))
                brightness = np.mean(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY))
                
                frames_info.append({
                    "time": t,
                    "avg_color": avg_color.tolist(),
                    "color_variance": color_std.tolist(),
                    "brightness": float(brightness)
                })
            
            # 3. 提取字幕/转录 (如果有)
            transcript = ""
            if clip.audio is not None:
                # 简化的音频分析
                audio = clip.audio
                audio_duration = audio.duration
                # 这里可以接入ASR进行语音转文字
                transcript = f"[音频时长: {audio_duration:.1f}秒]"
            
            clip.close()
            
            # 4. 使用AI进行深度分析
            visual_summary = self._summarize_visual(frames_info)
            
            analysis_prompt = f"""请作为专业短视频分析师，对以下视频进行深度分析：

视频基础信息：
- 时长: {duration:.1f}秒
- 分辨率: {width}x{height}
- 帧率: {fps}fps

视觉特征摘要：
{visual_summary}

音频/字幕：
{transcript}

请分析以下维度：
1. 语言风格（语气、节奏、表达方式）
2. 画面风格（色调、构图、转场风格）
3. 呈现效果（视觉冲击力、信息密度）
4. 质量标准（清晰度、专业度评级）
5. 平台传播效果（完播率预测、互动潜力评估）

请输出JSON格式分析报告。"""
            
            response = await model_router.chat([
                {"role": "system", "content": "你是一位专业的短视频内容分析师，擅长从多个维度评估视频质量。"},
                {"role": "user", "content": analysis_prompt}
            ])
            
            # 解析分析结果
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0:
                analysis = json.loads(response[json_start:json_end])
            else:
                analysis = {"raw_analysis": response}
            
            # 补充技术指标
            analysis["technical"] = {
                "duration": duration,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "aspect_ratio": "9:16" if height > width else "16:9" if width > height else "1:1",
                "avg_brightness": np.mean([f["brightness"] for f in frames_info]),
                "color_variance": np.mean([np.mean(f["color_variance"]) for f in frames_info])
            }
            
            return SkillResult.ok(
                data=analysis,
                message="视频解析完成"
            )
        
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="视频解析失败"
            )
    
    def _summarize_visual(self, frames_info: List[Dict]) -> str:
        """总结视觉特征"""
        brightness_values = [f["brightness"] for f in frames_info]
        avg_brightness = sum(brightness_values) / len(brightness_values)
        brightness_trend = "偏暗" if avg_brightness < 100 else "正常" if avg_brightness < 180 else "偏亮"
        
        return f"""- 整体亮度: {brightness_trend} (均值: {avg_brightness:.1f})
- 采样帧数: {len(frames_info)}
- 色彩变化: {"丰富" if np.std(brightness_values) > 30 else "稳定"}"""


@skill(
    name="质量检测器",
    category=SkillCategory.QUALITY,
    version="1.0.0",
    description="自动检查视频各元素质量",
    author="SafeVideo Forge",
    inputs={"video_url": str},
    outputs={"quality_report": dict, "pass": bool},
    config_schema={
        "check_resolution": {"type": "boolean", "default": True},
        "check_audio": {"type": "boolean", "default": True},
        "check_duration": {"type": "boolean", "default": True},
        "min_resolution": {"type": "string", "default": "720x1280"}
    }
)
class QualityCheckerSkill(BaseSkill):
    """质量检测技能"""
    
    async def execute(self, context: SkillContext) -> SkillResult:
        video_url = context.get("video_url", "")
        
        try:
            from moviepy.editor import VideoFileClip
            import numpy as np
            
            clip = VideoFileClip(video_url)
            checks = {}
            issues = []
            
            # 1. 分辨率检查
            w, h = clip.size
            min_w, min_h = map(int, self.config.get("min_resolution", "720x1280").split("x"))
            checks["resolution"] = {
                "actual": f"{w}x{h}",
                "required": f"{min_w}x{min_h}",
                "pass": w >= min_w and h >= min_h
            }
            if not checks["resolution"]["pass"]:
                issues.append(f"分辨率不足: {w}x{h} < {min_w}x{min_h}")
            
            # 2. 时长检查
            checks["duration"] = {
                "actual": clip.duration,
                "pass": 3 <= clip.duration <= 180  # 3秒到3分钟
            }
            if not checks["duration"]["pass"]:
                issues.append(f"时长不合适: {clip.duration:.1f}秒")
            
            # 3. 音频检查
            has_audio = clip.audio is not None
            checks["audio"] = {
                "has_audio": has_audio,
                "pass": has_audio
            }
            if not has_audio:
                issues.append("缺少音频轨道")
            
            # 4. 画面质量检查（帧清晰度）
            frame = clip.get_frame(0)
            gray = np.mean(frame, axis=2)
            variance = np.var(gray)
            checks["sharpness"] = {
                "variance": float(variance),
                "pass": variance > 100  # 简单的清晰度阈值
            }
            if not checks["sharpness"]["pass"]:
                issues.append("画面可能偏模糊")
            
            # 5. 帧率检查
            checks["fps"] = {
                "actual": clip.fps,
                "pass": clip.fps >= 24
            }
            if not checks["fps"]["pass"]:
                issues.append(f"帧率偏低: {clip.fps}fps")
            
            clip.close()
            
            all_pass = all(c["pass"] for c in checks.values() if "pass" in c)
            
            report = {
                "overall_pass": all_pass and len(issues) == 0,
                "checks": checks,
                "issues": issues,
                "suggestions": self._generate_suggestions(checks, issues)
            }
            
            return SkillResult.ok(
                data=report,
                message="质量检测完成" + (" ✅" if report["overall_pass"] else " ⚠️")
            )
        
        except Exception as e:
            return SkillResult.fail(
                error=str(e),
                message="质量检测失败"
            )
    
    def _generate_suggestions(self, checks: Dict, issues: List[str]) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        if not checks.get("resolution", {}).get("pass", True):
            suggestions.append("建议提高视频分辨率至1080x1920以上")
        
        if not checks.get("fps", {}).get("pass", True):
            suggestions.append("建议将帧率提升至30fps以获得更流畅的观感")
        
        if not checks.get("audio", {}).get("pass", True):
            suggestions.append("建议添加背景音乐和旁白解说")
        
        if not checks.get("sharpness", {}).get("pass", True):
            suggestions.append("建议使用更清晰的素材或进行锐化处理")
        
        return suggestions

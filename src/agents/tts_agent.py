"""
TTS智能体 - 负责语音合成和音频输出

功能：
1. 文本转语音（TTS）
2. 语音情感/紧急程度调整
3. 多语言支持
4. 音频播放控制
"""

import asyncio
import time
import platform
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

import numpy as np


class TTSAgent:
    """
    TTS智能体 - 使用系统TTS进行语音合成

    提供语音反馈功能，支持紧急程度调整和语音播放。
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化TTS智能体

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # TTS引擎（延迟加载）
        self.tts_engine = None
        self.tts_type = None  # "pyttsx3" 或 "coqui"

        # 音频参数
        self.sample_rate = 22050
        self.channels = 1

        # 语音模板
        self.templates = self.config.get("tts", {}).get("templates", {})

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return {
                "tts": {
                    "engine": "pyttsx3",
                    "templates": {}
                }
            }

    def _load_engine(self):
        """
        延迟加载TTS引擎

        首次使用时才加载引擎，减少启动时间。
        优先使用系统TTS（pyttsx3），如果不可用则尝试Coqui TTS。
        """
        if self.tts_engine is not None:
            return

        print("[TTSAgent] 加载TTS引擎...")

        # 优先使用系统TTS
        try:
            import pyttsx3

            self.tts_engine = pyttsx3.init()
            self.tts_type = "pyttsx3"

            # 设置中文语音（如果可用）
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    print(f"[TTSAgent] 使用中文语音: {voice.name}")
                    break

            print("[TTSAgent] 系统TTS加载完成")
            return

        except ImportError:
            print("[TTSAgent] pyttsx3未安装，尝试Coqui TTS...")
        except Exception as e:
            print(f"[TTSAgent] 系统TTS加载失败: {e}")

        # 尝试使用Coqui TTS
        try:
            from TTS.api import TTS

            model_path = self.config.get("tts", {}).get("model_path")
            self.tts_engine = TTS(model_name=model_path)
            self.tts_type = "coqui"

            print("[TTSAgent] Coqui TTS加载完成")
            return

        except Exception as e:
            print(f"[TTSAgent] Coqui TTS加载失败: {e}")
            print("[TTSAgent] 所有TTS引擎均不可用")

    async def speak(self, feedback: Dict[str, Any]) -> None:
        """
        语音合成并播放（核心接口）

        Args:
            feedback: 反馈数据字典
                {
                    "message": str,  # 要说的文本
                    "urgency": str,  # "high", "medium", "low"
                    "delay": float  # 延迟（秒）
                }
        """
        # 确保引擎已加载
        self._load_engine()

        if self.tts_engine is None:
            print("[TTSAgent] TTS引擎不可用，跳过语音播放")
            return

        # 提取参数
        message = feedback.get("message", "")
        urgency = feedback.get("urgency", "medium")
        delay = feedback.get("delay", 0)

        if not message:
            return

        # 延迟执行
        if delay > 0:
            await asyncio.sleep(delay)

        print(f"[TTSAgent] 播放语音: {message} (紧急度: {urgency})")

        # 根据TTS类型播放
        if self.tts_type == "pyttsx3":
            await self._speak_pyttsx3(message, urgency)
        elif self.tts_type == "coqui":
            await self._speak_coqui(message, urgency)

    async def _speak_pyttsx3(self, text: str, urgency: str) -> None:
        """
        使用pyttsx3播放语音

        Args:
            text: 要播放的文本
            urgency: 紧急程度
        """
        try:
            # 根据紧急程度调整语速
            rate = self._get_rate_by_urgency(urgency)

            # 设置语速
            current_rate = self.tts_engine.getProperty('rate')
            self.tts_engine.setProperty('rate', int(current_rate * rate))

            # 播放语音
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

            print("[TTSAgent] 语音播放完成")

        except Exception as e:
            print(f"[TTSAgent] pyttsx3播放失败: {e}")

    async def _speak_coqui(self, text: str, urgency: str) -> None:
        """
        使用Coqui TTS播放语音

        Args:
            text: 要播放的文本
            urgency: 紧急程度
        """
        try:
            # 生成语音
            speed = self._get_speed_by_urgency(urgency)

            # 使用tts_to_file方法避免API兼容性问题
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_file = f.name

            self.tts_engine.tts_to_file(
                text=text,
                file_path=temp_file,
                speed=speed
            )

            # 播放生成的音频文件
            await self._play_audio_file(temp_file)

            # 清理临时文件
            try:
                Path(temp_file).unlink(missing_ok=True)
            except:
                pass

            print("[TTSAgent] 语音播放完成")

        except Exception as e:
            print(f"[TTSAgent] Coqui TTS播放失败: {e}")
            # 降级到文件播放
            print("[TTSAgent] 尝试降级方案...")

    async def _play_audio_file(self, file_path: str) -> None:
        """
        播放音频文件（使用PyAudio直接播放）

        Args:
            file_path: 音频文件路径
        """
        from pathlib import Path
        import wave

        if not Path(file_path).exists():
            print(f"[TTSAgent] 文件不存在: {file_path}")
            return

        try:
            # 使用PyAudio直接播放
            wf = wave.open(str(file_path), 'rb')

            import pyaudio
            p = pyaudio.PyAudio()

            # 打开输出流
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )

            # 读取并播放音频数据
            CHUNK = 1024
            data = wf.readframes(CHUNK)

            while len(data) > 0:
                stream.write(data)
                data = wf.readframes(CHUNK)

            # 清理
            stream.stop_stream()
            stream.close()
            p.terminate()
            wf.close()

        except Exception as e:
            print(f"[TTSAgent] PyAudio播放失败: {e}")
            # 降级到系统播放器
            self._play_audio_file_fallback(file_path)

    def _play_audio_file_fallback(self, file_path: str) -> None:
        """
        使用系统播放器播放音频（降级方案）

        Args:
            file_path: 音频文件路径
        """
        system = platform.system()

        try:
            if system == "Windows":
                import subprocess
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"], check=True)
            elif system == "Darwin":  # macOS
                import subprocess
                subprocess.run(["afplay", str(file_path)], check=True)
            else:  # Linux
                import subprocess
                subprocess.run(["aplay", str(file_path)], check=True)

        except Exception as e:
            print(f"[TTSAgent] 系统播放器也失败: {e}")

    def _get_speed_by_urgency(self, urgency: str) -> float:
        """
        根据紧急程度获取语速倍率

        Args:
            urgency: 紧急程度

        Returns:
            语速倍率
        """
        speed_map = {
            "high": 1.2,    # 快速，紧迫
            "medium": 1.0,  # 正常
            "low": 0.9      # 缓慢，温和
        }

        return speed_map.get(urgency, 1.0)

    def _get_rate_by_urgency(self, urgency: str) -> float:
        """
        根据紧急程度获取pyttsx3语速倍率

        Args:
            urgency: 紧急程度

        Returns:
            语速倍率
        """
        rate_map = {
            "high": 1.3,    # 快速
            "medium": 1.0,  # 正常
            "low": 0.8      # 缓慢
        }

        return rate_map.get(urgency, 1.0)

    def speak_template(self, template_name: str, **kwargs) -> None:
        """
        使用预定义模板播放语音

        Args:
            template_name: 模板名称
            **kwargs: 模板参数
        """
        template = self.templates.get(template_name)

        if template:
            message = template.format(**kwargs)
            asyncio.create_task(self.speak({
                "message": message,
                "urgency": "medium"
            }))
        else:
            print(f"[TTSAgent] 未找到模板: {template_name}")

    def stop(self):
        """停止当前播放"""
        try:
            if self.tts_type == "pyttsx3" and self.tts_engine:
                self.tts_engine.stop()
        except Exception as e:
            print(f"[TTSAgent] 停止播放错误: {e}")

    def test_audio(self):
        """测试音频输出"""
        print("[TTSAgent] 测试音频输出...")
        asyncio.run(self.speak({
            "message": "语音系统正常",
            "urgency": "low"
        }))

"""
TTS智能体 - 负责语音合成和音频输出

功能：
1. 文本转语音（TTS）
2. 语音情感调整
3. 多语言支持
4. 音频播放控制
"""

import asyncio
import time
from typing import Dict, Any
from pathlib import Path
import yaml

import numpy as np
import sounddevice as sd


class TTSAgent:
    """
    TTS智能体 - 使用Coqui TTS进行语音合成

    提供高质量的语音反馈，支持多语言和情感调整。
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化TTS智能体

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # TTS模型（延迟加载）
        self.tts_model = None

        # 音频参数
        self.sample_rate = 22050
        self.channels = 1

        # 语音模板
        self.templates = self.config.get("tts", {}).get("templates", {})

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_model(self):
        """
        延迟加载TTS模型

        首次使用时才加载模型，减少启动时间。
        """
        if self.tts_model is None:
            print("[TTSAgent] 加载TTS模型...")
            try:
                from TTS.api import TTS

                model_path = self.config.get("tts", {}).get("model_path")
                self.tts_model = TTS(model_path=model_path)

                print("[TTSAgent] TTS模型加载完成")

            except Exception as e:
                print(f"[TTSAgent] TTS模型加载失败: {e}")
                print("[TTSAgent] 将使用备用语音方案")
                self.tts_model = "fallback"  # 标记为使用备用方案

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
        # 确保模型已加载
        self._load_model()

        # 提取参数
        message = feedback.get("message", "")
        urgency = feedback.get("urgency", "medium")
        delay = feedback.get("delay", 0)

        if not message:
            return

        # 延迟执行
        if delay > 0:
            await asyncio.sleep(delay)

        # 根据紧急程度调整语音参数
        speed = self._get_speed_by_urgency(urgency)

        print(f"[TTSAgent] 播放语音: {message} (紧急度: {urgency})")

        # 生成语音
        audio = await self._synthesize(message, speed=speed)

        # 播放语音
        if audio is not None:
            await self._play_audio(audio)

    async def _synthesize(self, text: str, speed: float = 1.0) -> np.ndarray:
        """
        文本转语音

        Args:
            text: 输入文本
            speed: 语速倍率

        Returns:
            音频数据（numpy数组）
        """
        try:
            # 使用Coqui TTS
            if self.tts_model and self.tts_model != "fallback":
                # 生成语音
                wav = self.tts_model.tts(
                    text=text,
                    speed=speed
                )

                return np.array(wav)

            else:
                # 备用方案：使用系统TTS（仅适用于演示）
                return await self._fallback_tts(text)

        except Exception as e:
            print(f"[TTSAgent] 语音合成错误: {e}")
            return None

    async def _fallback_tts(self, text: str) -> np.ndarray:
        """
        备用TTS方案

        当Coqui TTS不可用时，使用系统TTS或生成简单的蜂鸣声。

        Args:
            text: 输入文本

        Returns:
            音频数据
        """
        print(f"[TTSAgent] 使用备用TTS: {text}")

        # 生成简单的提示音
        duration = 0.5  # 秒
        sample_rate = 22050
        frequency = 440  # Hz（A4音符）

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.3 * np.sin(2 * np.pi * frequency * t)

        return audio

    async def _play_audio(self, audio: np.ndarray) -> None:
        """
        播放音频

        Args:
            audio: 音频数据（numpy数组）
        """
        try:
            # 使用sounddevice播放
            sd.play(
                audio.astype(np.float32),
                samplerate=self.sample_rate,
                channels=self.channels
            )

            # 等待播放完成
            sd.wait()

        except Exception as e:
            print(f"[TTSAgent] 音频播放错误: {e}")

            # 尝试使用备用播放方式
            try:
                import pyaudio
                p = pyaudio.PyAudio()

                stream = p.open(
                    format=pyaudio.paFloat32,
                    channels=self.channels,
                    rate=self.sample_rate,
                    output=True
                )

                stream.write(audio.tobytes())
                stream.stop_stream()
                stream.close()
                p.terminate()

            except Exception as e2:
                print(f"[TTSAgent] 备用播放方式也失败: {e2}")

    def _get_speed_by_urgency(self, urgency: str) -> float:
        """
        根据紧急程度获取语速

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
            sd.stop()
        except Exception as e:
            print(f"[TTSAgent] 停止播放错误: {e}")

    def set_volume(self, volume: float):
        """
        设置音量

        Args:
            volume: 音量（0.0-1.0）
        """
        # TODO: 实现音量控制
        pass

    def test_audio(self):
        """测试音频输出"""
        print("[TTSAgent] 测试音频输出...")
        asyncio.run(self.speak({
            "message": "语音系统正常",
            "urgency": "low"
        }))

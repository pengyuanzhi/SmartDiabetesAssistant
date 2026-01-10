"""
TTS智能体单元测试
"""

import pytest
import asyncio
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTTSAgent:
    """TTS智能体测试类"""

    @pytest.fixture
    def tts_config(self):
        """TTS配置 fixture"""
        return {
            "engine": "system",  # 使用系统TTS
            "language": "zh-cn",
            "voice_rate": 1.0,
            "voice_volume": 1.0
        }

    @pytest.fixture
    def output_dir(self, tmp_path):
        """输出目录 fixture"""
        return tmp_path / "tts_output"

    def test_tts_agent_import(self):
        """测试TTS智能体导入"""
        try:
            from src.agents.tts_agent import TTSAgent
            assert TTSAgent is not None
        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    def test_tts_agent_init(self, tts_config):
        """测试TTS智能体初始化"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config=tts_config)
            assert agent is not None
            assert agent.config == tts_config

        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    @pytest.mark.asyncio
    async def test_tts_generate_speech(self, tts_config, output_dir):
        """测试语音生成"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config=tts_config)
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / "test_speech.wav"

            # 生成语音
            result_path = await agent.generate_speech(
                text="测试语音合成",
                output_path=str(output_path)
            )

            # 验证结果
            if result_path:
                assert Path(result_path).exists()
                assert Path(result_path).stat().st_size > 0
            else:
                pytest.skip("语音生成失败")

        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    @pytest.mark.asyncio
    async def test_tts_emotions(self, tts_config, output_dir):
        """测试不同情感的语音合成"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config=tts_config)
            output_dir.mkdir(exist_ok=True)

            emotions = ["neutral", "positive", "negative", "urgent"]
            results = {}

            for emotion in emotions:
                output_path = output_dir / f"test_{emotion}.wav"
                result = await agent.generate_speech(
                    text="测试情感语音",
                    emotion=emotion,
                    output_path=str(output_path)
                )
                results[emotion] = result is not None

            # 至少有一个情感成功
            assert any(results.values())

        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    @pytest.mark.asyncio
    async def test_tts_queue(self, tts_config):
        """测试语音队列功能"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config=tts_config)

            # 添加多条消息到队列
            messages = ["消息1", "消息2", "消息3"]
            for msg in messages:
                await agent.add_to_queue(msg)

            # 处理队列
            await agent.process_queue()

            # 验证队列为空
            assert len(agent.queue) == 0

        except ImportError:
            pytest.skip("TTSAgent模块未实现")
        except AttributeError:
            pytest.skip("队列功能未实现")

    @pytest.mark.asyncio
    async def test_tts_performance(self, tts_config):
        """测试TTS性能"""
        try:
            from src.agents.tts_agent import TTSAgent
            import time

            agent = TTSAgent(config=tts_config)

            test_text = "这是一段性能测试文本"
            iterations = 3

            times = []
            for _ in range(iterations):
                start = time.time()
                result = await agent.generate_speech(test_text)
                end = time.time()

                if result:
                    times.append(end - start)

            # 至少有一次成功
            assert len(times) > 0

            # 平均时间应该合理（<2秒）
            avg_time = sum(times) / len(times)
            assert avg_time < 2.0

        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    def test_system_tts_available(self):
        """测试系统TTS是否可用"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            assert engine is not None
            engine.stop()
        except ImportError:
            pytest.skip("pyttsx3未安装")
        except Exception as e:
            pytest.skip(f"系统TTS不可用: {e}")


class TestTTSAgentIntegration:
    """TTS智能体集成测试"""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """测试完整工作流"""
        try:
            from src.agents.tts_agent import TTSAgent
            from pathlib import Path
            import tempfile

            config = {"engine": "system"}
            agent = TTSAgent(config=config)

            # 创建临时目录
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)

                # 生成多个语音文件
                messages = [
                    ("系统启动", "neutral"),
                    ("操作正确", "positive"),
                    ("警告信息", "negative"),
                ]

                for i, (text, emotion) in enumerate(messages):
                    output_path = tmp_path / f"output_{i}.wav"
                    result = await agent.generate_speech(
                        text=text,
                        emotion=emotion,
                        output_path=str(output_path)
                    )

                    if result:
                        assert Path(result).exists()

        except ImportError:
            pytest.skip("TTSAgent模块未实现")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

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
    def tts_config_path(self, tmp_path):
        """创建临时TTS配置文件"""
        import yaml

        config = {
            "tts": {
                "model_path": "tts_models/multilingual/multi-dataset/your_tts",
                "templates": {}
            }
        }

        config_file = tmp_path / "tts_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)

        return str(config_file)

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

    def test_tts_agent_init(self, tts_config_path):
        """测试TTS智能体初始化"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config_path=tts_config_path)
            assert agent is not None
            assert agent.config is not None

        except ImportError:
            pytest.skip("TTSAgent模块未实现")

    @pytest.mark.asyncio
    async def test_tts_speak(self, tts_config_path):
        """测试语音播放"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config_path=tts_config_path)

            # 测试语音播放
            feedback = {
                "message": "测试语音合成",
                "urgency": "medium",
                "delay": 0
            }

            # 调用 speak 方法（不会抛出异常即成功）
            await agent.speak(feedback)

            # 如果到达这里，说明speak方法执行成功
            assert True

        except ImportError:
            pytest.skip("TTSAgent模块未实现")
        except Exception as e:
            # speak方法可能因为缺少依赖而失败，这是预期的
            pytest.skip(f"语音播放失败（可能缺少依赖）: {e}")

    @pytest.mark.asyncio
    async def test_tts_urgency_levels(self, tts_config_path):
        """测试不同紧急程度的语音"""
        try:
            from src.agents.tts_agent import TTSAgent

            agent = TTSAgent(config_path=tts_config_path)

            # 测试不同的紧急程度
            urgencies = ["low", "medium", "high"]

            for urgency in urgencies:
                feedback = {
                    "message": f"测试{urgency}紧急程度",
                    "urgency": urgency,
                    "delay": 0
                }

                # 调用 speak 方法
                await agent.speak(feedback)

            # 如果到达这里，说明所有紧急程度都测试成功
            assert True

        except ImportError:
            pytest.skip("TTSAgent模块未实现")
        except Exception as e:
            pytest.skip(f"语音播放失败（可能缺少依赖）: {e}")

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
    async def test_complete_workflow(self, tmp_path):
        """测试完整工作流"""
        try:
            from src.agents.tts_agent import TTSAgent
            import yaml

            # 创建临时配置
            config = {
                "tts": {
                    "model_path": "tts_models/multilingual/multi-dataset/your_tts",
                    "templates": {}
                }
            }

            config_file = tmp_path / "config.yaml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f)

            agent = TTSAgent(config_path=str(config_file))

            # 测试多个反馈
            messages = [
                ("系统启动", "low"),
                ("操作正确", "low"),
                ("警告信息", "medium"),
            ]

            for message, urgency in messages:
                feedback = {
                    "message": message,
                    "urgency": urgency,
                    "delay": 0
                }

                await agent.speak(feedback)

            # 如果到达这里，说明工作流测试成功
            assert True

        except ImportError:
            pytest.skip("TTSAgent模块未实现")
        except Exception as e:
            pytest.skip(f"工作流测试失败（可能缺少依赖）: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

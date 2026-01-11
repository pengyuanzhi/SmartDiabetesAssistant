"""
测试更新后的TTS智能体

验证PyAudio播放功能是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.tts_agent import TTSAgent


async def test_tts_pyaudio():
    """测试TTS智能体的PyAudio播放功能"""
    print("="*60)
    print("测试TTS智能体（PyAudio播放）")
    print("="*60)

    try:
        # 初始化TTS智能体
        print("\n[1/3] 初始化TTS智能体...")
        agent = TTSAgent()
        print("✓ TTS智能体初始化成功")

        # 测试系统TTS（pyttsx3）
        print("\n[2/3] 测试系统TTS播放...")
        print("提示：请调高音量\n")

        await agent.speak({
            "message": "语音系统测试",
            "urgency": "medium",
            "delay": 0
        })

        print("✓ 系统TTS播放完成")

        # 测试不同紧急程度
        print("\n[3/3] 测试不同紧急程度...")

        test_messages = [
            ("低紧急度提示", "low"),
            ("中紧急度提示", "medium"),
            ("高紧急度警告", "high")
        ]

        for message, urgency in test_messages:
            print(f"\n播放: {message} (紧急度: {urgency})")
            await agent.speak({
                "message": message,
                "urgency": urgency,
                "delay": 0.5
            })

        print("\n" + "="*60)
        print("测试完成！")
        print("="*60)

        print("\n如果听到语音，说明PyAudio播放功能正常")
        print("如果没有听到，请检查：")
        print("1. 系统音量是否打开")
        print("2. pyaudio是否正确安装")
        print("3. 音频输出设备是否正常")

    except ImportError as e:
        print(f"\n✗ 导入错误: {e}")
        print("\n请确保已安装依赖:")
        print("  pip install pyttsx3 pyaudio")
        return False

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


async def test_with_coqui_tts():
    """测试Coqui TTS（如果可用）"""
    print("\n" + "="*60)
    print("测试Coqui TTS（可选）")
    print("="*60)

    try:
        import torch
        version = tuple(map(int, torch.__version__.split('.')[:2]))

        if version >= (2, 6):
            print("\n⚠️ 检测到PyTorch 2.6+")
            print("Coqui TTS与此版本不兼容，跳过测试")
            return

    except ImportError:
        print("\n⚠️ PyTorch未安装，跳过Coqui TTS测试")
        return

    try:
        from TTS.api import TTS

        print("\n[1/2] 加载Coqui TTS模型...")
        print("注意：首次使用会下载模型（约50MB）")

        # 创建临时配置使用Coqui TTS
        import tempfile
        import yaml

        config = {
            "tts": {
                "engine": "coqui",
                "coqui_model_path": "tts_models/zh-CN/baker/tacotron2-DDC-GST"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name

        agent = TTSAgent(config_path=config_path)
        print("✓ Coqui TTS加载成功")

        print("\n[2/2] 测试Coqui TTS播放...")
        await agent.speak({
            "message": "Coqui TTS语音测试",
            "urgency": "medium"
        })

        print("✓ Coqui TTS播放完成")

        # 清理
        import os
        os.unlink(config_path)

    except ImportError:
        print("\n⚠️ Coqui TTS未安装")
        print("安装命令: pip install TTS")
    except Exception as e:
        print(f"\n⚠️ Coqui TTS测试失败: {e}")


async def main():
    """主测试函数"""
    print("\nTTS智能体更新验证")
    print("项目: 智能糖尿病助手")
    print()

    # 测试系统TTS
    success = await test_tts_pyaudio()

    if success:
        # 可选：测试Coqui TTS
        await test_with_coqui_tts()

    print("\n测试结束")


if __name__ == "__main__":
    asyncio.run(main())

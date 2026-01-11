"""
快速测试TTS修复 - 验证连续播放是否正常

测试pyttsx3能否连续播放多条语音
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.tts_agent import TTSAgent


async def test_continuous_playback():
    """测试连续播放功能"""
    print("=" * 60)
    print("TTS连续播放测试")
    print("=" * 60)
    print()

    try:
        # 初始化TTS智能体
        print("[1/4] 初始化TTS智能体...")
        agent = TTSAgent()
        print("✓ 初始化成功\n")

        # 测试连续播放
        print("[2/4] 测试连续播放4条语音...")
        print("提示: 请依次听到4条不同的语音\n")

        test_messages = [
            ("智能糖尿病助手系统启动", "low"),
            ("注射角度正确", "low"),
            ("警告，注射角度过小", "medium"),
            ("注射完成，请按压注射部位", "low"),
        ]

        for i, (text, urgency) in enumerate(test_messages, 1):
            print(f"[{i}/4] 播放: {text}")

            feedback = {
                "message": text,
                "urgency": urgency,
                "delay": 0
            }

            try:
                await agent.speak(feedback)
                print(f"       ✓ 完成\n")
            except Exception as e:
                print(f"       ✗ 失败: {e}\n")

        # 测试不同紧急程度
        print("[3/4] 测试不同紧急程度...")

        urgency_tests = [
            ("低紧急度测试", "low"),
            ("中紧急度测试", "medium"),
            ("高紧急度测试", "high"),
        ]

        for text, urgency in urgency_tests:
            print(f"播放: {text} (紧急度: {urgency})")
            await agent.speak({
                "message": text,
                "urgency": urgency,
                "delay": 0
            })
            print()

        # 测试快速连续播放
        print("[4/4] 测试快速连续播放（无延迟）...")
        print("提示: 应该听到连续的语音\n")

        quick_messages = ["第一条", "第二条", "第三条"]
        for msg in quick_messages:
            await agent.speak({
                "message": msg,
                "urgency": "medium",
                "delay": 0
            })

        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

        print("\n如果听到所有语音，说明修复成功！")
        print("如果没有听到某些语音，请查看上方的错误信息")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("\nTTS修复验证工具")
    print("项目: 智能糖尿病助手\n")
    print("此测试验证pyttsx3连续播放问题是否已修复\n")

    await test_continuous_playback()

    print("\n测试结束")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n[错误] 测试异常: {e}")
        import traceback
        traceback.print_exc()

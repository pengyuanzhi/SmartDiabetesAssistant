"""
测试主程序场景中的TTS播放

模拟主程序中可能出现的连续播放场景
"""

import asyncio
import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.tts_agent import TTSAgent


async def test_main_agent_scenario():
    """测试主程序场景"""
    print("=" * 60)
    print("主程序TTS场景测试")
    print("=" * 60)
    print()

    try:
        # 检查配置文件
        config_path = "config/model_config.yaml"

        if os.path.exists(config_path):
            agent = TTSAgent(config_path=config_path)
        else:
            print("[提示] 配置文件不存在，使用默认配置")
            agent = TTSAgent()

        print("✓ TTSAgent初始化成功\n")

        # 场景1: 启动监测会话
        print("[1/4] 测试启动监测会话...")
        print("(应该听到：开始监测，请按照标准流程操作)\n")

        await agent.speak({
            "message": "开始监测，请按照标准流程操作",
            "urgency": "low",
            "delay": 0
        })

        print("✓ 启动监测完成\n")

        # 等待用户确认
        input("按回车继续...")

        # 场景2: 模拟多告警同时触发（并发播放）
        print("[2/4] 测试多告警并发播放...")
        print("(应该听到3条不同的语音)\n")

        alerts = [
            {"message": "警告，注射角度过小，请调整至45度以上", "urgency": "high"},
            {"message": "注射速度过快，请减慢", "urgency": "medium"},
            {"message": "请保持注射姿势", "urgency": "low"}
        ]

        for i, alert in enumerate(alerts, 1):
            print(f"[{i}/3] 播放: {alert['message']}")
            await agent.speak({
                "message": alert["message"],
                "urgency": alert["urgency"],
                "delay": 0
            })
            print(f"✓ 完成\n")
            await asyncio.sleep(0.5)

        print("✓ 多告警播放完成\n")

        # 等待用户确认
        input("按回车继续...")

        # 场景3: 连续监测反馈（高频播放）
        print("[3/4] 测试连续监测反馈...")
        print("(模拟连续4帧，每帧都可能触发语音)\n")

        test_frames = [
            {"angle": 30.0, "speed": 5.0, "has_alert": True, "message": "角度30度偏小"},
            {"angle": 60.0, "speed": 3.0, "has_alert": False, "message": "操作正确"},
            {"angle": 25.0, "speed": 8.0, "has_alert": True, "message": "速度过快"},
            {"angle": 75.0, "speed": 2.0, "has_alert": False, "message": "保持姿势"},
        ]

        for i, frame_data in enumerate(test_frames, 1):
            print(f"[{i}/4] 帧{frame_data['angle']:.0f}度, 速度{frame_data['speed']:.1f}")

            # 模拟反馈
            if frame_data["has_alert"]:
                await agent.speak({
                    "message": frame_data["message"],
                    "urgency": "medium",
                    "delay": 0
                })
                print(f"  ✓ 播放完成\n")
            else:
                print(f"  → 无告警\n")

            await asyncio.sleep(0.3)

        print("✓ 连续监测完成\n")

        # 等待用户确认
        input("按回车继续...")

        # 场景4: 快速连续播放（压力测试）
        print("[4/4] 测试快速连续播放...")
        print("(连续播放6条短语音)\n")

        quick_messages = [
            "第一条", "第二条", "第三条",
            "第四条", "第五条", "第六条"
        ]

        for i, msg in enumerate(quick_messages, 1):
            print(f"[{i}/6] {msg}")
            await agent.speak({
                "message": msg,
                "urgency": "medium",
                "delay": 0
            })

        print("\n✓ 快速连续播放完成\n")

        print("=" * 60)
        print("主程序场景测试完成!")
        print("=" * 60)

        print("\n如果所有语音都能正常播放，说明主程序中的问题已修复")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("\n主程序TTS场景验证工具")
    print("项目: 智能糖尿病助手\n")
    print("此测试验证主程序中的TTS播放场景\n")

    await test_main_agent_scenario()

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

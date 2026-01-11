"""
测试主程序场景中的TTS播放

模拟主程序中可能出现的连续播放场景
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.main_agent import MainAgent
from src.agents.tts_agent import TTSAgent


async def test_main_agent_scenario():
    """测试主程序场景"""
    print("=" * 60)
    print("主程序TTS场景测试")
    print("=" * 60)
    print()

    try:
        # 初始化MainAgent
        print("[1/4] 初始化MainAgent...")
        agent = MainAgent()
        print("✓ MainAgent初始化成功\n")

        # 场景1: 启动监测会话
        print("[2/4] 测试启动监测会话...")
        print("(应该听到：开始监测，请按照标准流程操作)\n")

        await agent.start_monitoring(
            session_id="test_session_001",
            user_profile={"name": "测试用户"}
        )

        print("✓ 启动监测完成\n")

        # 等待用户确认
        input("按回车继续...")

        # 场景2: 模拟多告警同时触发（并发播放）
        print("[3/4] 测试多告警并发播放...")
        print("(应该听到3条不同的语音)\n")

        # 创建测试状态
        from src.agents.main_agent import AgentState

        test_state = {
            "messages": [],
            "video_frame": {},
            "pose_data": {},
            "injection_site": {},
            "injection_angle": 0.0,
            "injection_speed": 0.0,
            "injection_duration": 0.0,
            "current_step": "injection_deliver",
            "step_start_time": 0.0,
            "alerts": [
                {
                    "type": "angle_error",
                    "severity": "critical",
                    "message": "警告，注射角度过小，请调整至45度以上"
                },
                {
                    "type": "speed_warning",
                    "severity": "warning",
                    "message": "注射速度过快，请减慢"
                },
                {
                    "type": "info",
                    "severity": "info",
                    "message": "请保持注射姿势"
                }
            ],
            "feedback_history": [],
            "user_profile": {},
            "session_id": "test"
        }

        # 执行多模态输出节点（会并发播放3条语音）
        await agent._multimodal_output_node(test_state)

        print("✓ 多告警播放完成\n")

        # 等待用户确认
        input("按回车继续...")

        # 场景3: 连续监测反馈（高频播放）
        print("[4/4] 测试连续监测反馈...")
        print("(模拟连续4帧，每帧都可能触发语音)\n")

        test_frames = [
            {"angle": 30.0, "speed": 5.0, "has_alert": True},
            {"angle": 60.0, "speed": 3.0, "has_alert": False},
            {"angle": 25.0, "speed": 8.0, "has_alert": True},
            {"angle": 75.0, "speed": 2.0, "has_alert": False},
        ]

        for i, frame_data in enumerate(test_frames, 1):
            print(f"[{i}/4] 帧{frame_data}")

            # 根据帧数据生成告警
            alerts = []
            if frame_data["has_alert"]:
                if frame_data["angle"] < 45:
                    alerts.append({
                        "type": "angle",
                        "severity": "warning",
                        "message": f"角度{frame_data['angle']:.0f}度偏小"
                    })
                if frame_data["speed"] > 4.0:
                    alerts.append({
                        "type": "speed",
                        "severity": "warning",
                        "message": "速度过快"
                    })

            # 更新状态
            test_state["alerts"] = alerts
            test_state["injection_angle"] = frame_data["angle"]
            test_state["injection_speed"] = frame_data["speed"]

            # 执行反馈
            if alerts:
                await agent._multimodal_output_node(test_state)

        print("✓ 连续监测完成\n")

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

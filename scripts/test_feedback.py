"""
测试多模态反馈系统

测试语音、震动、视觉等多模态反馈的协调和输出
"""

import sys
import asyncio
from pathlib import Path
from enum import Enum

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """告警类型"""
    ANGLE_INCORRECT = "angle_incorrect"
    SITE_INCORRECT = "site_incorrect"
    SPEED_TOO_FAST = "speed_too_fast"
    SPEED_TOO_SLOW = "speed_too_slow"
    OPERATION_CORRECT = "operation_correct"
    INJECTION_COMPLETE = "injection_complete"
    SYSTEM_READY = "system_ready"


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def test_audio_feedback():
    """测试音频反馈"""
    print_header("测试音频反馈")

    try:
        from src.agents.tts_agent import TTSAgent

        print("\n初始化TTS智能体...")
        print("提示: 使用系统TTS (pyttsx3) 进行测试")

        # 使用默认配置路径初始化
        try:
            tts_agent = TTSAgent()
        except:
            # 如果配置文件不存在，创建临时配置
            import tempfile
            import yaml

            temp_config = {
                "tts": {
                    "model_path": "tts_models/multilingual/multi-dataset/your_tts",
                    "templates": {}
                }
            }

            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(temp_config, f)
                temp_config_path = f.name

            tts_agent = TTSAgent(config_path=temp_config_path)

        # 测试不同级别的告警
        test_cases = [
            (AlertLevel.INFO, "系统就绪", "智能糖尿病助手已启动"),
            (AlertLevel.INFO, "操作正确", "注射角度正确"),
            (AlertLevel.WARNING, "角度警告", "注射角度偏小，请调整至45度以上"),
            (AlertLevel.CRITICAL, "紧急停止", "注射速度过快，请立即停止"),
        ]

        print("\n开始测试...\n")

        for level, alert_type, message in test_cases:
            print(f"[{level.value.upper()}] {alert_type}: {message}")

            try:
                # 根据级别选择紧急程度
                urgency = {
                    AlertLevel.INFO: "low",
                    AlertLevel.WARNING: "medium",
                    AlertLevel.CRITICAL: "high"
                }[level]

                # 使用 TTSAgent 的 speak 方法
                feedback = {
                    "message": message,
                    "urgency": urgency,
                    "delay": 0
                }

                print(f"  [播放中]...")

                # 播放语音
                await tts_agent.speak(feedback)

                print(f"  [完成] 语音播放完成")

            except Exception as e:
                print(f"  [错误] {e}")

            print()

        print("[成功] 音频反馈测试完成")
        return True

    except ImportError as e:
        print(f"[错误] 无法导入TTS智能体: {e}")
        print("提示: 请确保已安装 pyttsx3: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vibration_feedback():
    """测试震动反馈（PC端使用模拟模式）"""
    print_header("测试震动反馈")

    try:
        from src.agents.haptic_agent import HapticAgent

        print("\n初始化触觉智能体...")
        print("提示: PC端使用模拟模式（控制台输出）")

        haptic_agent = HapticAgent(config={})

        # 测试不同震动模式
        vibration_patterns = [
            ("gentle_reminder", "轻柔提醒", 500),
            ("strong_warning", "强烈警告", 1000),
            ("double_click", "双重点击", 300),
            ("gradual", "渐强震动", 1500),
        ]

        print("\n开始测试...\n")

        for pattern, description, duration in vibration_patterns:
            print(f"模式: {pattern:20} 描述: {description}")

            try:
                await haptic_agent.vibrate(pattern, duration)
                print(f"  [完成] 震动模式已触发")
            except Exception as e:
                print(f"  [错误] {e}")

            print()

        print("[成功] 震动反馈测试完成")
        return True

    except ImportError as e:
        print(f"[错误] 无法导入触觉智能体: {e}")
        return False
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_visual_feedback():
    """测试视觉反馈（使用保存的图像）"""
    print_header("测试视觉反馈")

    try:
        from src.agents.ui_agent import UIAgent
        import cv2
        import numpy as np

        print("\n初始化UI智能体...")
        ui_agent = UIAgent(config={})

        # 创建测试帧
        print("\n创建测试帧...")
        test_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        test_frame[:] = (50, 50, 50)  # 灰色背景

        # 测试不同类型的视觉反馈
        test_cases = [
            ("文本提示", "系统就绪", "neutral"),
            ("警告框", "角度警告", "warning"),
            ("错误框", "严重错误", "critical"),
            ("成功提示", "操作正确", "success"),
        ]

        output_dir = Path("test_visual_outputs")
        output_dir.mkdir(exist_ok=True)

        print("\n开始测试...\n")

        for i, (feedback_type, message, style) in enumerate(test_cases, 1):
            output_path = output_dir / f"feedback_{i}.jpg"
            print(f"[{i}/{len(test_cases)}] {feedback_type}: {message}")

            try:
                # 绘制反馈
                frame = test_frame.copy()

                if style == "neutral":
                    color = (255, 255, 255)  # 白色
                elif style == "warning":
                    color = (0, 165, 255)  # 橙色
                elif style == "critical":
                    color = (0, 0, 255)  # 红色
                elif style == "success":
                    color = (0, 255, 0)  # 绿色
                else:
                    color = (255, 255, 255)

                # 绘制文本框
                cv2.rectangle(frame, (100, 300), (1180, 420), color, 2)
                cv2.putText(
                    frame,
                    message,
                    (640, 360),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    color,
                    3
                )

                # 保存图像
                cv2.imwrite(str(output_path), frame)
                print(f"  [成功] 已保存: {output_path}")

            except Exception as e:
                print(f"  [错误] {e}")

            print()

        print(f"[成功] 视觉反馈测试完成，输出目录: {output_dir}")
        return True

    except ImportError as e:
        print(f"[错误] 无法导入UI智能体: {e}")
        return False
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_feedback_coordinator():
    """测试反馈协调器（多模态协调）"""
    print_header("测试反馈协调器")

    try:
        from src.feedback.coordinator import FeedbackCoordinator

        print("\n初始化反馈协调器...")
        coordinator = FeedbackCoordinator(config={})

        # 模拟不同场景的告警
        scenarios = [
            {
                "name": "系统启动",
                "level": AlertLevel.INFO,
                "type": AlertType.SYSTEM_READY,
                "message": "智能糖尿病助手已启动，请准备注射",
                "expected_modalities": ["audio"]
            },
            {
                "name": "角度正确",
                "level": AlertLevel.INFO,
                "type": AlertType.OPERATION_CORRECT,
                "message": "注射角度正确",
                "expected_modalities": ["audio"]
            },
            {
                "name": "角度偏小",
                "level": AlertLevel.WARNING,
                "type": AlertType.ANGLE_INCORRECT,
                "message": "注射角度偏小，请调整至45度以上",
                "expected_modalities": ["audio", "vibration"]
            },
            {
                "name": "速度过快",
                "level": AlertLevel.CRITICAL,
                "type": AlertType.SPEED_TOO_FAST,
                "message": "注射速度过快，请立即停止",
                "expected_modalities": ["audio", "vibration", "visual"]
            },
        ]

        print("\n开始测试...\n")

        for scenario in scenarios:
            print(f"场景: {scenario['name']}")
            print(f"级别: {scenario['level'].value}")
            print(f"消息: {scenario['message']}")
            print(f"预期模态: {', '.join(scenario['expected_modalities'])}")

            try:
                # 生成反馈
                result = await coordinator.generate_feedback(
                    level=scenario['level'],
                    alert_type=scenario['type'],
                    message=scenario['message']
                )

                print(f"  实际模态: {', '.join(result.get('modalities', []))}")
                print(f"  [完成] 反馈已生成")

                # 询问是否执行
                try:
                    execute = input("  是否执行反馈? (y/N): ").strip().lower()
                    if execute == 'y':
                        await coordinator.execute_feedback(result)
                        print("  [完成] 反馈已执行")
                except (EOFError, KeyboardInterrupt):
                    pass

            except Exception as e:
                print(f"  [错误] {e}")

            print()

        print("[成功] 反馈协调器测试完成")
        return True

    except ImportError as e:
        print(f"[错误] 无法导入反馈协调器: {e}")
        return False
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_feedback_priority():
    """测试反馈优先级处理"""
    print_header("测试反馈优先级")

    try:
        from src.feedback.coordinator import FeedbackCoordinator

        print("\n初始化反馈协调器...")
        coordinator = FeedbackCoordinator(config={})

        # 模拟快速连续的告警
        print("\n模拟快速连续的告警...\n")

        alerts = [
            (AlertLevel.INFO, "操作正确"),
            (AlertLevel.WARNING, "角度偏小"),
            (AlertLevel.CRITICAL, "速度过快"),
            (AlertLevel.INFO, "角度已调整"),
        ]

        for i, (level, message) in enumerate(alerts, 1):
            print(f"[{i}/{len(alerts)}] 级别: {level.value:8} | 消息: {message}")

            try:
                # 生成反馈
                result = await coordinator.generate_feedback(
                    level=level,
                    alert_type=AlertType.ANGLE_INCORRECT,
                    message=message
                )

                # 检查是否被去重
                if result.get('deduplicated'):
                    print(f"        [去重] 告警已被去重，不重复生成")
                else:
                    print(f"        [生成] 反馈已生成")

            except Exception as e:
                print(f"        [错误] {e}")

            # 模拟短暂延迟
            await asyncio.sleep(0.5)

        print("\n[成功] 优先级处理测试完成")
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_integration_scenario():
    """集成测试：完整的注射监测场景"""
    print_header("集成测试：完整注射监测场景")

    try:
        from src.feedback.coordinator import FeedbackCoordinator
        import asyncio

        print("\n模拟完整注射流程...\n")
        print("场景: 用户进行胰岛素注射")
        print("系统实时监测并提供反馈\n")

        coordinator = FeedbackCoordinator(config={})

        # 注射流程
        injection_steps = [
            {
                "step": "1. 系统启动",
                "level": AlertLevel.INFO,
                "message": "智能糖尿病助手已启动",
                "delay": 1.0
            },
            {
                "step": "2. 检测到注射器",
                "level": AlertLevel.INFO,
                "message": "检测到注射器，请准备注射",
                "delay": 1.0
            },
            {
                "step": "3. 角度检测（角度偏小）",
                "level": AlertLevel.WARNING,
                "message": "注射角度偏小，请调整至45度以上",
                "delay": 2.0
            },
            {
                "step": "4. 角度已调整",
                "level": AlertLevel.INFO,
                "message": "角度已调整，可以开始注射",
                "delay": 1.0
            },
            {
                "step": "5. 开始注射（速度正常）",
                "level": AlertLevel.INFO,
                "message": "开始注射，请保持均匀速度",
                "delay": 1.5
            },
            {
                "step": "6. 速度过快警告",
                "level": AlertLevel.CRITICAL,
                "message": "注射速度过快，请立即减速",
                "delay": 2.0
            },
            {
                "step": "7. 速度已恢复正常",
                "level": AlertLevel.INFO,
                "message": "速度已恢复正常",
                "delay": 1.0
            },
            {
                "step": "8. 注射完成",
                "level": AlertLevel.INFO,
                "message": "注射完成，请按压注射部位",
                "delay": 1.0
            },
        ]

        print(f"共 {len(injection_steps)} 个步骤\n")

        for i, step_info in enumerate(injection_steps, 1):
            print(f"{step_info['step']}")
            print(f"  级别: {step_info['level'].value}")
            print(f"  消息: {step_info['message']}")

            try:
                # 生成并执行反馈
                result = await coordinator.generate_feedback(
                    level=step_info['level'],
                    alert_type=AlertType.OPERATION_CORRECT,
                    message=step_info['message']
                )

                print(f"  状态: [反馈已生成]")

                # 模拟延迟
                await asyncio.sleep(step_info['delay'])

            except Exception as e:
                print(f"  错误: {e}")

            print()

        print("[成功] 完整场景测试完成")
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("多模态反馈系统测试工具")
    print("=" * 60)
    print("\n可用测试:")
    print("  1. 音频反馈测试")
    print("  2. 震动反馈测试")
    print("  3. 视觉反馈测试")
    print("  4. 反馈协调器测试")
    print("  5. 优先级处理测试")
    print("  6. 集成场景测试")
    print("  7. 运行所有测试")
    print("  0. 退出")

    while True:
        print("\n" + "=" * 60)
        try:
            choice = input("请选择测试 (0-7): ").strip()

            if choice == "0":
                print("退出测试")
                break
            elif choice == "1":
                await test_audio_feedback()
            elif choice == "2":
                await test_vibration_feedback()
            elif choice == "3":
                await test_visual_feedback()
            elif choice == "4":
                await test_feedback_coordinator()
            elif choice == "5":
                await test_feedback_priority()
            elif choice == "6":
                await test_integration_scenario()
            elif choice == "7":
                print("\n运行所有测试...\n")
                tests = [
                    ("音频反馈", test_audio_feedback),
                    ("震动反馈", test_vibration_feedback),
                    ("视觉反馈", test_visual_feedback),
                    ("反馈协调器", test_feedback_coordinator),
                    ("优先级处理", test_feedback_priority),
                    ("集成场景", test_integration_scenario),
                ]

                results = {}
                for name, test_func in tests:
                    try:
                        result = await test_func()
                        results[name] = result
                    except Exception as e:
                        print(f"\n[错误] {name} 测试失败: {e}")
                        results[name] = False

                # 打印总结
                print("\n" + "=" * 60)
                print("测试总结")
                print("=" * 60)
                for name, result in results.items():
                    status = "[成功]" if result else "[失败]"
                    print(f"{name:15} {status}")

                total = len(results)
                passed = sum(results.values())
                print(f"\n总计: {passed}/{total} 通过")
                break
            else:
                print("无效选择，请重试")

        except (EOFError, KeyboardInterrupt):
            print("\n\n退出测试")
            break
        except Exception as e:
            print(f"\n[错误] {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n[错误] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

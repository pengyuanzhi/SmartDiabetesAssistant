"""
测试TTS智能体功能

测试项目中集成的TTS智能体，包括语音合成、情感调整、多语言支持等
"""

import sys
import asyncio
from pathlib import Path
import tempfile
import yaml

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_temp_config():
    """创建临时配置文件"""
    config = {
        "tts": {
            "model_path": "tts_models/multilingual/multi-dataset/your_tts",
            "templates": {}
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        return f.name


async def test_tts_agent_basic():
    """测试TTS智能体基本功能"""
    print("\n=== 测试TTS智能体基本功能 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        # 初始化TTS智能体
        print("正在初始化TTS智能体...")
        config_path = create_temp_config()
        agent = TTSAgent(config_path=config_path)

        # 测试语音播放
        test_messages = [
            ("智能糖尿病助手系统启动", "low"),
            ("注射角度正确", "low"),
            ("警告，注射角度过小，请调整至45度以上", "medium"),
            ("注射完成，请按压注射部位", "low"),
        ]

        print("\n开始语音播放测试...\n")
        print("提示: 使用系统TTS (pyttsx3) 进行播放\n")

        for i, (text, urgency) in enumerate(test_messages, 1):
            print(f"[{i}/{len(test_messages)}] 文本: {text}")
            print(f"           紧急度: {urgency}")

            try:
                # 使用 speak 方法播放语音
                feedback = {
                    "message": text,
                    "urgency": urgency,
                    "delay": 0
                }

                print(f"           [播放中]...")
                await agent.speak(feedback)
                print(f"           [完成] 播放完成")

            except Exception as e:
                print(f"           [错误] {e}")

            print()

        print("[成功] TTS智能体基本功能测试完成")

        # 清理临时配置文件
        Path(config_path).unlink(missing_ok=True)

        return True

    except ImportError as e:
        print(f"[错误] 无法导入TTS智能体: {e}")
        print("请确保已安装所有依赖: pip install -r requirements-pc.txt")
        return False
    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tts_agent_emotions():
    """测试不同紧急程度的语音"""
    print("\n=== 测试紧急程度语音 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        config_path = create_temp_config()
        agent = TTSAgent(config_path=config_path)

        # 测试不同紧急程度
        urgencies = {
            "low": "请开始注射操作",
            "medium": "很好，注射角度正确",
            "high": "警告，注射速度过快，请立即停止"
        }

        print("测试不同紧急程度表达...\n")

        for urgency, text in urgencies.items():
            print(f"紧急度: {urgency:8} | 文本: {text}")

            try:
                feedback = {
                    "message": text,
                    "urgency": urgency,
                    "delay": 0
                }

                print(f"状态: [播放中]...")
                await agent.speak(feedback)
                print(f"状态: [完成]")

            except Exception as e:
                print(f"状态: [错误] {e}")

            print()

        print("[成功] 紧急程度语音测试完成")

        Path(config_path).unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_tts_agent_queue():
    """测试语音队列功能"""
    print("\n=== 测试语音队列功能 ===\n")

    print("此功能测试连续语音提示\n")

    try:
        from src.agents.tts_agent import TTSAgent

        config_path = create_temp_config()
        agent = TTSAgent(config_path=config_path)

        # 模拟连续的语音提示
        messages = [
            ("系统启动", "low"),
            ("检测到注射器", "low"),
            ("请调整注射角度", "medium"),
            ("角度已正确", "low"),
            ("开始注射", "low"),
            ("注射速度过快", "high"),
            ("速度已恢复正常", "low"),
            ("注射完成", "low"),
        ]

        print(f"添加 {len(messages)} 条语音到队列...\n")

        for i, (message, urgency) in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}] 播放: {message}")

            try:
                feedback = {
                    "message": message,
                    "urgency": urgency,
                    "delay": 0
                }

                await agent.speak(feedback)

                # 短暂延迟
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"  错误: {e}")

        print("\n[成功] 语音队列测试完成")

        Path(config_path).unlink(missing_ok=True)
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_tts_agent_performance():
    """测试TTS性能"""
    print("\n=== 测试TTS性能 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent
        import time

        config_path = create_temp_config()
        agent = TTSAgent(config_path=config_path)

        test_text = "这是一段用于性能测试的文本"
        iterations = 3

        print(f"进行 {iterations} 次语音合成测试...\n")

        times = []
        for i in range(iterations):
            feedback = {
                "message": test_text,
                "urgency": "medium",
                "delay": 0
            }

            start = time.time()
            try:
                await agent.speak(feedback)
                end = time.time()
                times.append(end - start)
                print(f"[{i+1}/{iterations}] 耗时: {end - start:.3f}秒")
            except Exception as e:
                print(f"[{i+1}/{iterations}] 失败: {e}")

        if times:
            avg_time = sum(times) / len(times)
            print(f"\n性能统计:")
            print(f"  - 平均耗时: {avg_time:.3f}秒")
            print(f"  - 最快: {min(times):.3f}秒")
            print(f"  - 最慢: {max(times):.3f}秒")
            print(f"  - 吞吐量: {1/avg_time:.1f} 次/秒")

            if avg_time < 1.0:
                print("\n[成功] 性能良好，满足实时性要求")
            elif avg_time < 2.0:
                print("\n[提示] 性能可接受")
            else:
                print("\n[警告] 性能需要优化")
        else:
            print("[错误] 没有成功的测试")

        Path(config_path).unlink(missing_ok=True)
        return len(times) > 0

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("TTS智能体功能测试")
    print("=" * 60)

    tests = [
        ("基本功能", test_tts_agent_basic),
        ("紧急程度语音", test_tts_agent_emotions),
        ("语音队列", test_tts_agent_queue),
        ("性能测试", test_tts_agent_performance),
    ]

    results = {}

    for name, test_func in tests:
        print("\n" + "=" * 60)
        try:
            result = await test_func()
            results[name] = result
        except Exception as e:
            print(f"[错误] 测试异常: {e}")
            results[name] = False

        # 等待用户确认继续
        print("\n" + "=" * 60)
        try:
            choice = input("继续下一个测试? (Y/n): ").strip().lower()
            if choice == 'n':
                break
        except (EOFError, KeyboardInterrupt):
            print("\n跳过剩余测试")
            break

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

    if passed == total:
        print("\n[成功] 所有测试通过")
    elif passed > 0:
        print(f"\n[提示] {total - passed} 个测试失败")
    else:
        print("\n[错误] 所有测试失败")

    return passed == total


async def main():
    """主函数"""
    print("=" * 60)
    print("TTS智能体测试工具")
    print("=" * 60)
    print("\n可用测试:")
    print("  1. 基本功能测试")
    print("  2. 紧急程度语音测试")
    print("  3. 语音队列测试")
    print("  4. 性能测试")
    print("  5. 运行所有测试")
    print("  0. 退出")

    while True:
        print("\n" + "=" * 60)
        try:
            choice = input("请选择测试 (0-5): ").strip()

            if choice == "0":
                print("退出测试")
                break
            elif choice == "1":
                await test_tts_agent_basic()
            elif choice == "2":
                await test_tts_agent_emotions()
            elif choice == "3":
                await test_tts_agent_queue()
            elif choice == "4":
                await test_tts_agent_performance()
            elif choice == "5":
                await run_all_tests()
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

"""
测试TTS智能体功能

测试项目中集成的TTS智能体，包括语音合成、情感调整、多语言支持等
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_tts_agent_basic():
    """测试TTS智能体基本功能"""
    print("\n=== 测试TTS智能体基本功能 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        # 初始化TTS智能体
        print("正在初始化TTS智能体...")
        agent = TTSAgent(config={})

        # 测试语音合成
        test_messages = [
            ("智能糖尿病助手系统启动", "neutral"),
            ("注射角度正确", "positive"),
            ("警告，注射角度过小，请调整至45度以上", "negative"),
            ("注射完成，请按压注射部位", "neutral"),
        ]

        print("\n开始语音合成测试...\n")

        for i, (text, emotion) in enumerate(test_messages, 1):
            print(f"[{i}/{len(test_messages)}] 文本: {text}")
            print(f"           情感: {emotion}")

            try:
                # 生成语音
                audio_path = await agent.generate_speech(text, emotion=emotion)

                if audio_path:
                    print(f"           [成功] 音频已生成: {audio_path}")

                    # 播放音频（可选）
                    play = input("           是否播放? (y/N): ").strip().lower()
                    if play == 'y':
                        agent.play_audio(audio_path)
                else:
                    print(f"           [失败] 语音生成失败")

            except Exception as e:
                print(f"           [错误] {e}")

            print()

        print("[成功] TTS智能体基本功能测试完成")
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
    """测试不同情感的语音合成"""
    print("\n=== 测试情感语音合成 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        agent = TTSAgent(config={})

        # 测试不同情感
        emotions = {
            "neutral": "请开始注射操作",
            "positive": "很好，注射角度正确",
            "negative": "警告，注射速度过快",
            "urgent": "请立即停止，操作有误"
        }

        print("测试不同情感表达...\n")

        for emotion, text in emotions.items():
            print(f"情感: {emotion:10} | 文本: {text}")

            try:
                audio_path = await agent.generate_speech(text, emotion=emotion)
                if audio_path:
                    print(f"状态: [成功] | 文件: {audio_path}")
                else:
                    print(f"状态: [失败]")
            except Exception as e:
                print(f"状态: [错误] {e}")

            print()

        print("[成功] 情感语音合成测试完成")
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_tts_agent_queue():
    """测试语音队列功能"""
    print("\n=== 测试语音队列功能 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        agent = TTSAgent(config={})

        # 模拟连续的语音提示
        messages = [
            "系统启动",
            "检测到注射器",
            "请调整注射角度",
            "角度已正确",
            "开始注射",
            "注射速度过快",
            "速度已恢复正常",
            "注射完成"
        ]

        print(f"添加 {len(messages)} 条语音到队列...\n")

        for i, message in enumerate(messages, 1):
            print(f"[{i}/{len(messages)}] 添加: {message}")
            await agent.add_to_queue(message)

        print("\n开始处理队列...")
        await agent.process_queue()

        print("\n[成功] 语音队列测试完成")
        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_tts_agent_language_switching():
    """测试多语言切换"""
    print("\n=== 测试多语言切换 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        agent = TTSAgent(config={})

        # 测试不同语言
        messages = [
            ("zh-cn", "智能糖尿病助手"),
            ("en-us", "Smart Diabetes Assistant"),
            ("zh-cn", "请开始注射"),
            ("en-us", "Please start injection"),
        ]

        print("测试语言切换...\n")

        for lang, text in messages:
            print(f"语言: {lang:6} | 文本: {text}")

            try:
                audio_path = await agent.generate_speech(text, language=lang)
                if audio_path:
                    print(f"状态: [成功]")
                else:
                    print(f"状态: [失败]")
            except Exception as e:
                print(f"状态: [错误] {e}")

            print()

        print("[成功] 多语言切换测试完成")
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

        agent = TTSAgent(config={})

        test_text = "这是一段用于性能测试的文本，包含了基本的语音合成内容"
        iterations = 5

        print(f"进行 {iterations} 次语音合成测试...\n")

        times = []
        for i in range(iterations):
            start = time.time()
            audio_path = await agent.generate_speech(test_text)
            end = time.time()

            if audio_path:
                elapsed = end - start
                times.append(elapsed)
                print(f"[{i+1}/{iterations}] 耗时: {elapsed:.3f}秒")
            else:
                print(f"[{i+1}/{iterations}] 失败")

        if times:
            avg_time = sum(times) / len(times)
            print(f"\n性能统计:")
            print(f"  - 平均耗时: {avg_time:.3f}秒")
            print(f"  - 最快: {min(times):.3f}秒")
            print(f"  - 最慢: {max(times):.3f}秒")
            print(f"  - 吞吐量: {1/avg_time:.1f} 次/秒")

            if avg_time < 0.5:
                print("\n[成功] 性能良好，满足实时性要求")
            elif avg_time < 1.0:
                print("\n[提示] 性能可接受，建议优化")
            else:
                print("\n[警告] 性能不足，需要优化")

        return True

    except Exception as e:
        print(f"[错误] 测试失败: {e}")
        return False


async def test_tts_agent_save_output():
    """测试语音保存功能"""
    print("\n=== 测试语音保存功能 ===\n")

    try:
        from src.agents.tts_agent import TTSAgent

        agent = TTSAgent(config={})

        # 创建输出目录
        output_dir = Path("test_tts_outputs")
        output_dir.mkdir(exist_ok=True)

        # 测试消息
        test_cases = [
            ("start", "系统启动"),
            ("correct_angle", "注射角度正确"),
            ("wrong_angle", "注射角度错误"),
            ("injection_complete", "注射完成"),
        ]

        print(f"保存语音文件到: {output_dir}/\n")

        for name, text in test_cases:
            output_path = output_dir / f"{name}.wav"
            print(f"生成: {name:20} -> {output_path}")

            try:
                result_path = await agent.generate_speech(
                    text,
                    output_path=str(output_path)
                )

                if result_path:
                    file_size = Path(result_path).stat().st_size
                    print(f"状态: [成功] | 大小: {file_size/1024:.1f}KB")
                else:
                    print(f"状态: [失败]")

            except Exception as e:
                print(f"状态: [错误] {e}")

        print(f"\n[成功] 语音文件已保存到 {output_dir}/")
        return True

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
        ("情感语音", test_tts_agent_emotions),
        ("语音队列", test_tts_agent_queue),
        ("多语言切换", test_tts_agent_language_switching),
        ("性能测试", test_tts_agent_performance),
        ("保存功能", test_tts_agent_save_output),
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
    print("  2. 情感语音测试")
    print("  3. 语音队列测试")
    print("  4. 多语言切换测试")
    print("  5. 性能测试")
    print("  6. 保存功能测试")
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
                await test_tts_agent_basic()
            elif choice == "2":
                await test_tts_agent_emotions()
            elif choice == "3":
                await test_tts_agent_queue()
            elif choice == "4":
                await test_tts_agent_language_switching()
            elif choice == "5":
                await test_tts_agent_performance()
            elif choice == "6":
                await test_tts_agent_save_output()
            elif choice == "7":
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

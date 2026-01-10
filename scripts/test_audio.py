"""
测试音频设备和语音合成（Windows/Linux/macOS兼容版本）

检测音频输出设备并测试TTS语音合成功能
包括语音录制、语音克隆、多语音测试等高级功能
"""

import sys
import platform
import asyncio
from pathlib import Path
import time
from typing import List, Dict


def test_audio_devices():
    """检测音频设备"""
    print("\n=== 检测音频设备 ===\n")

    system = platform.system()

    # 检测输出设备
    print("[音频输出设备]")
    if system == "Windows":
        try:
            import winsound
            print("[成功] Windows音频系统可用")
            print("提示: 使用系统默认音频输出设备")
        except ImportError:
            print("[错误] 无法导入Windows音频模块")
    elif system == "Darwin":  # macOS
        try:
            import subprocess
            result = subprocess.run(["afplay", "--help"], capture_output=True)
            if result.returncode == 0:
                print("[成功] macOS音频系统可用 (afplay)")
        except FileNotFoundError:
            print("[警告] afplay命令未找到")
    elif system == "Linux":
        try:
            import subprocess
            result = subprocess.run(["aplay", "--version"], capture_output=True)
            if result.returncode == 0:
                print("[成功] Linux音频系统可用 (ALSA)")
                version = result.stdout.decode().split('\n')[0]
                print(f"  {version}")
        except FileNotFoundError:
            print("[警告] aplay命令未找到，请安装alsa-utils")

    # 检测输入设备
    print("\n[音频输入设备]")
    try:
        import pyaudio
        p = pyaudio.PyAudio()

        input_devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append(i)
                print(f"  设备 {i}: {info['name']}")
                print(f"    采样率: {int(info['defaultSampleRate'])} Hz")
                print(f"    通道: {info['maxInputChannels']}")

        p.terminate()

        if not input_devices:
            print("  [警告] 未检测到音频输入设备")
            return False
        else:
            print(f"\n  [成功] 检测到 {len(input_devices)} 个输入设备")
            return True

    except ImportError:
        print("  [提示] pyaudio未安装（可选）")
        print("  安装命令:")
        print("    Windows: pip install pipwin && pipwin install pyaudio")
        print("    Linux: sudo apt install python3-pyaudio")
        print("    macOS: brew install portaudio && pip install pyaudio")
        return False
    except Exception as e:
        print(f"  [错误] {e}")
        return False


def test_system_tts():
    """测试系统TTS（跨平台）"""
    print("\n=== 测试系统TTS ===\n")

    try:
        import pyttsx3

        # 初始化TTS引擎
        engine = pyttsx3.init()

        # 获取可用语音
        voices = engine.getProperty('voices')
        print(f"检测到 {len(voices)} 个可用语音:\n")

        for i, voice in enumerate(voices):
            print(f"语音 {i}:")
            print(f"  - ID: {voice.id}")
            print(f"  - 名称: {voice.name}")
            print(f"  - 语言: {voice.languages}")
            print()

        # 设置中文语音（如果可用）
        for voice in voices:
            if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                print(f"[成功] 使用中文语音: {voice.name}")
                break
        else:
            # 使用第一个可用语音
            if voices:
                engine.setProperty('voice', voices[0].id)
                print(f"[提示] 使用默认语音: {voices[0].name}")

        # 测试语音合成
        test_messages = [
            "智能糖尿病助手启动",
            "请保持45度角注射",
            "注射速度过快，请减慢",
        ]

        print("\n开始语音测试...")
        for i, message in enumerate(test_messages, 1):
            print(f"\n[{i}/{len(test_messages)}] 正在播放: {message}")
            engine.say(message)
            engine.runAndWait()

        print("\n[成功] 系统TTS测试完成")
        engine.stop()
        return True

    except ImportError:
        print("[错误] 未安装 pyttsx3")
        print("安装命令: pip install pyttsx3")
        return False
    except Exception as e:
        print(f"[错误] 系统TTS测试失败: {e}")
        return False


def record_reference_audio(output_path: str = "reference_voice.wav", duration: int = 10) -> bool:
    """
    录制参考音频用于语音克隆

    Args:
        output_path: 输出文件路径
        duration: 录制时长（秒）

    Returns:
        录制是否成功
    """
    print(f"\n=== 录制参考音频 ===")
    print(f"输出文件: {output_path}")
    print(f"录制时长: {duration} 秒\n")

    try:
        import pyaudio
        import wave

        p = pyaudio.PyAudio()

        # 列出可用设备
        input_devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append(i)

        if not input_devices:
            print("[错误] 未检测到音频输入设备")
            p.terminate()
            return False

        # 选择设备
        device_index = input_devices[0]
        if len(input_devices) > 1:
            print(f"检测到 {len(input_devices)} 个输入设备，使用设备 {device_index}")

        # 录制参数
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 22050  # 语音克隆推荐采样率

        print(f"\n录制参数:")
        print(f"  采样率: {RATE} Hz")
        print(f"  通道数: {CHANNELS}")
        print(f"  格式: 16-bit PCM")
        print(f"\n提示: 请朗读一段清晰的中文语音，建议内容：")
        print('  "你好，我是智能糖尿病助手的语音助手，今天天气不错"')

        input("\n按回车键开始录制...")

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input_device_index=device_index,
            input=True,
            frames_per_chunk=CHUNK
        )

        print(f"\n[录制中] 请说话（{duration}秒）...")
        frames = []

        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

            # 显示进度
            progress = int((i + 1) / (RATE / CHUNK * duration) * 100)
            print(f"\r进度: {progress}%", end="")

        print("\n[录制完成]")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存录音
        wf = wave.open(output_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # 检查文件大小
        file_size = Path(output_path).stat().st_size / 1024  # KB
        print(f"\n[成功] 录音已保存到: {output_path}")
        print(f"文件大小: {file_size:.1f} KB")

        # 验证录音质量
        if file_size < 10:
            print("[警告] 文件过小，可能录音质量不佳")
        elif file_size > 500:
            print("[提示] 文件较大，语音克隆可能需要更长时间")

        return True

    except ImportError:
        print("[错误] 未安装 pyaudio")
        print("安装命令:")
        print("  Windows: pip install pipwin && pipwin install pyaudio")
        print("  Linux: sudo apt install python3-pyaudio")
        print("  macOS: brew install portaudio && pip install pyaudio")
        return False
    except Exception as e:
        print(f"[错误] 录音失败: {e}")
        return False


def test_coqui_tts():
    """测试Coqui TTS（需要网络下载模型）"""
    print("\n=== 测试Coqui TTS ===\n")

    try:
        from TTS.api import TTS

        # 初始化TTS（使用轻量级模型）
        print("正在加载Coqui TTS模型...")
        print("提示: 首次运行会自动下载模型（约50MB）")

        # 使用多语言模型
        model_name = "tts_models/multilingual/multi-dataset/your_tts"
        tts = TTS(model_name=model_name, progress_bar=True, gpu=False)

        # 测试语音合成
        test_text = "智能糖尿病助手语音测试"
        output_path = "test_tts_output.wav"

        print(f"\n正在合成语音: {test_text}")
        tts.tts_to_file(
            text=test_text,
            file_path=output_path,
            language_zh="zh-cn"
        )

        print(f"[成功] 语音已保存到: {output_path}")

        # 播放合成的音频
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.PlaySound(output_path, winsound.SND_FILENAME)
            elif platform.system() == "Darwin":  # macOS
                import subprocess
                subprocess.run(["afplay", output_path])
            else:  # Linux
                import subprocess
                subprocess.run(["aplay", output_path])

            print("[成功] 音频播放完成")
        except Exception as e:
            print(f"[警告] 无法播放音频: {e}")
            print(f"提示: 请手动播放 {output_path}")

        return True

    except ImportError:
        print("[错误] 未安装 Coqui TTS")
        print("安装命令: pip install TTS")
        print("\n注意: Coqui TTS在Windows上安装可能需要额外配置")
        print("推荐使用系统TTS (pyttsx3) 进行开发")
        return False
    except Exception as e:
        print(f"[错误] Coqui TTS测试失败: {e}")
        print("\n可能的原因:")
        print("  1. 网络连接问题（无法下载模型）")
        print("  2. 磁盘空间不足")
        print("  3. 模型下载中断")
        return False


def test_voice_cloning_single(reference_audio: str, test_texts: List[str]) -> bool:
    """
    使用单个参考音频进行语音克隆

    Args:
        reference_audio: 参考音频文件路径
        test_texts: 要合成的文本列表

    Returns:
        克隆是否成功
    """
    print(f"\n=== 语音克隆测试 ===")
    print(f"参考音频: {reference_audio}")
    print(f"测试文本数: {len(test_texts)}\n")

    if not Path(reference_audio).exists():
        print(f"[错误] 参考音频文件不存在: {reference_audio}")
        return False

    try:
        from TTS.api import TTS

        print("正在加载语音克隆模型...")
        print("提示: 如果模型未下载，会自动下载（约50MB）\n")

        # 加载支持语音克隆的模型
        model_name = "tts_models/multilingual/multi-dataset/your_tts"
        tts = TTS(
            model_name=model_name,
            progress_bar=True,
            gpu=False
        )

        print("[成功] 模型加载完成\n")

        # 批量克隆语音
        output_dir = Path("cloned_voices")
        output_dir.mkdir(exist_ok=True)

        for i, text in enumerate(test_texts, 1):
            output_path = output_dir / f"cloned_{i}.wav"

            print(f"[{i}/{len(test_texts)}] 合成: {text}")

            start_time = time.time()
            tts.tts_to_file(
                text=text,
                file_path=str(output_path),
                speaker_wav=reference_audio,
                language_zh="zh-cn"
            )
            elapsed = time.time() - start_time

            file_size = output_path.stat().st_size / 1024  # KB
            print(f"  [完成] 耗时: {elapsed:.2f}秒 | 文件大小: {file_size:.1f}KB")

        print(f"\n[成功] 所有语音已保存到: {output_dir}/")
        return True

    except ImportError:
        print("[错误] 未安装 Coqui TTS")
        print("安装命令: pip install TTS")
        return False
    except Exception as e:
        print(f"[错误] 语音克隆失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_voice_cloning_multiple(reference_audios: List[str], test_text: str) -> bool:
    """
    使用多个参考音频进行语音克隆对比

    Args:
        reference_audios: 参考音频文件路径列表
        test_text: 要合成的测试文本

    Returns:
        克隆是否成功
    """
    print(f"\n=== 多语音克隆对比 ===")
    print(f"参考音频数: {len(reference_audios)}")
    print(f"测试文本: {test_text}\n")

    try:
        from TTS.api import TTS

        print("正在加载语音克隆模型...")
        model_name = "tts_models/multilingual/multi-dataset/your_tts"
        tts = TTS(model_name=model_name, progress_bar=True, gpu=False)

        print("[成功] 模型加载完成\n")

        # 为每个参考音频生成克隆语音
        output_dir = Path("voice_comparison")
        output_dir.mkdir(exist_ok=True)

        for i, ref_audio in enumerate(reference_audios, 1):
            if not Path(ref_audio).exists():
                print(f"[{i}/{len(reference_audios)}] 跳过: {ref_audio} (不存在)")
                continue

            print(f"[{i}/{len(reference_audios)}] 使用: {Path(ref_audio).name}")

            output_path = output_dir / f"clone_{i}.wav"

            start_time = time.time()
            tts.tts_to_file(
                text=test_text,
                file_path=str(output_path),
                speaker_wav=ref_audio,
                language_zh="zh-cn"
            )
            elapsed = time.time() - start_time

            file_size = output_path.stat().st_size / 1024  # KB
            print(f"  [完成] 耗时: {elapsed:.2f}秒 | 文件: {output_path.name} ({file_size:.1f}KB)")

        print(f"\n[成功] 对比语音已保存到: {output_dir}/")
        print("提示: 可以手动播放这些文件，对比克隆效果")
        return True

    except Exception as e:
        print(f"[错误] 多语音克隆失败: {e}")
        return False


def test_voice_style_transfer():
    """测试语音风格转换（高级功能）"""
    print("\n=== 语音风格转换 ===\n")
    print("此功能可以将一个语音的风格应用到另一个语音上")
    print("需要: 两个参考音频文件\n")

    reference_audios = []

    # 查找可用的参考音频
    for pattern in ["reference_*.wav", "voice_*.wav", "sample_*.wav"]:
        reference_audios.extend(Path(".").glob(pattern))

    if len(reference_audios) < 2:
        print(f"[提示] 未找到足够的参考音频文件（需要至少2个）")
        print("请准备参考音频文件并命名为:")
        print("  - reference_voice1.wav")
        print("  - reference_voice2.wav")
        return False

    print(f"找到 {len(reference_audios)} 个参考音频:")
    for i, audio in enumerate(reference_audios[:5], 1):  # 最多显示5个
        print(f"  {i}. {audio.name}")

    print("\n此功能正在开发中...")
    return False


def interactive_voice_cloning():
    """交互式语音克隆工具"""
    print("\n=== 交互式语音克隆工具 ===\n")

    print("选项:")
    print("  1. 录制新的参考音频")
    print("  2. 使用现有参考音频")
    print("  3. 批量克隆（多个文本）")
    print("  4. 多语音对比")
    print("  0. 返回")

    while True:
        try:
            choice = input("\n请选择 (0-4): ").strip()

            if choice == "0":
                print("返回主菜单")
                break

            elif choice == "1":
                # 录制参考音频
                output_file = input("输出文件名 (默认: reference_voice.wav): ").strip()
                if not output_file:
                    output_file = "reference_voice.wav"

                duration = input("录制时长（秒，默认: 10）: ").strip()
                if not duration:
                    duration = 10
                else:
                    duration = int(duration)

                if record_reference_audio(output_file, duration):
                    # 自动测试
                    test_texts = ["这是使用语音克隆技术生成的语音"]
                    test_voice_cloning_single(output_file, test_texts)

            elif choice == "2":
                # 使用现有音频
                ref_audio = input("参考音频路径 (默认: reference_voice.wav): ").strip()
                if not ref_audio:
                    ref_audio = "reference_voice.wav"

                if not Path(ref_audio).exists():
                    print(f"[错误] 文件不存在: {ref_audio}")
                    continue

                text = input("要合成的文本: ").strip()
                if not text:
                    text = "这是语音克隆测试"

                test_voice_cloning_single(ref_audio, [text])

            elif choice == "3":
                # 批量克隆
                ref_audio = input("参考音频路径 (默认: reference_voice.wav): ").strip()
                if not ref_audio:
                    ref_audio = "reference_voice.wav"

                if not Path(ref_audio).exists():
                    print(f"[错误] 文件不存在: {ref_audio}")
                    continue

                print("输入要合成的文本（每行一条，空行结束）:")
                texts = []
                while True:
                    line = input().strip()
                    if not line:
                        break
                    texts.append(line)

                if texts:
                    test_voice_cloning_single(ref_audio, texts)

            elif choice == "4":
                # 多语音对比
                print("输入参考音频路径（每行一个，空行结束）:")
                audios = []
                while True:
                    line = input().strip()
                    if not line:
                        break
                    audios.append(line)

                if len(audios) < 2:
                    print("[错误] 至少需要2个参考音频")
                    continue

                text = input("测试文本: ").strip()
                if not text:
                    text = "语音克隆对比测试"

                test_voice_cloning_multiple(audios, text)

            else:
                print("无效选择")

        except (EOFError, KeyboardInterrupt):
            print("\n返回主菜单")
            break
        except Exception as e:
            print(f"[错误] {e}")


def main():
    """主测试函数"""
    print("=" * 60)
    print("智能糖尿病助手 - 音频系统测试工具")
    print("=" * 60)
    print(f"平台: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 60)

    # 1. 检测音频设备
    test_audio_devices()

    # 2. 测试系统TTS（推荐）
    print("\n" + "=" * 60)
    try:
        choice = input("是否测试系统TTS? (Y/n): ").strip().lower()
        if choice != 'n':
            system_tts_ok = test_system_tts()
        else:
            print("\n跳过系统TTS测试")
            system_tts_ok = False
    except (EOFError, KeyboardInterrupt):
        print("\n跳过系统TTS测试")
        system_tts_ok = False

    # 3. 测试Coqui TTS（可选）
    print("\n" + "=" * 60)
    try:
        choice = input("是否测试Coqui TTS？（需要下载模型，约50MB）(y/N): ").strip().lower()
        if choice == 'y' or choice == 'yes':
            coqui_tts_ok = test_coqui_tts()
        else:
            print("\n跳过Coqui TTS测试")
            coqui_tts_ok = False
    except (EOFError, KeyboardInterrupt):
        print("\n跳过Coqui TTS测试")
        coqui_tts_ok = False

    # 4. 语音克隆（高级功能）
    print("\n" + "=" * 60)
    try:
        choice = input("是否测试语音克隆功能？（需要Coqui TTS）(y/N): ").strip().lower()
        if choice == 'y' or choice == 'yes':
            interactive_voice_cloning()
    except (EOFError, KeyboardInterrupt):
        print("\n跳过语音克隆测试")

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"系统TTS: {'[成功]' if system_tts_ok else '[失败/跳过]'}")
    print(f"Coqui TTS: {'[成功]' if coqui_tts_ok else '[失败/跳过]'}")

    print("\n建议:")
    if system_tts_ok:
        print("  - 系统TTS正常工作，可用于开发调试")
        print("  - 运行主程序: python src/main.py --tts system")
    else:
        print("  - 请先安装系统TTS: pip install pyttsx3")

    if coqui_tts_ok:
        print("  - Coqui TTS可用，可提供更自然的语音")
        print("  - 支持语音克隆功能")
        print("  - 运行主程序: python src/main.py --tts coqui")

    print("\n下一步:")
    print("  1. 测试摄像头: python scripts/test_camera.py")
    print("  2. 测试反馈系统: python scripts/test_feedback.py")
    print("  3. 运行完整系统: python scripts/quick_start.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n[错误] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

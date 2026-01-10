"""
测试音频设备和语音合成（Windows/Linux/macOS兼容版本）

检测音频输出设备并测试TTS语音合成功能
"""

import sys
import platform
import asyncio
from pathlib import Path


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
        return False
    except Exception as e:
        print(f"[错误] Coqui TTS测试失败: {e}")
        print("\n可能的原因:")
        print("  1. 网络连接问题（无法下载模型）")
        print("  2. 磁盘空间不足")
        print("  3. 模型下载中断")
        return False


def test_audio_devices():
    """检测音频输出设备"""
    print("\n=== 检测音频设备 ===\n")

    system = platform.system()

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
        # 检查ALSA
        try:
            import subprocess
            result = subprocess.run(["aplay", "--version"], capture_output=True)
            if result.returncode == 0:
                print("[成功] Linux音频系统可用 (ALSA)")
                version = result.stdout.decode().split('\n')[0]
                print(f"  {version}")
        except FileNotFoundError:
            print("[警告] aplay命令未找到，请安装alsa-utils")


def test_voice_cloning():
    """测试语音克隆功能（可选）"""
    print("\n=== 测试语音克隆（高级功能） ===\n")

    print("此功能用于个性化语音输出")
    print("需要: 参考语音音频文件")

    # 检查是否有参考音频
    reference_audio = "reference_voice.wav"

    if not Path(reference_audio).exists():
        print(f"[提示] 未找到参考音频文件: {reference_audio}")
        print("如需测试语音克隆，请:")
        print("  1. 准备一段5-10秒的清晰语音音频")
        print("  2. 保存为 reference_voice.wav")
        print("  3. 重新运行此测试")
        return False

    try:
        from TTS.api import TTS

        print("正在加载语音克隆模型...")
        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/your_tts",
            progress_bar=True,
            gpu=False
        )

        test_text = "这是使用语音克隆技术生成的个性化语音"
        output_path = "test_cloned_voice.wav"

        print(f"\n正在克隆语音: {test_text}")
        tts.tts_to_file(
            text=test_text,
            file_path=output_path,
            speaker_wav=reference_audio,
            language_zh="zh-cn"
        )

        print(f"[成功] 克隆语音已保存到: {output_path}")
        return True

    except Exception as e:
        print(f"[错误] 语音克隆失败: {e}")
        return False


def test_audio_recording():
    """测试音频录制（用于语音输入功能）"""
    print("\n=== 测试音频录制 ===\n")

    try:
        import pyaudio

        # 初始化PyAudio
        p = pyaudio.PyAudio()

        # 列出所有输入设备
        print("检测到的音频输入设备:\n")

        input_devices = []
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append(i)
                print(f"设备 {i}: {info['name']}")
                print(f"  - 采样率: {int(info['defaultSampleRate'])} Hz")
                print(f"  - 输入通道: {info['maxInputChannels']}")
                print()

        if not input_devices:
            print("[警告] 未检测到音频输入设备")
            p.terminate()
            return False

        # 录制测试音频
        print("\n开始录制测试音频（3秒）...")
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 3

        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_chunk=CHUNK
        )

        print("[录制中] 请说话...")
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("[录制完成]")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存录音
        output_file = "test_recording.wav"
        import wave

        wf = wave.open(output_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"[成功] 录音已保存到: {output_file}")
        return True

    except ImportError:
        print("[错误] 未安装 pyaudio")
        print("安装命令:")
        print("  Windows: pip install pipwin && pipwin install pyaudio")
        print("  Linux: sudo apt install python3-pyaudio")
        print("  macOS: brew install portaudio && pip install pyaudio")
        return False
    except Exception as e:
        print(f"[错误] 音频录制失败: {e}")
        return False


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
    system_tts_ok = test_system_tts()

    # 3. 测试Coqui TTS（可选）
    print("\n" + "=" * 60)
    print("是否测试Coqui TTS？（需要下载模型，约50MB）")
    print("提示: 首次运行会下载模型，可能需要几分钟")
    print("=" * 60)

    try:
        choice = input("\n是否继续? (y/N): ").strip().lower()
        if choice == 'y' or choice == 'yes':
            coqui_tts_ok = test_coqui_tts()
        else:
            print("\n跳过Coqui TTS测试")
            coqui_tts_ok = False
    except (EOFError, KeyboardInterrupt):
        print("\n跳过Coqui TTS测试")
        coqui_tts_ok = False

    # 4. 测试音频录制（可选）
    print("\n" + "=" * 60)
    try:
        choice = input("\n是否测试音频录制功能? (y/N): ").strip().lower()
        if choice == 'y' or choice == 'yes':
            recording_ok = test_audio_recording()
        else:
            print("\n跳过音频录制测试")
            recording_ok = False
    except (EOFError, KeyboardInterrupt):
        print("\n跳过音频录制测试")
        recording_ok = False

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"系统TTS: {'[成功]' if system_tts_ok else '[失败]'}")
    print(f"Coqui TTS: {'[成功]' if coqui_tts_ok else '[跳过/失败]'}")
    print(f"音频录制: {'[成功]' if recording_ok else '[跳过/失败]'}")

    print("\n建议:")
    if system_tts_ok:
        print("  - 系统TTS正常工作，可用于开发调试")
        print("  - 运行主程序: python src/main.py --tts system")
    else:
        print("  - 请先安装系统TTS: pip install pyttsx3")

    if coqui_tts_ok:
        print("  - Coqui TTS可用，可提供更自然的语音")
        print("  - 运行主程序: python src/main.py --tts coqui")
    else:
        print("  - Coqui TTS需要下载模型，网络不佳时可能失败")

    if recording_ok:
        print("  - 音频录制功能正常，可用于语音输入")

    print("\n下一步:")
    print("  1. 测试摄像头: python scripts/test_camera.py")
    print("  2. 运行完整系统: python scripts/quick_start.py")
    print("  3. 查看更多选项: python src/main.py --help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n[错误] 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

"""
音频录制和播放测试脚本

功能：
1. 列出可用的音频输入设备（麦克风）
2. 录制音频
3. 播放录制的音频
4. 保存音频文件
"""

import pyaudio
import wave
import platform
import os
from pathlib import Path


# 音频参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
CHUNK = 1024


def get_audio_devices():
    """获取所有音频输入设备"""
    p = pyaudio.PyAudio()

    print("\n=== 可用的音频输入设备 ===\n")

    input_devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            input_devices.append(i)
            print(f"设备 {i}: {info['name']}")
            print(f"  采样率: {int(info['defaultSampleRate'])} Hz")
            print(f"  输入通道: {info['maxInputChannels']}")
            print()

    p.terminate()

    return input_devices


def record_audio(duration=5, device_index=None, output_file="test_recording.wav"):
    """
    录制音频

    Args:
        duration: 录制时长（秒）
        device_index: 设备索引（None表示使用默认设备）
        output_file: 输出文件路径

    Returns:
        是否成功
    """
    p = pyaudio.PyAudio()

    try:
        # 打开音频流
        print(f"\n打开音频流...")
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )

        print(f"开始录制 {duration} 秒...")
        print("提示: 请现在开始说话\n")

        frames = []

        # 录制音频
        for i in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

            # 显示进度
            if (i + 1) % (RATE / CHUNK) == 0:  # 每秒更新一次
                elapsed = (i + 1) / (RATE / CHUNK)
                print(f"  录制中... {elapsed:.0f}/{duration} 秒")

        print(f"\n录制完成!")

        # 停止并关闭流
        stream.stop_stream()
        stream.close()

        # 保存音频文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        wf = wave.open(str(output_path), 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"音频已保存到: {output_path}")
        print(f"文件大小: {output_path.stat().st_size / 1024:.1f} KB")

        return True

    except Exception as e:
        print(f"[错误] 录制失败: {e}")
        return False

    finally:
        p.terminate()


def play_audio(file_path):
    """
    播放音频文件（使用PyAudio直接播放）

    Args:
        file_path: 音频文件路径

    Returns:
        是否成功
    """
    if not Path(file_path).exists():
        print(f"[错误] 文件不存在: {file_path}")
        return False

    print(f"\n播放音频: {file_path}")
    print("提示: 请调高音量")
    print("播放中... (按Ctrl+C停止)\n")

    try:
        # 使用PyAudio直接播放
        wf = wave.open(str(file_path), 'rb')

        p = pyaudio.PyAudio()

        # 打开输出流
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        # 读取并播放音频数据
        data = wf.readframes(CHUNK)
        total_frames = 0
        total_duration = wf.getnframes() / wf.getframerate()

        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

            # 显示进度
            total_frames += CHUNK
            if total_frames % (wf.getframerate()) < CHUNK:  # 每秒更新
                elapsed = total_frames / wf.getframerate()
                print(f"  播放进度: {elapsed:.1f}/{total_duration:.1f} 秒")

        # 清理
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()

        print("\n播放完成!")
        return True

    except KeyboardInterrupt:
        print("\n播放已停止")
        return True
    except Exception as e:
        print(f"\n[错误] 播放失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_microphone_access():
    """测试麦克风访问权限"""
    print("\n=== 测试麦克风访问 ===\n")

    try:
        p = pyaudio.PyAudio()

        # 尝试打开默认输入设备
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("✓ 麦克风访问正常")

        # 读取一小段数据测试
        print("正在测试音频输入...")
        data = stream.read(CHUNK)
        print(f"✓ 成功读取 {len(data)} 字节音频数据")

        stream.close()
        p.terminate()

        return True

    except Exception as e:
        print(f"✗ 麦克风访问失败: {e}")

        if "Permission denied" in str(e):
            print("\n可能的原因:")
            print("  - 未授予麦克风访问权限")
            print("  - 请在系统设置中允许此程序访问麦克风")

        return False


def record_and_play_test(duration=5):
    """
    录制并播放测试

    Args:
        duration: 录制时长（秒）

    Returns:
        是否成功
    """
    output_file = "test_recordings/test.wav"

    # 录制
    if not record_audio(duration=duration, output_file=output_file):
        return False

    # 显示文件信息
    print_audio_info(output_file)

    # 播放
    print("\n" + "="*50)
    if not play_audio(output_file):
        return False

    return True


def print_audio_info(file_path):
    """
    显示音频文件信息

    Args:
        file_path: 音频文件路径
    """
    try:
        wf = wave.open(str(file_path), 'rb')

        print("\n=== 音频文件信息 ===")
        print(f"文件路径: {file_path}")
        print(f"文件大小: {Path(file_path).stat().st_size / 1024:.1f} KB")
        print(f"通道数: {wf.getnchannels()}")
        print(f"采样宽度: {wf.getsampwidth()} bytes")
        print(f"采样率: {wf.getframerate()} Hz")
        print(f"帧数: {wf.getnframes()}")
        print(f"时长: {wf.getnframes() / wf.getframerate():.2f} 秒")
        print(f"压缩类型: {wf.getcomptype()}")
        print("="*50)

        wf.close()
    except Exception as e:
        print(f"[错误] 无法读取文件信息: {e}")


def interactive_menu():
    """交互式菜单"""
    while True:
        print("\n" + "="*50)
        print("        音频录制测试工具")
        print("="*50)
        print()
        print("请选择操作:")
        print("  1. 查看音频输入设备")
        print("  2. 测试麦克风访问")
        print("  3. 录制并播放音频（5秒）")
        print("  4. 录制并播放音频（10秒）")
        print("  5. 录制并播放音频（自定义时长）")
        print("  6. 播放已录制的音频")
        print("  0. 退出")
        print()

        choice = input("请选择 (0-6): ").strip()

        if choice == "0":
            print("退出程序")
            break

        elif choice == "1":
            get_audio_devices()

        elif choice == "2":
            test_microphone_access()

        elif choice == "3":
            record_and_play_test(duration=5)

        elif choice == "4":
            record_and_play_test(duration=10)

        elif choice == "5":
            try:
                duration = float(input("请输入录制时长（秒）: ").strip())
                if duration <= 0:
                    print("时长必须大于0")
                else:
                    record_and_play_test(duration=duration)
            except ValueError:
                print("无效的输入")

        elif choice == "6":
            # 列出所有录制的音频文件
            recording_dir = Path("test_recordings")
            if recording_dir.exists():
                audio_files = list(recording_dir.glob("*.wav"))
                if audio_files:
                    print("\n已录制的音频文件:")
                    for i, f in enumerate(audio_files, 1):
                        size = f.stat().st_size / 1024
                        print(f"  {i}. {f.name} ({size:.1f} KB)")

                    try:
                        file_choice = int(input("\n请选择要播放的文件编号: ").strip())
                        if 1 <= file_choice <= len(audio_files):
                            selected_file = audio_files[file_choice - 1]
                            print_audio_info(selected_file)
                            play_audio(selected_file)
                        else:
                            print("无效的选择")
                    except ValueError:
                        print("无效的输入")
                else:
                    print("没有找到录制的音频文件")
            else:
                print("没有找到录制的音频文件")

        else:
            print("无效的选择，请重新输入")


def main():
    """主函数"""
    print("="*50)
    print("        音频录制测试工具")
    print("="*50)
    print()
    print("此工具用于测试音频录制和播放功能")
    print()

    # 检查PyAudio是否安装
    try:
        import pyaudio
        print("✓ PyAudio已安装")
    except ImportError:
        print("✗ PyAudio未安装")
        print("\n安装命令:")
        print("  pip install pyaudio")
        print("\nWindows用户可能需要先安装:")
        print("  pip install pipwin")
        print("  pipwin install pyaudio")
        return

    # 运行交互式菜单
    interactive_menu()


if __name__ == "__main__":
    main()

"""
麦克风录音诊断和修复工具

用于诊断和修复麦克风录音音量太小的问题
"""

import pyaudio
import wave
import platform
import os


def list_audio_devices():
    """列出所有音频设备"""
    p = pyaudio.PyAudio()

    print("\n=== 所有音频设备 ===\n")

    print("【输入设备（麦克风）】")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            is_default = " [默认]" if i == p.get_default_input_device_info()['index'] else ""
            print(f"\n设备 {i}{is_default}: {info['name']}")
            print(f"  采样率: {int(info['defaultSampleRate'])} Hz")
            print(f"  最大输入通道: {info['maxInputChannels']}")

    print("\n" + "="*50)
    print("【输出设备（扬声器）】")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxOutputChannels'] > 0:
            is_default = " [默认]" if i == p.get_default_output_device_info()['index'] else ""
            print(f"\n设备 {i}{is_default}: {info['name']}")
            print(f"  采样率: {int(info['defaultSampleRate'])} Hz")
            print(f"  最大输出通道: {info['maxOutputChannels']}")

    p.terminate()


def test_microphone_with_boost(device_index=None, duration=3):
    """
    测试麦克风（带音量增强）

    Args:
        device_index: 设备索引（None=默认设备）
        duration: 录制时长（秒）
    """
    p = pyaudio.PyAudio()

    # 音频参数 - 使用更兼容的参数
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    # 尝试多个采样率，从标准开始
    RATES_TO_TRY = [16000, 22050, 44100, 48000]
    CHUNK = 512  # 更小的缓冲区

    try:
        if device_index is None:
            try:
                device_index = p.get_default_input_device_info()['index']
            except OSError:
                print("\n[错误] 无法获取默认输入设备")
                print("请尝试选择特定的音频设备")
                p.terminate()
                return 0

        device_info = p.get_device_info_by_index(device_index)
        device_name = device_info['name']
        max_rate = int(device_info['defaultSampleRate'])

        print(f"\n使用设备 {device_index}: {device_name}")
        print(f"设备默认采样率: {max_rate} Hz")
        print(f"录制时长: {duration} 秒\n")

        # 找到支持的采样率
        RATE = None
        for rate in RATES_TO_TRY:
            if rate <= max_rate:
                RATE = rate
                break

        if RATE is None:
            RATE = max_rate

        print(f"使用采样率: {RATE} Hz")

        # 尝试打开音频流，使用设备支持的采样率
        stream = None
        last_error = None

        # 尝试不同的通道配置
        channel_configs = [1, 2]
        stream_opened = False

        for channels in channel_configs:
            try:
                print(f"\n尝试 {channels} 通道...")
                stream = p.open(
                    format=FORMAT,
                    channels=channels,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK
                )
                CHANNELS = channels
                stream_opened = True
                print(f"成功打开音频流 ({channels} 通道)")
                break
            except OSError as e:
                last_error = e
                print(f"失败: {e}")
                continue

        if not stream_opened:
            print(f"\n[错误] 无法打开音频流")
            print(f"错误信息: {last_error}")
            print("\n可能的原因:")
            print("1. 设备被其他程序占用")
            print("2. 驱动程序不兼容")
            print("3. 设备不支持此采样率")
            print("\n建议:")
            print("- 关闭其他使用麦克风的程序（如Zoom、Teams等）")
            print("- 尝试选择其他音频设备")
            print("- 重启电脑")
            p.terminate()
            return 0

        print("开始录制...请大声说话或拍手")
        print("提示：尽量靠近麦克风\n")

        frames = []

        # 实时监控音量
        import struct
        max_amplitude = 0
        frame_count = 0

        for i in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

            # 解码音频数据检查音量
            samples = struct.unpack('<' + 'h' * (CHUNK), data)
            current_max = max(abs(s) for s in samples)
            max_amplitude = max(max_amplitude, current_max)

            # 每秒更新一次音量显示
            frame_count += CHUNK
            if frame_count % RATE < CHUNK:
                volume_percent = (current_max / 32768) * 100
                bar_length = int(volume_percent / 2)
                bar = '█' * bar_length + '░' * (50 - bar_length)
                print(f"  [{bar}] {volume_percent:.1f}% (当前: {current_max}, 最大: {max_amplitude})")

        print(f"\n录制完成！最大振幅: {max_amplitude}")

        # 停止流
        stream.stop_stream()
        stream.close()

        # 保存文件
        output_file = "test_recordings/test_boosted.wav"
        os.makedirs("test_recordings", exist_ok=True)

        wf = wave.open(output_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print(f"\n文件已保存: {output_file}")

        # 分析录音质量
        if max_amplitude < 100:
            print("\n❌ 麦克风音量太小！")
            print("\n可能的原因：")
            print("1. 麦克风被静音")
            print("2. 选择了错误的输入设备（如立体声混音）")
            print("3. 麦克风权限未授予")
            print("4. 系统麦克风音量设置太低")
            print("\n建议的解决方案：")
            print("1. 检查系统设置 → 声音 → 麦克风音量")
            print("2. 确保麦克风权限已开启")
            print("3. 尝试选择其他输入设备")
            print("4. 使用外部麦克风")
        elif max_amplitude < 1000:
            print("\n⚠️ 麦克风音量偏小")
            print("建议：调大系统麦克风音量或靠近麦克风")
        else:
            print("\n✅ 麦克风工作正常！")

        p.terminate()
        return max_amplitude

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        p.terminate()
        return 0


def interactive_diagnostic():
    """交互式诊断"""
    print("="*60)
    print("        麦克风录音诊断工具")
    print("="*60)

    # 检查PyAudio
    try:
        import pyaudio
        print("✓ PyAudio已安装\n")
    except ImportError:
        print("✗ PyAudio未安装")
        print("\n安装命令:")
        print("  pip install pyaudio")
        return

    while True:
        print("\n" + "="*60)
        print("请选择操作:")
        print("  1. 查看所有音频设备")
        print("  2. 测试默认麦克风（3秒）")
        print("  3. 测试默认麦克风（5秒）")
        print("  4. 选择特定麦克风测试")
        print("  5. 查看系统麦克风设置指南")
        print("  0. 退出")
        print()

        choice = input("请选择 (0-5): ").strip()

        if choice == "0":
            print("退出程序")
            break

        elif choice == "1":
            list_audio_devices()

        elif choice == "2":
            test_microphone_with_boost(duration=3)

        elif choice == "3":
            test_microphone_with_boost(duration=5)

        elif choice == "4":
            list_audio_devices()
            try:
                device_index = int(input("\n请输入设备编号: ").strip())
                test_microphone_with_boost(device_index=device_index, duration=3)
            except ValueError:
                print("无效的输入")

        elif choice == "5":
            show_microphone_guide()

        else:
            print("无效的选择")


def show_microphone_guide():
    """显示系统麦克风设置指南"""
    system = platform.system()

    print("\n" + "="*60)
    print("系统麦克风设置指南")
    print("="*60)

    if system == "Windows":
        print("\n【Windows】\n")
        print("1. 检查麦克风权限:")
        print("   设置 → 隐私 → 麦克风 → 允许应用访问麦克风")
        print("\n2. 检查麦克风音量:")
        print("   设置 → 系统 → 声音 → 输入设备")
        print("   - 确保选择了正确的麦克风")
        print("   - 调整输入音量滑块到80-100%")
        print("\n3. 检查应用程序权限:")
        print("   Windows安全中心 → 权限管理 → 允许此应用访问麦克风")
        print("\n4. 测试麦克风:")
        print("   设置 → 系统 → 声音 → 测试麦克风")

    elif system == "Darwin":  # macOS
        print("\n【macOS】\n")
        print("1. 检查麦克风权限:")
        print("   系统偏好设置 → 安全性与隐私 → 隐私 → 麦克风")
        print("\n2. 检查输入音量:")
        print("   系统偏好设置 → 声音 → 输入")
        print("   - 选择正确的输入设备")
        print("   - 调整输入音量滑块")

    else:  # Linux
        print("\n【Linux】\n")
        print("1. 检查麦克风设备:")
        print("   arecord -l  # 列出录音设备")
        print("\n2. 调整音量:")
        print("   alsamixer  # 音量控制工具")
        print("\n3. 测试录音:")
        print("   arecord -f cd -d 5 test.wav")

    print("\n" + "="*60)
    print("\n常见问题:")
    print("• 如果录音仍是静音，尝试:")
    print("  1. 更换USB接口（外置麦克风）")
    print("  2. 重启电脑")
    print("  3. 更新音频驱动程序")
    print("  4. 使用手机耳机测试")


if __name__ == "__main__":
    interactive_diagnostic()

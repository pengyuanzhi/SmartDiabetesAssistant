"""
测试摄像头设备（Windows/Linux/macOS兼容版本）

列出所有可用的摄像头并测试视频流
"""

import cv2
import sys
import platform


def list_cameras():
    """列出所有可用的摄像头"""
    print("\n=== 检测可用的摄像头 ===\n")

    available_cameras = []

    # 检测更多设备（最多10个）
    max_cameras = 10

    for i in range(max_cameras):
        cap = None

        # Windows: 尝试使用DirectShow后端
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

        # 如果DirectShow失败，使用默认后端
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(i)

        if cap.isOpened():
            # 获取摄像头属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            backend = cap.getBackendName()

            print(f"[OK] 摄像头 {i}:")
            print(f"  - 分辨率: {width}x{height}")
            print(f"  - 帧率: {fps}")
            print(f"  - 后端: {backend}")
            print()

            available_cameras.append(i)
            cap.release()
        else:
            print(f"[--] 摄像头 {i}: 不可用")

    return available_cameras


def test_camera_headless(camera_id: int, duration: int = 10):
    """
    测试指定摄像头（无GUI模式）

    Args:
        camera_id: 摄像头ID
        duration: 测试时长（秒）
    """
    print(f"\n=== 测试摄像头 {camera_id} ===")
    print(f"测试时长: {duration} 秒")
    print("使用无GUI模式（适合Windows服务器）\n")

    # Windows: 使用DirectShow后端
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"[错误] 无法打开摄像头 {camera_id}")
        return False

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 获取实际设置
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"实际分辨率: {width}x{height}")
    print(f"实际帧率: {fps}")
    print("开始读取帧...\n")

    frame_count = 0
    start_time = cv2.getTickCount()

    import time

    try:
        # 读取几帧进行测试
        test_duration = min(duration, 5)  # 最多测试5秒
        start = time.time()

        while time.time() - start < test_duration:
            ret, frame = cap.read()

            if not ret:
                print(f"[错误] 无法读取帧（已读取 {frame_count} 帧）")
                break

            frame_count += 1

            # 每10帧打印一次进度
            if frame_count % 10 == 0:
                elapsed = time.time() - start
                current_fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"\r已读取 {frame_count} 帧 | FPS: {current_fps:.1f}", end="")

        print()  # 换行

    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消")

    # 统计信息
    total_time = time.time() - start
    avg_fps = frame_count / total_time if total_time > 0 else 0

    print(f"\n=== 测试结果 ===")
    print(f"总帧数: {frame_count}")
    print(f"总时长: {total_time:.2f} 秒")
    print(f"平均帧率: {avg_fps:.2f} FPS")

    if frame_count > 0:
        print(f"[成功] 摄像头工作正常")
    else:
        print(f"[失败] 摄像头无法读取帧")

    cap.release()

    return frame_count > 0


def save_test_frame(camera_id: int, output_path: str = "test_frame.jpg"):
    """
    保存一帧测试图像

    Args:
        camera_id: 摄像头ID
        output_path: 输出文件路径
    """
    print(f"\n=== 捕获测试帧 ===")

    # Windows: 使用DirectShow后端
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"[错误] 无法打开摄像头 {camera_id}")
        return False

    ret, frame = cap.read()

    if ret and frame is not None:
        cv2.imwrite(output_path, frame)
        print(f"[成功] 测试帧已保存到: {output_path}")
        print(f"  帧尺寸: {frame.shape}")
        cap.release()
        return True
    else:
        print("[错误] 无法读取帧")
        cap.release()
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("智能糖尿病助手 - 摄像头测试工具")
    print("=" * 60)
    print(f"平台: {platform.system()} {platform.release()}")
    print(f"OpenCV: {cv2.__version__}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 60)

    # 列出可用摄像头
    available_cameras = list_cameras()

    if not available_cameras:
        print("\n[错误] 未检测到可用的摄像头")
        print("\n故障排查:")
        print("  1. 确认摄像头已连接到电脑")
        print("  2. 检查摄像头指示灯是否亮起")
        print("  3. 关闭其他使用摄像头的程序（Teams, Zoom, Skype等）")
        print("  4. 在设备管理器中确认摄像头被识别")
        print("  5. 尝试重启摄像头（拔下USB插头，重新插入）")
        print("\nWindows用户提示:")
        print("  - 确保摄像头驱动已安装")
        print("  - 可以尝试使用DirectShow后端（已自动启用）")
        sys.exit(1)

    # 选择摄像头
    print(f"\n检测到 {len(available_cameras)} 个可用摄像头")
    print("可用摄像头ID:", ", ".join(map(str, available_cameras)))

    if len(available_cameras) == 1:
        camera_id = available_cameras[0]
        print(f"\n自动选择摄像头 {camera_id}")
    else:
        try:
            camera_id = input(f"\n请选择摄像头ID [{available_cameras[0]}]: ")
            camera_id = int(camera_id) if camera_id.strip() else available_cameras[0]
        except ValueError:
            camera_id = available_cameras[0]
            print(f"输入无效，使用摄像头 {camera_id}")

    # 先保存一帧测试图像
    print("\n" + "=" * 60)
    save_test_frame(camera_id, f"camera_{camera_id}_test.jpg")

    # 进行无GUI测试
    print("\n" + "=" * 60)
    success = test_camera_headless(camera_id)

    if success:
        print("\n" + "=" * 60)
        print("[成功] 摄像头测试完成")
        print(f"\n运行主程序:")
        print(f"  python src/main.py --camera {camera_id}")
        print(f"  或")
        print(f"  python scripts/quick_start.py {camera_id}")
        print("\n提示:")
        print("  - Windows用户使用DirectShow后端（已自动启用）")
        print("  - 如遇到显示问题，会自动使用无GUI模式")
    else:
        print("\n[失败] 摄像头测试失败")
        print("\n建议:")
        print("  1. 检查test_frame.jpg文件是否生成")
        print("  2. 尝试其他摄像头ID")
        print("  3. 查看上面的错误信息")


if __name__ == "__main__":
    main()

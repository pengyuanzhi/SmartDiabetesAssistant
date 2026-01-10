"""
测试摄像头设备

列出所有可用的摄像头并测试视频流
"""

import cv2
import sys


def list_cameras():
    """列出所有可用的摄像头"""
    print("\n=== 检测可用的摄像头 ===\n")

    available_cameras = []

    for i in range(5):  # 检测前5个设备
        cap = cv2.VideoCapture(i)

        if cap.isOpened():
            # 获取摄像头属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            backend = cap.getBackendName()

            print(f"✓ 摄像头 {i}:")
            print(f"  - 分辨率: {width}x{height}")
            print(f"  - 帧率: {fps}")
            print(f"  - 后端: {backend}")
            print()

            available_cameras.append(i)
            cap.release()
        else:
            print(f"✗ 摄像头 {i}: 不可用")

    return available_cameras


def test_camera(camera_id: int, duration: int = 10):
    """
    测试指定摄像头

    Args:
        camera_id: 摄像头ID
        duration: 测试时长（秒）
    """
    print(f"\n=== 测试摄像头 {camera_id} ===")
    print(f"测试时长: {duration} 秒")
    print("按 'q' 键提前退出\n")

    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 {camera_id}")
        return False

    # 设置分辨率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 获取实际设置
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    print(f"实际分辨率: {width}x{height}")
    print(f"实际帧率: {fps}\n")

    frame_count = 0
    start_time = cv2.getTickCount()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("❌ 无法读取帧")
            break

        frame_count += 1

        # 显示帧
        cv2.imshow(f'Camera {camera_id} Test', frame)

        # 计算FPS
        elapsed = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        current_fps = frame_count / elapsed if elapsed > 0 else 0

        # 在帧上显示信息
        info_text = f"Frame: {frame_count} | FPS: {current_fps:.1f} | Press 'q' to quit"
        cv2.putText(
            frame, info_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
        cv2.imshow(f'Camera {camera_id} Test', frame)

        # 检查按键
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n用户中断")
            break
        elif elapsed >= duration:
            print(f"\n达到测试时长 {duration} 秒")
            break

    # 统计信息
    total_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
    avg_fps = frame_count / total_time if total_time > 0 else 0

    print(f"\n=== 测试结果 ===")
    print(f"总帧数: {frame_count}")
    print(f"总时长: {total_time:.2f} 秒")
    print(f"平均帧率: {avg_fps:.2f} FPS")

    cap.release()
    cv2.destroyAllWindows()

    return True


def main():
    """主函数"""
    print("=" * 50)
    print("智能糖尿病助手 - 摄像头测试工具")
    print("=" * 50)

    # 列出可用摄像头
    available_cameras = list_cameras()

    if not available_cameras:
        print("\n❌ 未检测到可用的摄像头")
        print("请检查:")
        print("  1. 摄像头是否已连接")
        print("  2. 摄像头驱动是否已安装")
        print("  3. 摄像头是否被其他程序占用")
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

    # 测试摄像头
    success = test_camera(camera_id)

    if success:
        print("\n✅ 摄像头测试完成")
        print(f"\n运行主程序使用: python src/main.py --camera {camera_id}")
    else:
        print("\n❌ 摄像头测试失败")


if __name__ == "__main__":
    main()

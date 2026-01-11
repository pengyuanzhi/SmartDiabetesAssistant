# -*- coding: utf-8 -*-
"""
YOLO快速测试 - 一键验证目标检测功能
"""

import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def quick_test():
    """快速YOLO测试"""
    print("=" * 60)
    print("YOLO快速检测测试")
    print("=" * 60)
    print()

    try:
        # 1. 检查依赖
        print("[1/5] 检查依赖...")
        from ultralytics import YOLO
        print("✓ ultralytics已安装\n")

        # 2. 加载模型
        print("[2/5] 加载YOLO模型...")
        print("（首次运行会自动下载模型，约6MB）\n")
        model = YOLO("yolov8n.pt")
        print("✓ 模型加载成功\n")

        # 3. 创建测试图像
        print("[3/5] 创建测试图像...")
        import numpy as np

        # 创建640x480测试图像
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # 绘制一些测试对象
        cv2.rectangle(image, (100, 100), (250, 250), (255, 0, 0), -1)
        cv2.rectangle(image, (350, 150), (500, 300), (0, 255, 0), -1)
        cv2.circle(image, (400, 380), 60, (0, 0, 255), -1)

        # 添加文本
        cv2.putText(image, "YOLO Test", (220, 430),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        cv2.imwrite("test_input.jpg", image)
        print("✓ 测试图像创建完成: test_input.jpg\n")

        # 4. 执行检测
        print("[4/5] 执行目标检测...")
        results = model(image)

        num_detections = len(results[0].boxes)
        print(f"✓ 检测完成，发现 {num_detections} 个目标\n")

        # 5. 显示结果
        print("[5/5] 保存检测结果...")
        if num_detections > 0:
            print("\n检测详情:")
            for i, box in enumerate(results[0].boxes, 1):
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id]
                print(f"  [{i}] {class_name} - 置信度: {conf:.2f}")

        # 保存结果
        annotated = results[0].plot()
        cv2.imwrite("test_output.jpg", annotated)
        print("\n✓ 结果已保存: test_output.jpg")

        # 成功总结
        print("\n" + "=" * 60)
        print("测试成功！")
        print("=" * 60)
        print("\n生成的文件:")
        print("  - test_input.jpg (输入图像)")
        print("  - test_output.jpg (检测结果)")

        print("\n提示:")
        print("  - 可以打开test_output.jpg查看检测结果")
        print("  - 不同颜色框代表不同类别")

        return True

    except ImportError:
        print("\n✗ 缺少依赖库")
        print("\n请安装:")
        print("  pip install ultralytics opencv-python")
        return False

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\nYOLO快速检测测试")
    print("=" * 60)
    print("此脚本将自动完成YOLO目标检测的完整测试\n")

    success = quick_test()

    if success:
        print("\n✓ 所有测试通过！YOLO功能正常")
    else:
        print("\n✗ 测试失败，请检查错误信息")

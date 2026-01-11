# -*- coding: utf-8 -*-
"""
YOLO目标检测测试脚本

测试YOLOv8模型的目标检测功能，用于注射部位识别
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class YOLOTester:
    """YOLO测试器"""

    def __init__(self):
        """初始化测试器"""
        self.model = None
        self.class_names = {
            0: "腹部",
            1: "大腿",
            2: "上臂",
            3: "臀部"
        }
        self.colors = {
            0: (255, 0, 0),    # 红色 - 腹部
            1: (0, 255, 0),    # 绿色 - 大腿
            2: (0, 0, 255),    # 蓝色 - 上臂
            3: (255, 255, 0)   # 黄色 - 臀部
        }

    def check_ultralytics(self):
        """检查ultralytics是否安装"""
        print("\n=== 检查依赖 ===\n")
        try:
            import ultralytics
            print("✓ ultralytics已安装")
            try:
                version = ultralytics.__version__
                print(f"  版本: {version}")
            except AttributeError:
                print("  版本: 未知（无法获取版本信息）")
            return True
        except ImportError:
            print("✗ ultralytics未安装")
            print("\n安装命令:")
            print("  pip install ultralytics")
            return False

    def test_model_loading(self, model_path: str = "yolov8n.pt"):
        """
        测试模型加载

        Args:
            model_path: 模型路径
        """
        print("\n=== 测试模型加载 ===\n")

        try:
            from ultralytics import YOLO

            print(f"正在加载模型: {model_path}")
            print("提示: 首次运行会自动下载模型（约6MB）\n")

            self.model = YOLO(model_path)

            print("✓ 模型加载成功")
            print(f"  模型类型: {self.model.__class__.__name__}")
            print(f"  任务类型: {self.model.task}")
            print(f"  类别数: {len(self.model.names)}")

            # 显示类别
            print("\n检测类别:")
            for idx, name in self.model.names.items():
                print(f"  {idx}: {name}")

            return True

        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            return False

    def test_image_detection(self, image_path: str = None):
        """
        测试图像目标检测

        Args:
            image_path: 图像路径（None则使用测试图像）
        """
        print("\n=== 测试图像检测 ===\n")

        if self.model is None:
            print("✗ 模型未加载，请先运行模型加载测试")
            return False

        try:
            # 如果没有提供图像，创建测试图像
            if image_path is None or not Path(image_path).exists():
                print("创建测试图像...")
                image = self._create_test_image()
                print("✓ 测试图像创建完成\n")
            else:
                image = cv2.imread(image_path)
                if image is None:
                    print(f"✗ 无法读取图像: {image_path}")
                    return False
                print(f"✓ 图像加载成功: {image_path}")

            # 执行检测
            print("正在执行目标检测...")
            results = self.model(image)

            print(f"✓ 检测完成，发现 {len(results[0].boxes)} 个目标\n")

            # 处理检测结果
            if len(results[0].boxes) > 0:
                print("检测结果:")
                for i, box in enumerate(results[0].boxes, 1):
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()

                    class_name = self.model.names[cls_id]

                    print(f"  [{i}] {class_name}")
                    print(f"      置信度: {conf:.2f}")
                    print(f"      边界框: {xyxy}")

                # 可视化结果
                output_path = "test_yolo_result.jpg"
                self._visualize_results(image, results[0], output_path)
                print(f"\n✓ 检测结果已保存: {output_path}")
            else:
                print("  未检测到目标")

            return True

        except Exception as e:
            print(f"✗ 图像检测失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_video_detection(self, video_path: str = None, duration: int = 5):
        """
        测试视频目标检测

        Args:
            video_path: 视频路径（None则使用摄像头）
            duration: 测试时长（秒）
        """
        print("\n=== 测试视频检测 ===\n")

        if self.model is None:
            print("✗ 模型未加载，请先运行模型加载测试")
            return False

        try:
            # 打开视频源
            if video_path:
                cap = cv2.VideoCapture(video_path)
                print(f"使用视频文件: {video_path}")
            else:
                cap = cv2.VideoCapture(0)
                print("使用摄像头")

            if not cap.isOpened():
                print("✗ 无法打开视频源")
                return False

            # 获取视频信息
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            print(f"✓ 视频源打开成功")
            print(f"  分辨率: {width}x{height}")
            print(f"  帧率: {fps}")
            print(f"\n开始检测（持续 {duration} 秒）...\n")

            # 处理视频帧
            frame_count = 0
            max_frames = fps * duration

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # 执行检测
                results = self.model(frame)

                # 显示结果
                annotated_frame = results[0].plot()

                # 显示检测数量
                num_detections = len(results[0].boxes)
                cv2.putText(annotated_frame, f"Detections: {num_detections}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 255, 0), 2)

                cv2.imshow("YOLO Detection", annotated_frame)

                frame_count += 1

                # 按q退出
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n用户中断")
                    break

            cap.release()
            cv2.destroyAllWindows()

            print(f"\n✓ 视频检测完成，处理了 {frame_count} 帧")

            return True

        except Exception as e:
            print(f"✗ 视频检测失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_custom_classes(self):
        """测试自定义类别（注射部位）"""
        print("\n=== 测试自定义类别 ===\n")

        if self.model is None:
            print("✗ 模型未加载，请先运行模型加载测试")
            return False

        try:
            # 创建包含多个测试区域的图像
            print("创建测试图像（包含多个注射部位）...")
            image = self._create_multi_region_image()
            print("✓ 测试图像创建完成\n")

            # 执行检测
            print("正在执行检测...")
            results = self.model(image, verbose=False)

            print(f"✓ 检测完成，发现 {len(results[0].boxes)} 个目标\n")

            # 分析结果
            detected_classes = {}
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                class_name = self.model.names[cls_id]
                detected_classes[class_name] = detected_classes.get(class_name, 0) + 1

            if detected_classes:
                print("检测到的部位:")
                for name, count in detected_classes.items():
                    print(f"  {name}: {count} 个")

                # 可视化
                output_path = "test_yolo_multi_region.jpg"
                self._visualize_with_labels(image, results[0], output_path)
                print(f"\n✓ 检测结果已保存: {output_path}")

                # 评估
                self._evaluate_detection(detected_classes)
            else:
                print("未检测到任何目标")
                print("提示: 这可能是因为模型未针对注射部位训练")
                print("建议: 使用自定义训练的模型")

            return True

        except Exception as e:
            print(f"✗ 自定义类别测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_injection_site_recommendation(self):
        """测试注射部位推荐"""
        print("\n=== 测试注射部位推荐 ===\n")

        # 定义推荐部位
        recommended_sites = [0, 1, 2]  # 腹部、大腿、上臂

        print("推荐的注射部位:")
        for site_id in recommended_sites:
            print(f"  {site_id}: {self.class_names[site_id]} ✓")

        print("\n不推荐的注射部位:")
        for site_id in self.class_names:
            if site_id not in recommended_sites:
                print(f"  {site_id}: {self.class_names[site_id]} ✗")

        return True

    def _create_test_image(self, width: int = 640, height: int = 480) -> np.ndarray:
        """创建测试图像"""
        # 创建白色背景
        image = np.ones((height, width, 3), dtype=np.uint8) * 255

        # 绘制一些矩形框模拟目标
        cv2.rectangle(image, (100, 100), (200, 200), (0, 0, 255), -1)  # 红色矩形
        cv2.rectangle(image, (300, 150), (400, 250), (0, 255, 0), -1)  # 绿色矩形
        cv2.rectangle(image, (500, 200), (600, 300), (255, 0, 0), -1)  # 蓝色矩形

        # 添加文本
        cv2.putText(image, "YOLO Test Image", (150, 400),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        return image

    def _create_multi_region_image(self, width: int = 640, height: int = 480) -> np.ndarray:
        """创建包含多个区域的测试图像"""
        # 创建背景
        image = np.ones((height, width, 3), dtype=np.uint8) * 240

        # 绘制模拟注射部位的椭圆区域
        regions = [
            (320, 240, 100, (255, 200, 200)),  # 腹部 - 中央
            (150, 350, 80, (200, 200, 255)),   # 大腿 - 左下
            (500, 200, 70, (200, 255, 200)),   # 上臂 - 右上
            (100, 100, 60, (255, 255, 200)),   # 臀部 - 左上
        ]

        for x, y, radius, color in regions:
            cv2.circle(image, (x, y), radius, color, -1)
            cv2.circle(image, (x, y), radius, (0, 0, 0), 2)

        # 添加标签
        labels = ["Abdomen", "Thigh", "Upper Arm", "Buttock"]
        positions = [(320, 240), (150, 350), (500, 200), (100, 100)]

        for label, (x, y) in zip(labels, positions):
            cv2.putText(image, label, (x - 30, y), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, (0, 0, 0), 1)

        return image

    def _visualize_results(self, image: np.ndarray, result, output_path: str):
        """可视化检测结果"""
        annotated = result.plot()
        cv2.imwrite(output_path, annotated)

    def _visualize_with_labels(self, image: np.ndarray, result, output_path: str):
        """可视化结果并添加自定义标签"""
        annotated = image.copy()

        for box in result.boxes:
            # 获取边界框
            xyxy = box.xyxy[0].tolist()
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            # 绘制边界框
            color = self.colors.get(cls_id, (255, 255, 255))
            cv2.rectangle(annotated,
                       (int(xyxy[0]), int(xyxy[1])),
                       (int(xyxy[2]), int(xyxy[3])),
                       color, 2)

            # 添加标签
            label = f"{self.class_names.get(cls_id, f'Class{cls_id}')}: {conf:.2f}"
            cv2.putText(annotated, label,
                       (int(xyxy[0]), int(xyxy[1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imwrite(output_path, annotated)

    def _evaluate_detection(self, detected_classes: Dict[str, int]):
        """评估检测结果"""
        print("\n检测评估:")

        # 检查是否检测到推荐部位
        recommended = ["腹部", "大腿", "上臂"]
        detected_recommended = [cls for cls in detected_classes if cls in recommended]

        if detected_recommended:
            print(f"✓ 检测到推荐部位: {', '.join(detected_recommended)}")
        else:
            print("✗ 未检测到推荐部位")

        # 检查是否检测到不推荐部位
        not_recommended = ["臀部"]
        detected_not_recommended = [cls for cls in detected_classes if cls in not_recommended]

        if detected_not_recommended:
            print(f"⚠ 检测到不推荐部位: {', '.join(detected_not_recommended)}")
        else:
            print("✓ 未检测到不推荐部位")


def interactive_menu():
    """交互式菜单"""
    print("=" * 60)
    print("        YOLO目标检测测试工具")
    print("=" * 60)

    tester = YOLOTester()

    while True:
        print("\n" + "=" * 60)
        print("请选择操作:")
        print("  1. 检查依赖")
        print("  2. 测试模型加载")
        print("  3. 测试图像检测")
        print("  4. 测试视频检测（摄像头）")
        print("  5. 测试自定义类别")
        print("  6. 查看注射部位推荐")
        print("  0. 退出")
        print()

        choice = input("请选择 (0-6): ").strip()

        if choice == "0":
            print("退出程序")
            break

        elif choice == "1":
            tester.check_ultralytics()

        elif choice == "2":
            model_path = input("请输入模型路径 (直接回车使用yolov8n.pt): ").strip()
            if not model_path:
                model_path = "yolov8n.pt"
            tester.test_model_loading(model_path)

        elif choice == "3":
            image_path = input("请输入图像路径 (直接回车使用测试图像): ").strip()
            if not image_path:
                image_path = None
            tester.test_image_detection(image_path)

        elif choice == "4":
            duration = input("请输入测试时长（秒，直接回车使用5秒）: ").strip()
            if not duration:
                duration = 5
            else:
                duration = int(duration)

            video_path = input("请输入视频路径 (直接回车使用摄像头): ").strip()
            if not video_path:
                video_path = None

            tester.test_video_detection(video_path, duration)

        elif choice == "5":
            tester.test_custom_classes()

        elif choice == "6":
            tester.test_injection_site_recommendation()

        else:
            print("无效选择，请重试")


def main():
    """主函数"""
    print("\nYOLO目标检测测试工具")
    print("项目: 智能糖尿病助手\n")
    print("此工具用于测试YOLOv8目标检测功能")
    print("主要用于注射部位识别\n")

    interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消测试")
    except Exception as e:
        print(f"\n[错误] 测试异常: {e}")
        import traceback
        traceback.print_exc()

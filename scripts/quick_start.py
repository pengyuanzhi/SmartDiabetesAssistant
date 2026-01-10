"""
快速启动脚本 - PC端调试版本

简化版启动程序，用于快速测试和开发
"""

import asyncio
import cv2
import time
from pathlib import Path

from loguru import logger

# 添加src目录到路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents import VisionAgent, DecisionAgent
from processing import VideoCamera


class QuickStartDemo:
    """快速启动演示"""

    def __init__(self, camera_id: int = 0):
        """初始化"""
        self.camera_id = camera_id
        self.camera = None
        self.running = False

        # 初始化智能体
        self.vision_agent = VisionAgent()
        self.decision_agent = DecisionAgent()

        logger.info("✓ 快速启动演示已初始化")

    async def start(self):
        """启动演示"""
        logger.info(f"启动摄像头 {self.camera_id}...")

        self.camera = VideoCamera(self.camera_id)
        self.camera.start()

        self.running = True

        logger.info("开始处理视频流...")
        logger.info("按 'q' 键退出\n")

        frame_count = 0
        start_time = time.time()

        try:
            while self.running:
                # 读取帧
                frame = self.camera.read_frame()

                if frame is None:
                    logger.warning("无法读取帧")
                    break

                frame_count += 1

                # 每5帧处理一次（降低CPU占用）
                if frame_count % 5 == 0:
                    # 准备数据
                    frame_data = {
                        "image": frame,
                        "timestamp": time.time(),
                        "frame_id": frame_count
                    }

                    # 视觉处理
                    vision_results = await self.vision_agent.process_frame(frame_data)

                    # 决策判断
                    context = {
                        "injection_angle": vision_results.get("angle", 0),
                        "injection_site": vision_results.get("site", {}),
                        "injection_speed": 0,
                        "current_step": "monitoring"
                    }

                    alerts = await self.decision_agent.evaluate(context)

                    # 显示结果
                    display_frame = self._draw_results(
                        frame.copy(),
                        vision_results,
                        alerts
                    )

                    # 显示告警
                    if alerts:
                        logger.warning(f"告警: {alerts[0]['message']}")

                else:
                    display_frame = frame

                # 显示帧
                cv2.imshow("Smart Diabetes Assistant - Quick Start", display_frame)

                # 计算FPS
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0

                # 显示FPS
                print(f"\r帧: {frame_count} | FPS: {fps:.1f}", end="")

                # 检查按键
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("\n用户中断")
                    break

        except KeyboardInterrupt:
            logger.info("\n收到中断信号")

        finally:
            # 统计信息
            total_time = time.time() - start_time
            avg_fps = frame_count / total_time if total_time > 0 else 0

            logger.info(f"\n=== 统计信息 ===")
            logger.info(f"总帧数: {frame_count}")
            logger.info(f"总时长: {total_time:.2f} 秒")
            logger.info(f"平均帧率: {avg_fps:.2f} FPS")

            self.stop()

    def _draw_results(self, frame, vision_results, alerts):
        """在帧上绘制结果"""
        # 绘制姿态骨架
        if vision_results.get("pose"):
            pose = vision_results["pose"]
            self._draw_pose_skeleton(frame, pose.get("keypoints", {}))

        # 绘制检测框
        if vision_results.get("site"):
            site = vision_results["site"]
            self._draw_detection_box(frame, site)

        # 绘制角度
        angle = vision_results.get("angle", 0)
        if angle > 0:
            color = (0, 255, 0) if 45 <= angle <= 90 else (0, 0, 255)
            cv2.putText(
                frame, f"角度: {angle:.1f}°", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2
            )

        # 绘制告警
        if alerts:
            alert = alerts[0]
            text = alert["message"][:30]
            color = (0, 0, 255) if alert["severity"] == "critical" else (0, 165, 255)

            cv2.putText(
                frame, text, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2
            )

        return frame

    def _draw_pose_skeleton(self, frame, keypoints):
        """绘制姿态骨架"""
        # 定义骨骼连接
        skeleton_pairs = [
            ("shoulder", "elbow"),
            ("elbow", "wrist"),
        ]

        for p1_name, p2_name in skeleton_pairs:
            p1 = keypoints.get(p1_name)
            p2 = keypoints.get(p2_name)

            if p1 and p2 and p1[2] > 0.5 and p2[2] > 0.5:
                cv2.line(
                    frame,
                    (int(p1[0]), int(p1[1])),
                    (int(p2[0]), int(p2[1])),
                    (0, 255, 0), 2
                )

    def _draw_detection_box(self, frame, detection):
        """绘制检测框"""
        bbox = detection.get("bbox")
        if bbox:
            x, y, w, h = [int(v) for v in bbox]
            color = (0, 255, 0) if detection.get("is_recommended") else (0, 165, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            # 标签
            label = detection.get("chinese_name", detection.get("class_name", ""))
            cv2.putText(
                frame, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

    def stop(self):
        """停止演示"""
        self.running = False

        if self.camera:
            self.camera.stop()

        cv2.destroyAllWindows()
        logger.info("✓ 演示已停止")


async def main():
    """主函数"""
    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    print("\n" + "=" * 60)
    print("智能糖尿病助手 - PC端快速启动")
    print("=" * 60 + "\n")

    # 获取摄像头ID
    camera_id = 0
    if len(sys.argv) > 1:
        try:
            camera_id = int(sys.argv[1])
        except ValueError:
            camera_id = 0

    # 创建并启动演示
    demo = QuickStartDemo(camera_id)

    try:
        await demo.start()
    except Exception as e:
        logger.error(f"运行错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        demo.stop()


if __name__ == "__main__":
    # Windows环境
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

"""
实时视频处理管道

功能：
1. 视频流采集
2. 异步帧处理
3. 生产者-消费者模式
4. 性能监控
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable
from collections import deque
import threading

import cv2
import numpy as np


class VideoCamera:
    """摄像头管理类"""

    def __init__(self, camera_id: int = 0, resolution: tuple = (1920, 1080)):
        """
        初始化摄像头

        Args:
            camera_id: 摄像头ID
            resolution: 分辨率 (width, height)
        """
        self.camera_id = camera_id
        self.resolution = resolution
        self.cap = None

    def start(self):
        """启动摄像头"""
        self.cap = cv2.VideoCapture(self.camera_id)

        if not self.cap.isOpened():
            raise RuntimeError(f"无法打开摄像头 {self.camera_id}")

        # 设置分辨率
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        # 设置帧率
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print(f"[VideoCamera] 摄像头已启动: {self.camera_id}")

    def read_frame(self) -> Optional[np.ndarray]:
        """
        读取一帧

        Returns:
            图像数组（BGR格式）或None
        """
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()

        if not ret:
            return None

        return frame

    def stop(self):
        """停止摄像头"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("[VideoCamera] 摄像头已停止")


class VideoProcessingPipeline:
    """
    实时视频处理管道

    使用异步生产者-消费者模式实现高性能视频流处理。
    """

    def __init__(
        self,
        camera_id: int = 0,
        queue_size: int = 30,
        target_fps: int = 30
    ):
        """
        初始化视频处理管道

        Args:
            camera_id: 摄像头ID
            queue_size: 帧队列大小
            target_fps: 目标帧率
        """
        self.camera = VideoCamera(camera_id)
        self.queue_size = queue_size
        self.target_fps = target_fps

        # 帧队列
        self.frame_queue: asyncio.Queue = None

        # 处理回调
        self.frame_processor: Callable = None

        # 运行状态
        self.running = False
        self.producer_task = None
        self.consumer_task = None

        # 性能统计
        self.stats = {
            "frames_processed": 0,
            "frames_dropped": 0,
            "avg_fps": 0.0,
            "avg_latency_ms": 0.0
        }

    async def start(self, frame_processor: Callable):
        """
        启动视频处理管道

        Args:
            frame_processor: 帧处理回调函数
                async def processor(frame_data: dict) -> dict:
                    ...
        """
        print("[VideoPipeline] 启动视频处理管道...")

        # 初始化队列
        self.frame_queue = asyncio.Queue(maxsize=self.queue_size)

        # 设置处理器
        self.frame_processor = frame_processor

        # 启动摄像头
        self.camera.start()

        # 启动生产者和消费者
        self.running = True

        self.producer_task = asyncio.create_task(self._produce_frames())
        self.consumer_task = asyncio.create_task(self._consume_frames())

        print("[VideoPipeline] 视频处理管道已启动")

    async def _produce_frames(self):
        """
        帧生产者 - 从摄像头读取帧并放入队列
        """
        frame_interval = 1.0 / self.target_fps

        while self.running:
            start_time = time.time()

            # 读取帧
            frame = self.camera.read_frame()

            if frame is not None:
                frame_data = {
                    "image": frame,
                    "timestamp": time.time(),
                    "frame_id": self.stats["frames_processed"]
                }

                # 尝试放入队列
                try:
                    self.frame_queue.put_nowait(frame_data)
                    self.stats["frames_processed"] += 1
                except asyncio.QueueFull:
                    # 队列满，丢弃最旧的帧
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame_data)
                        self.stats["frames_dropped"] += 1
                    except:
                        pass

            # 控制帧率
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_interval - elapsed)
            await asyncio.sleep(sleep_time)

    async def _consume_frames(self):
        """
        帧消费者 - 从队列取出帧并处理
        """
        latencies = []

        while self.running:
            try:
                # 获取帧（带超时）
                frame_data = await asyncio.wait_for(
                    self.frame_queue.get(),
                    timeout=1.0
                )

                start_time = time.time()

                # 处理帧
                if self.frame_processor:
                    try:
                        await self.frame_processor(frame_data)
                    except Exception as e:
                        print(f"[VideoPipeline] 帧处理错误: {e}")

                # 记录延迟
                latency = time.time() - start_time
                latencies.append(latency)

                # 保持最近100次记录
                if len(latencies) > 100:
                    latencies.pop(0)

                self.stats["avg_latency_ms"] = sum(latencies) / len(latencies) * 1000

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[VideoPipeline] 消费者错误: {e}")

    async def stop(self):
        """停止视频处理管道"""
        print("[VideoPipeline] 停止视频处理管道...")

        self.running = False

        # 停止任务
        if self.producer_task:
            self.producer_task.cancel()
        if self.consumer_task:
            self.consumer_task.cancel()

        # 等待任务结束
        try:
            await asyncio.gather(self.producer_task, self.consumer_task, return_exceptions=True)
        except:
            pass

        # 停止摄像头
        self.camera.stop()

        # 计算平均FPS
        duration = time.time() - getattr(self, "start_time", time.time())
        if duration > 0:
            self.stats["avg_fps"] = self.stats["frames_processed"] / duration

        print(f"[VideoPipeline] 统计: {self.stats['frames_processed']} 帧, "
              f"{self.stats['frames_dropped']} 丢弃, "
              f"{self.stats['avg_fps']:.1f} FPS, "
              f"{self.stats['avg_latency_ms']:.1f} ms 延迟")

    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        return self.stats.copy()


class FramePreprocessor:
    """帧预处理器"""

    def __init__(self, target_size: tuple = None):
        """
        初始化预处理器

        Args:
            target_size: 目标尺寸 (width, height)
        """
        self.target_size = target_size

    def process(self, frame: np.ndarray) -> np.ndarray:
        """
        预处理帧

        Args:
            frame: 输入帧（BGR）

        Returns:
            处理后的帧
        """
        # 调整大小
        if self.target_size:
            frame = cv2.resize(frame, self.target_size)

        # 归一化
        frame = frame.astype(np.float32) / 255.0

        return frame

    def resize_with_aspect_ratio(
        self,
        frame: np.ndarray,
        target_size: tuple,
        keep_ratio: bool = True
    ) -> np.ndarray:
        """
        保持宽高比调整大小

        Args:
            frame: 输入帧
            target_size: 目标尺寸 (width, height)
            keep_ratio: 是否保持宽高比

        Returns:
            调整后的帧
        """
        if not keep_ratio:
            return cv2.resize(frame, target_size)

        # 计算缩放比例
        h, w = frame.shape[:2]
        target_w, target_h = target_size

        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # 调整大小
        resized = cv2.resize(frame, (new_w, new_h))

        # 填充到目标尺寸
        delta_w = target_w - new_w
        delta_h = target_h - new_h
        top, bottom = delta_h // 2, delta_h - delta_h // 2
        left, right = delta_w // 2, delta_w - delta_w // 2

        padded = cv2.copyMakeBorder(
            resized, top, bottom, left, right,
            cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )

        return padded


class ResultPostprocessor:
    """结果后处理器"""

    def process(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理推理结果

        Args:
            results: 原始结果

        Returns:
            处理后的结果
        """
        # TODO: 实现后处理逻辑
        # 例如：NMS、阈值过滤、坐标转换等

        return results

    def draw_overlay(
        self,
        frame: np.ndarray,
        results: Dict[str, Any]
    ) -> np.ndarray:
        """
        在帧上绘制结果叠加层

        Args:
            frame: 原始帧
            results: 推理结果

        Returns:
            绘制后的帧
        """
        output = frame.copy()

        # 绘制骨架
        if results.get("pose"):
            self._draw_pose(output, results["pose"])

        # 绘制检测框
        if results.get("site"):
            self._draw_detection(output, results["site"])

        # 绘制角度
        if results.get("angle"):
            self._draw_angle(output, results["angle"])

        return output

    def _draw_pose(self, frame: np.ndarray, pose: Dict[str, Any]):
        """绘制姿态骨架"""
        # TODO: 实现骨架绘制
        pass

    def _draw_detection(self, frame: np.ndarray, detection: Dict[str, Any]):
        """绘制检测框"""
        bbox = detection.get("bbox")
        if bbox:
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def _draw_angle(self, frame: np.ndarray, angle: float):
        """绘制角度信息"""
        text = f"角度: {angle:.1f}°"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

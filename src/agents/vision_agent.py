"""
视觉智能体 - 负责图像采集、模型推理和结果解析

功能：
1. 图像采集和预处理
2. 姿态估计（注射角度检测）
3. 目标检测（注射部位识别）
4. 光流计算（速度监测）
"""

import asyncio
import time
from typing import Dict, Any, List
from pathlib import Path
import yaml

import cv2
import numpy as np


class VisionAgent:
    """
    视觉智能体 - 处理所有视觉相关任务

    调用多个AI模型进行并行推理，返回综合的视觉分析结果。
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化视觉智能体

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # 初始化模型（延迟加载）
        self.pose_estimator = None
        self.site_detector = None
        self.flow_calculator = None

        # 缓存上一帧（用于光流计算）
        self.prev_frame = None

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_models(self):
        """
        延迟加载模型

        在首次推理时才加载模型，避免启动时间过长。
        """
        if self.pose_estimator is None:
            print("[VisionAgent] 加载姿态估计模型...")
            # TODO: 实际加载RTMPose模型
            # self.pose_estimator = RTMPoseLite(
            #     model_path=self.config['pose_estimation']['model_path']
            # )
            print("[VisionAgent] 姿态估计模型加载完成")

        if self.site_detector is None:
            print("[VisionAgent] 加载目标检测模型...")
            # TODO: 实际加载YOLOv8模型
            # self.site_detector = YOLOv8(
            #     model_path=self.config['object_detection']['model_path']
            # )
            print("[VisionAgent] 目标检测模型加载完成")

        if self.flow_calculator is None:
            print("[VisionAgent] 初始化光流计算器...")
            # TODO: 初始化光流计算器
            # self.flow_calculator = LiteFlowNet(
            #     model_path=self.config['optical_flow']['model_path']
            # )
            print("[VisionAgent] 光流计算器初始化完成")

    async def process_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单帧图像（核心接口）

        并发运行多个视觉模型，返回综合结果。

        Args:
            frame_data: 包含图像数据的字典
                {
                    "image": np.ndarray,  # BGR图像
                    "timestamp": float,
                    "frame_id": int
                }

        Returns:
            视觉分析结果字典
                {
                    "pose": dict,  # 姿态估计结果
                    "site": dict,  # 部位检测结果
                    "flow": dict,  # 光流计算结果
                    "timestamp": float
                }
        """
        # 确保模型已加载
        self._load_models()

        # 提取图像
        image = frame_data.get("image")
        timestamp = frame_data.get("timestamp", time.time())

        if image is None:
            return self._empty_result(timestamp)

        # 并发运行多个视觉任务
        tasks = [
            self._estimate_pose(image),
            self._detect_site(image),
            self._calculate_flow(image)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 组装结果
        pose_result = results[0] if not isinstance(results[0], Exception) else {}
        site_result = results[1] if not isinstance(results[1], Exception) else {}
        flow_result = results[2] if not isinstance(results[2], Exception) else {}

        return {
            "pose": pose_result,
            "site": site_result,
            "flow": flow_result,
            "timestamp": timestamp
        }

    async def _estimate_pose(self, image: np.ndarray) -> Dict[str, Any]:
        """
        姿态估计 - 检测人体关键点

        Args:
            image: BGR图像

        Returns:
            姿态结果字典
                {
                    "keypoints": {
                        "shoulder": [x, y, confidence],
                        "elbow": [x, y, confidence],
                        "wrist": [x, y, confidence],
                        ...
                    },
                    "bbox": [x, y, w, h],
                    "confidence": float
                }
        """
        try:
            # TODO: 实际的RTMPose推理
            # result = self.pose_estimator.detect(image)

            # 模拟结果（用于演示）
            keypoints = {
                "shoulder": [320, 200, 0.95],
                "elbow": [350, 300, 0.92],
                "wrist": [380, 400, 0.88],
                "hip": [300, 400, 0.90],
                "knee": [320, 500, 0.85],
                "ankle": [340, 600, 0.80]
            }

            return {
                "keypoints": keypoints,
                "bbox": [250, 150, 200, 500],
                "confidence": 0.90
            }

        except Exception as e:
            print(f"[VisionAgent] 姿态估计错误: {e}")
            return {}

    async def _detect_site(self, image: np.ndarray) -> Dict[str, Any]:
        """
        注射部位检测 - 识别腹部、大腿、上臂等

        Args:
            image: BGR图像

        Returns:
            检测结果字典
                {
                    "class_id": int,
                    "class_name": str,  # "abdomen", "thigh", "upper_arm", "buttock"
                    "confidence": float,
                    "bbox": [x, y, w, h],
                    "is_recommended": bool
                }
        """
        try:
            # TODO: 实际的YOLOv8推理
            # result = self.site_detector.detect(image)

            # 模拟结果（用于演示）
            return {
                "class_id": 0,
                "class_name": "abdomen",
                "chinese_name": "腹部",
                "confidence": 0.92,
                "bbox": [300, 350, 150, 100],
                "is_recommended": True
            }

        except Exception as e:
            print(f"[VisionAgent] 部位检测错误: {e}")
            return {}

    async def _calculate_flow(self, image: np.ndarray) -> Dict[str, Any]:
        """
        光流计算 - 计算运动速度

        Args:
            image: BGR图像

        Returns:
            光流结果字典
                {
                    "vectors": [
                        {"x": x, "y": y, "dx": dx, "dy": dy},
                        ...
                    ],
                    "avg_speed": float
                }
        """
        try:
            if self.prev_frame is None:
                self.prev_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                return {}

            current_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # TODO: 实际的LiteFlowNet推理
            # flow = self.flow_calculator.calculate(self.prev_frame, current_gray)

            # 使用OpenCV的Farneback方法作为临时方案
            flow = cv2.calcOpticalFlowFarneback(
                self.prev_frame, current_gray, None,
                pyr_scale=0.5, levels=3, winsize=15,
                iterations=3, poly_n=5, poly_sigma=1.2,
                flags=0
            )

            # 计算运动向量
            h, w = flow.shape[:2]
            step = 10  # 采样步长
            vectors = []

            for y in range(0, h, step):
                for x in range(0, w, step):
                    dx = float(flow[y, x, 0])
                    dy = float(flow[y, x, 1])
                    speed = (dx**2 + dy**2) ** 0.5

                    if speed > 1.0:  # 只保留显著运动
                        vectors.append({
                            "x": float(x),
                            "y": float(y),
                            "dx": dx,
                            "dy": dy,
                            "speed": speed
                        })

            # 计算平均速度
            avg_speed = 0.0
            if vectors:
                avg_speed = sum(v["speed"] for v in vectors) / len(vectors)

            self.prev_frame = current_gray

            return {
                "vectors": vectors,
                "avg_speed": avg_speed
            }

        except Exception as e:
            print(f"[VisionAgent] 光流计算错误: {e}")
            return {}

    def _empty_result(self, timestamp: float) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "pose": {},
            "site": {},
            "flow": {},
            "timestamp": timestamp
        }

    def preprocess_image(
        self,
        image: np.ndarray,
        target_size: tuple = None,
        normalize: bool = True
    ) -> np.ndarray:
        """
        图像预处理

        Args:
            image: BGR图像
            target_size: 目标尺寸 (width, height)
            normalize: 是否归一化

        Returns:
            预处理后的图像
        """
        # 调整大小
        if target_size:
            image = cv2.resize(image, target_size)

        # 归一化
        if normalize:
            image = image.astype(np.float32) / 255.0

        return image

    def draw_results(
        self,
        image: np.ndarray,
        pose_result: Dict[str, Any],
        site_result: Dict[str, Any],
        flow_result: Dict[str, Any]
    ) -> np.ndarray:
        """
        在图像上绘制检测结果（用于可视化）

        Args:
            image: 原始图像
            pose_result: 姿态结果
            site_result: 部位检测结果
            flow_result: 光流结果

        Returns:
            绘制后的图像
        """
        output = image.copy()

        # 绘制姿态骨架
        if pose_result and pose_result.get("keypoints"):
            self._draw_skeleton(output, pose_result["keypoints"])

        # 绘制检测框
        if site_result and site_result.get("bbox"):
            self._draw_bbox(output, site_result)

        # 绘制光流向量
        if flow_result and flow_result.get("vectors"):
            self._draw_flow_vectors(output, flow_result["vectors"])

        return output

    def _draw_skeleton(self, image: np.ndarray, keypoints: Dict[str, List[float]]):
        """绘制人体骨架"""
        # 定义骨骼连接
        skeleton_pairs = [
            ("shoulder", "elbow"),
            ("elbow", "wrist"),
            ("hip", "knee"),
            ("knee", "ankle"),
            ("shoulder", "hip")
        ]

        for p1_name, p2_name in skeleton_pairs:
            p1 = keypoints.get(p1_name)
            p2 = keypoints.get(p2_name)

            if p1 and p2 and p1[2] > 0.5 and p2[2] > 0.5:
                cv2.line(
                    image,
                    (int(p1[0]), int(p1[1])),
                    (int(p2[0]), int(p2[1])),
                    (0, 255, 0), 2
                )

        # 绘制关键点
        for name, point in keypoints.items():
            if point[2] > 0.5:
                cv2.circle(
                    image,
                    (int(point[0]), int(point[1])),
                    5, (0, 0, 255), -1
                )

    def _draw_bbox(self, image: np.ndarray, detection: Dict[str, Any]):
        """绘制检测框"""
        bbox = detection["bbox"]
        x, y, w, h = [int(v) for v in bbox]

        # 根据是否推荐选择颜色
        color = (0, 255, 0) if detection.get("is_recommended") else (0, 165, 255)

        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)

        # 绘制标签
        label = detection.get("chinese_name", detection.get("class_name", ""))
        confidence = detection.get("confidence", 0)
        text = f"{label}: {confidence:.2f}"

        cv2.putText(
            image, text, (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
        )

    def _draw_flow_vectors(self, image: np.ndarray, vectors: List[Dict[str, float]]):
        """绘制光流向量"""
        for v in vectors[:20]:  # 只绘制前20个向量（避免太密集）
            x, y = int(v["x"]), int(v["y"])
            dx, dy = v["dx"] * 5, v["dy"] * 5  # 放大5倍以便观察

            cv2.arrowedLine(
                image, (x, y),
                (int(x + dx), int(y + dy)),
                (255, 0, 0), 1
            )

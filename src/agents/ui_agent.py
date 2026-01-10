"""
UI智能体 - 负责用户界面显示

功能：
1. 实时视频显示
2. 检测结果叠加
3. 进度提示
4. 错误警告显示
"""

import asyncio
import time
from typing import Dict, Any
from pathlib import Path
import yaml

import numpy as np

# 可选导入 cv2（PC端可能未安装）
try:
    import cv2
    _has_cv2 = True
except ImportError:
    cv2 = None
    _has_cv2 = False


class UIAgent:
    """
    UI智能体 - 管理显示屏输出

    在OLED显示屏上显示实时视频、检测结果和系统状态。
    """

    def __init__(self, config_path: str = "config/hardware_config.yaml", config: Dict[str, Any] = None):
        """
        初始化UI智能体

        Args:
            config_path: 配置文件路径
            config: 配置字典（优先使用）
        """
        if config is not None:
            self.config = config
        else:
            self.config = self._load_config(config_path)

        # 显示参数
        self.display_resolution = tuple(
            self.config.get("display", {}).get("resolution", [800, 480])
        )

        # 当前显示状态
        self.current_message = ""
        self.current_alert_level = "info"  # info, warning, error

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"[UIAgent] 配置文件不存在: {config_path}")
            print("[UIAgent] 使用默认配置")
            return {
                "display": {
                    "resolution": [800, 480]
                }
            }

    async def display(self, feedback: Dict[str, Any]) -> None:
        """
        显示反馈信息（核心接口）

        Args:
            feedback: 反馈数据字典
                {
                    "type": str,  # "error", "warning", "info", "success"
                    "content": str,  # 显示内容
                    "duration": float  # 显示时长（秒）
                }
        """
        display_type = feedback.get("type", "info")
        content = feedback.get("content", "")
        duration = feedback.get("duration", 3.0)

        print(f"[UIAgent] 显示: {display_type} - {content}")

        # 更新当前状态
        self.current_message = content
        self.current_alert_level = display_type

        # TODO: 实际的显示逻辑
        # 需要集成PyGame或Qt框架来驱动显示屏

        # 模拟显示
        await asyncio.sleep(min(duration, 5.0))

    async def display_frame(
        self,
        frame: np.ndarray,
        annotations: Dict[str, Any] = None
    ) -> None:
        """
        显示带标注的视频帧

        Args:
            frame: 视频帧
            annotations: 标注数据
                {
                    "pose": dict,  # 姿态数据
                    "site": dict,  # 部位检测
                    "angle": float,  # 注射角度
                    "alerts": list  # 告警列表
                }
        """
        if not _has_cv2:
            print("[UIAgent] cv2 不可用，无法显示视频帧")
            return

        # 调整大小以适应屏幕
        resized = cv2.resize(frame, self.display_resolution)

        # 绘制标注
        if annotations:
            resized = self._draw_annotations(resized, annotations)

        # 显示帧
        # TODO: 实际的显示逻辑
        # pygame_screen.blit(...)
        # 或使用Qt框架

    def _draw_annotations(
        self,
        frame: np.ndarray,
        annotations: Dict[str, Any]
    ) -> np.ndarray:
        """
        在帧上绘制标注

        Args:
            frame: 原始帧
            annotations: 标注数据

        Returns:
            绘制后的帧
        """
        if not _has_cv2 or cv2 is None:
            print("[UIAgent] cv2 不可用，无法绘制标注")
            return frame

        output = frame.copy()

        # 绘制角度信息
        angle = annotations.get("angle", 0)
        if angle > 0:
            angle_text = f"角度: {angle:.1f}°"
            color = (0, 255, 0) if 45 <= angle <= 90 else (0, 0, 255)

            cv2.putText(
                output, angle_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2
            )

        # 绘制部位信息
        site = annotations.get("site", {})
        if site:
            site_text = f"部位: {site.get('chinese_name', site.get('class_name', '未知'))}"
            color = (0, 255, 0) if site.get("is_recommended") else (0, 165, 255)

            cv2.putText(
                output, site_text, (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2
            )

        # 绘制告警
        alerts = annotations.get("alerts", [])
        if alerts:
            y_offset = 110
            for alert in alerts[:3]:  # 最多显示3个
                alert_text = alert.get("message", "")[:30]  # 限制长度

                if alert.get("severity") == "critical":
                    color = (0, 0, 255)
                elif alert.get("severity") == "warning":
                    color = (0, 165, 255)
                else:
                    color = (0, 255, 0)

                cv2.putText(
                    output, alert_text, (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                )

                y_offset += 35

        return output

    def show_progress(self, step: str, progress: float = 0.0) -> None:
        """
        显示进度信息

        Args:
            step: 当前步骤名称
            progress: 进度（0.0-1.0）
        """
        print(f"[UIAgent] 进度: {step} - {progress*100:.1f}%")

        # TODO: 实际的进度显示
        # 绘制进度条等

    def show_error(self, error_message: str) -> None:
        """
        显示错误信息

        Args:
            error_message: 错误文本
        """
        print(f"[UIAgent] 错误: {error_message}")

        self.current_alert_level = "error"
        self.current_message = error_message

        # TODO: 显示红色错误框

    def clear(self):
        """清除显示"""
        self.current_message = ""
        self.current_alert_level = "info"

        # TODO: 清空屏幕

    def get_current_state(self) -> Dict[str, Any]:
        """
        获取当前显示状态

        Returns:
            状态字典
        """
        return {
            "message": self.current_message,
            "alert_level": self.current_alert_level,
            "timestamp": time.time()
        }

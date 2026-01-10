"""
触觉智能体 - 负责震动反馈控制

功能：
1. 震动模式控制
2. 强度调节
3. 时序编排
4. 预设效果库
"""

import asyncio
import time
from typing import Dict, Any, List
from pathlib import Path
import yaml


class HapticAgent:
    """
    触觉智能体 - 控制震动马达提供触觉反馈

    通过DRV2605L驱动器控制LRA震动马达，提供多种触觉效果。
    """

    def __init__(self, config_path: str = "config/hardware_config.yaml", config: Dict[str, Any] = None):
        """
        初始化触觉智能体

        Args:
            config_path: 配置文件路径
            config: 配置字典（优先使用）
        """
        if config is not None:
            self.config = config
        else:
            self.config = self._load_config(config_path)

        # 震动驱动（延迟加载）
        self.driver = None

        # 预设震动模式
        self.patterns = self._initialize_patterns()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"[HapticAgent] 配置文件不存在: {config_path}")
            print("[HapticAgent] 使用默认配置")
            return {
                "haptic": {
                    "patterns": {
                        "gentle_reminder": {
                            "intensity": 30,
                            "duration_ms": 200
                        },
                        "strong_warning": {
                            "intensity": 100,
                            "duration_ms": 1000
                        },
                        "double_click": {
                            "sequence": [
                                {"intensity": 50, "duration_ms": 50},
                                {"intensity": 0, "duration_ms": 50},
                                {"intensity": 50, "duration_ms": 50}
                            ]
                        },
                        "gradual": {
                            "intensities": [20, 40, 60, 80, 100],
                            "duration_step_ms": 100
                        }
                    }
                }
            }

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        初始化震动模式

        Returns:
            模式字典
        """
        return self.config.get("haptic", {}).get("patterns", {
            "gentle_reminder": {
                "intensity": 30,
                "duration_ms": 200
            },
            "strong_warning": {
                "intensity": 100,
                "duration_ms": 1000
            },
            "double_click": {
                "sequence": [
                    {"intensity": 50, "duration_ms": 50},
                    {"intensity": 0, "duration_ms": 50},
                    {"intensity": 50, "duration_ms": 50}
                ]
            },
            "gradual": {
                "intensities": [20, 40, 60, 80, 100],
                "duration_step_ms": 100
            }
        })

    def _load_driver(self):
        """
        延迟加载震动驱动

        首次使用时才初始化硬件。
        """
        if self.driver is None:
            print("[HapticAgent] 初始化震动驱动...")
            try:
                # 尝试导入GPIO库（Raspberry Pi）
                import smbus2
                import RPi.GPIO as GPIO

                # 初始化DRV2605L
                bus = smbus2.SMBus(1)  # I2C总线1
                address = 0x5A  # DRV2605L I2C地址

                # 配置驱动器
                bus.write_byte_data(address, 0x01, 0x00)  # 模式选择
                bus.write_byte_data(address, 0x1D, 0xB0)  # 库设置
                bus.write_byte_data(address, 0x1E, 0x30)  # 高层库

                self.driver = {
                    "bus": bus,
                    "address": address
                }

                print("[HapticAgent] 震动驱动初始化成功")

            except Exception as e:
                print(f"[HapticAgent] 震动驱动初始化失败: {e}")
                print("[HapticAgent] 将使用模拟模式")
                self.driver = "simulation"

    async def vibrate(self, feedback: Dict[str, Any]) -> None:
        """
        执行震动反馈（核心接口）

        Args:
            feedback: 反馈数据字典
                {
                    "pattern": str,  # 震动模式名称
                    "duration": float,  # 持续时间（秒）
                    "intensity": float  # 强度（0.0-1.0）
                }
        """
        # 确保驱动已加载
        self._load_driver()

        # 提取参数
        pattern_name = feedback.get("pattern", "gentle_reminder")
        duration = feedback.get("duration", 0.5)
        intensity = feedback.get("intensity", 1.0)

        print(f"[HapticAgent] 震动反馈: 模式={pattern_name}, 持续={duration}秒")

        # 获取模式
        pattern = self.patterns.get(pattern_name)

        if not pattern:
            print(f"[HapticAgent] 未找到模式: {pattern_name}")
            return

        # 执行震动
        if "sequence" in pattern:
            # 序列模式
            await self._vibrate_sequence(pattern["sequence"])
        elif "intensities" in pattern:
            # 渐变模式
            await self._vibrate_gradual(pattern["intensities"], pattern["duration_step_ms"])
        else:
            # 简单模式
            await self._vibrate_simple(
                pattern["intensity"] * intensity,
                duration * 1000
            )

    async def _vibrate_simple(self, intensity: float, duration_ms: float) -> None:
        """
        简单震动

        Args:
            intensity: 强度（0-100）
            duration_ms: 持续时间（毫秒）
        """
        try:
            if self.driver == "simulation":
                # 模拟模式
                print(f"[HapticAgent] 模拟震动: 强度={intensity:.1f}, 持续={duration_ms}ms")
                await asyncio.sleep(duration_ms / 1000)
            else:
                # 实际硬件控制
                self._set_vibration(intensity)
                await asyncio.sleep(duration_ms / 1000)
                self._stop_vibration()

        except Exception as e:
            print(f"[HapticAgent] 震动执行错误: {e}")

    async def _vibrate_sequence(self, sequence: List[Dict[str, Any]]) -> None:
        """
        序列震动

        Args:
            sequence: 震动序列
                [
                    {"intensity": int, "duration_ms": int},
                    ...
                ]
        """
        for step in sequence:
            intensity = step["intensity"]
            duration = step["duration_ms"]

            await self._vibrate_simple(intensity, duration)

    async def _vibrate_gradual(
        self,
        intensities: List[float],
        duration_step_ms: float
    ) -> None:
        """
        渐变震动

        Args:
            intensities: 强度列表
            duration_step_ms: 每步持续时间（毫秒）
        """
        for intensity in intensities:
            await self._vibrate_simple(intensity, duration_step_ms)

    def _set_vibration(self, intensity: float) -> None:
        """
        设置震动强度

        Args:
            intensity: 强度（0-100）
        """
        try:
            if self.driver == "simulation":
                return

            bus = self.driver["bus"]
            address = self.driver["address"]

            # 限制强度范围
            intensity = max(0, min(127, int(intensity * 1.27)))

            # 设置强度
            bus.write_byte_data(address, 0x1B, intensity)

            # 触发震动
            bus.write_byte_data(address, 0x0C, 0x01)

        except Exception as e:
            print(f"[HapticAgent] 设置震动强度错误: {e}")

    def _stop_vibration(self) -> None:
        """停止震动"""
        try:
            if self.driver == "simulation":
                return

            bus = self.driver["bus"]
            address = self.driver["address"]

            # 停止震动
            bus.write_byte_data(address, 0x0C, 0x00)

        except Exception as e:
            print(f"[HapticAgent] 停止震动错误: {e}")

    def stop(self):
        """停止当前震动"""
        self._stop_vibration()

    def test_haptic(self):
        """测试震动反馈"""
        print("[HapticAgent] 测试震动反馈...")

        async def _test():
            patterns = ["gentle_reminder", "double_click", "gradual", "strong_warning"]

            for pattern in patterns:
                print(f"[HapticAgent] 测试模式: {pattern}")
                await self.vibrate({"pattern": pattern})
                await asyncio.sleep(0.5)

        asyncio.run(_test())

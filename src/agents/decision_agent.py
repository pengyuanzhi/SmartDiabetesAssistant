"""
决策智能体 - 负责规则推理、异常检测和日志记录

功能：
1. 根据监测数据判断操作规范性
2. 生成多级告警（critical/warning/info）
3. 记录异常事件
4. 更新用户行为模式
"""

import time
from typing import Dict, Any, List
from pathlib import Path
import yaml


class DecisionAgent:
    """
    决策智能体 - 基于规则引擎判断注射操作的规范性

    根据视觉智能体提供的数据，结合用户配置和医学规范，
    判断当前操作是否正确，并生成相应的告警。
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化决策智能体

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.user_profile = self._load_user_profile()

        # 监测规则
        self.rules = self._initialize_rules()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载模型配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_user_profile(self, profile_path: str = "config/user_profile.yaml") -> Dict[str, Any]:
        """加载用户配置"""
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[DecisionAgent] 无法加载用户配置: {e}")
            return {}

    def _initialize_rules(self) -> Dict[str, Any]:
        """
        初始化监测规则

        Returns:
            规则字典
        """
        # 从配置中提取规则
        angle_config = self.config.get("pose_estimation", {}).get("angle_calculation", {})
        injection_config = self.config.get("optical_flow", {}).get("parameters", {})

        return {
            "angle": {
                "min": angle_config.get("valid_angle_range", [45, 90])[0],
                "max": angle_config.get("valid_angle_range", [45, 90])[1],
                "tolerance": 5  # 容忍度
            },
            "speed": {
                "min_duration": injection_config.get("injection_duration_min_sec", 5),
                "max_duration": injection_config.get("injection_duration_max_sec", 30),
                "max_speed": 10.0
            },
            "site": {
                "recommended_only": True
            }
        }

    async def evaluate(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        评估当前操作状态（核心接口）

        Args:
            context: 上下文数据
                {
                    "injection_angle": float,
                    "injection_site": dict,
                    "injection_speed": float,
                    "current_step": str,
                    "user_profile": dict
                }

        Returns:
            告警列表
                [
                    {
                        "type": str,  # "angle_error", "site_warning", "speed_warning"
                        "severity": str,  # "critical", "warning", "info"
                        "message": str,
                        "timestamp": float,
                        "data": dict  # 额外数据
                    },
                    ...
                ]
        """
        alerts = []

        # 1. 检查注射角度
        angle_alert = self._check_angle(context)
        if angle_alert:
            alerts.append(angle_alert)

        # 2. 检查注射部位
        site_alert = self._check_site(context)
        if site_alert:
            alerts.append(site_alert)

        # 3. 检查注射速度（仅在推药阶段）
        if context.get("current_step") == "injection_deliver":
            speed_alert = self._check_speed(context)
            if speed_alert:
                alerts.append(speed_alert)

        # 4. 检查操作流程（可选）
        workflow_alert = self._check_workflow(context)
        if workflow_alert:
            alerts.append(workflow_alert)

        return alerts

    def _check_angle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查注射角度

        Args:
            context: 上下文数据

        Returns:
            告警字典（如果有问题）
        """
        angle = context.get("injection_angle", 0)
        rule = self.rules["angle"]

        # 允许一定容忍度
        min_angle = rule["min"] - rule["tolerance"]
        max_angle = rule["max"] + rule["tolerance"]

        if angle < min_angle:
            return {
                "type": "angle_error",
                "severity": "critical",
                "message": f"注射角度{angle:.1f}°过小，请调整至{rule['min']}-{rule['max']}度之间",
                "timestamp": time.time(),
                "data": {
                    "current_angle": angle,
                    "recommended_range": [rule["min"], rule["max"]]
                }
            }

        elif angle > max_angle:
            return {
                "type": "angle_error",
                "severity": "critical",
                "message": f"注射角度{angle:.1f}°过大，请调整至{rule['min']}-{rule['max']}度之间",
                "timestamp": time.time(),
                "data": {
                    "current_angle": angle,
                    "recommended_range": [rule["min"], rule["max"]]
                }
            }

        # 角度在边界（容忍度内），给出提示
        if angle < rule["min"] or angle > rule["max"]:
            return {
                "type": "angle_warning",
                "severity": "warning",
                "message": f"注射角度{angle:.1f}°接近边界，建议调整",
                "timestamp": time.time(),
                "data": {
                    "current_angle": angle,
                    "recommended_range": [rule["min"], rule["max"]]
                }
            }

        return None

    def _check_site(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查注射部位

        Args:
            context: 上下文数据

        Returns:
            告警字典（如果有问题）
        """
        site = context.get("injection_site", {})

        if not site:
            return {
                "type": "site_error",
                "severity": "warning",
                "message": "未检测到注射部位，请调整位置",
                "timestamp": time.time(),
                "data": {}
            }

        is_recommended = site.get("is_recommended", False)
        class_name = site.get("chinese_name", site.get("class_name", "未知部位"))

        if not is_recommended:
            return {
                "type": "site_warning",
                "severity": "warning",
                "message": f"当前部位{class_name}不是推荐注射区域，建议选择腹部、大腿或上臂",
                "timestamp": time.time(),
                "data": {
                    "current_site": site.get("class_name"),
                    "recommended_sites": ["abdomen", "thigh", "upper_arm"]
                }
            }

        # 部位正确，给予正面反馈（低优先级）
        return {
            "type": "site_correct",
            "severity": "info",
            "message": f"注射部位选择合适：{class_name}",
            "timestamp": time.time(),
            "data": {
                "current_site": site.get("class_name")
            }
        }

    def _check_speed(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查注射速度

        Args:
            context: 上下文数据

        Returns:
            告警字典（如果有问题）
        """
        speed = context.get("injection_speed", 0)
        rule = self.rules["speed"]

        # 速度过快
        if speed > rule["max_speed"]:
            return {
                "type": "speed_fast",
                "severity": "critical",
                "message": f"注射速度过快，请减慢推药速度",
                "timestamp": time.time(),
                "data": {
                    "current_speed": speed,
                    "max_recommended_speed": rule["max_speed"]
                }
            }

        # 速度过慢（基于时长判断）
        # duration = context.get("injection_duration", 0)
        # if duration > rule["max_duration"]:
        #     return {
        #         "type": "speed_slow",
        #         "severity": "info",
        #         "message": "注射速度较慢，请适当加快",
        #         "timestamp": time.time(),
        #         "data": {
        #             "current_duration": duration,
        #             "max_recommended_duration": rule["max_duration"]
        #         }
        #     }

        return None

    def _check_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查操作流程

        Args:
            context: 上下文数据

        Returns:
            告警字典（如果有问题）
        """
        current_step = context.get("current_step", "")

        # 检查是否跳过了关键步骤
        required_steps = [
            "preparing",
            "skin_pinch",
            "injection_start",
            "injection_deliver",
            "injection_end",
            "pressing"
        ]

        # TODO: 实现完整的流程检查逻辑

        return None

    def update_rules(self, new_rules: Dict[str, Any]):
        """
        动态更新监测规则

        Args:
            new_rules: 新规则字典
        """
        self.rules.update(new_rules)
        print(f"[DecisionAgent] 规则已更新")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据字典
        """
        return {
            "rules": self.rules,
            "user_profile": self.user_profile
        }

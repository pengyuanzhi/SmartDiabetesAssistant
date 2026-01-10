"""
多模态反馈协调器 - 统一管理语音、震动、视觉反馈

功能：
1. 反馈计划生成
2. 多模态输出同步
3. 优先级队列管理
4. 自适应反馈策略
"""

import asyncio
import time
from typing import Dict, Any, List
from collections import deque

# 直接导入各个智能体模块，避免通过 __init__.py 导入其他依赖
import sys
import importlib.util
from pathlib import Path

def _load_agent_module(module_name: str):
    """
    动态加载智能体模块，避免通过 __init__.py 导入

    Args:
        module_name: 模块名称（如 'src.agents.tts_agent'）

    Returns:
        模块对象
    """
    project_root = Path(__file__).parent.parent.parent
    module_path = project_root / f"{module_name.replace('.', '/')}.py"

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 加载智能体模块
tts_agent_module = _load_agent_module('src.agents.tts_agent')
haptic_agent_module = _load_agent_module('src.agents.haptic_agent')
ui_agent_module = _load_agent_module('src.agents.ui_agent')

TTSAgent = tts_agent_module.TTSAgent
HapticAgent = haptic_agent_module.HapticAgent
UIAgent = ui_agent_module.UIAgent


class FeedbackPriority:
    """反馈优先级"""
    CRITICAL = 0
    WARNING = 1
    INFO = 2


class FeedbackCoordinator:
    """
    多模态反馈协调器

    根据告警严重程度协调语音、震动、视觉三种反馈方式，
    确保用户能够及时、清晰地收到提示。
    """

    def __init__(self, config_path: str = "config", config: Dict[str, Any] = None):
        """
        初始化反馈协调器

        Args:
            config_path: 配置文件路径
            config: 配置字典（优先使用）
        """
        # 如果提供了配置字典，使用它；否则从文件加载
        if config is not None:
            self.config = config
        else:
            self.config = {"config_path": config_path}

        # 初始化子智能体
        try:
            if config is not None:
                # 使用模拟模式
                self.tts_agent = TTSAgent()
                self.haptic_agent = HapticAgent(config=config)
                self.ui_agent = UIAgent(config=config)
            else:
                self.tts_agent = TTSAgent(f"{config_path}/model_config.yaml")
                self.haptic_agent = HapticAgent(f"{config_path}/hardware_config.yaml")
                self.ui_agent = UIAgent(f"{config_path}/hardware_config.yaml")
        except Exception as e:
            print(f"[FeedbackCoordinator] 初始化子智能体时出错: {e}")
            print("[FeedbackCoordinator] 使用默认配置重新初始化...")
            self.tts_agent = TTSAgent()
            self.haptic_agent = HapticAgent(config={})
            self.ui_agent = UIAgent(config={})

        # 反馈队列
        self.feedback_queue = deque()

        # 反馈历史（用于去重）
        self.feedback_history = []
        self.history_window_sec = 30  # 历史窗口

        # 自适应策略
        self.user_sensitivity = "medium"  # low, medium, high

    async def send_feedback(self, alerts: List[Dict[str, Any]]) -> None:
        """
        发送反馈（核心接口）

        Args:
            alerts: 告警列表
                [
                    {
                        "type": str,
                        "severity": str,  # "critical", "warning", "info"
                        "message": str,
                        "timestamp": float,
                        "data": dict
                    },
                    ...
                ]
        """
        if not alerts:
            return

        # 生成反馈计划
        feedback_plan = await self._generate_feedback_plan(alerts)

        # 执行反馈计划
        await self._execute_feedback_plan(feedback_plan)

        # 记录历史
        self._record_feedback(alerts)

    async def generate_feedback(
        self,
        level,
        alert_type,
        message: str
    ) -> Dict[str, Any]:
        """
        生成单个反馈（兼容测试脚本接口）

        Args:
            level: 告警级别 (AlertLevel枚举或字符串)
            alert_type: 告警类型 (AlertType枚举或字符串)
            message: 反馈消息

        Returns:
            反馈结果字典
        """
        # 将枚举转换为字符串
        severity = level.value if hasattr(level, 'value') else str(level)
        alert_type_str = alert_type.value if hasattr(alert_type, 'value') else str(alert_type)

        # 构造告警对象
        alert = {
            "type": alert_type_str,
            "severity": severity,
            "message": message,
            "timestamp": time.time(),
            "data": {}
        }

        # 检查是否被去重
        if self._should_suppress(alert):
            return {
                "modalities": [],
                "message": message,
                "deduplicated": True
            }

        # 生成反馈计划
        feedback_plan = await self._generate_feedback_plan([alert])

        # 返回反馈信息
        result = {
            "modalities": [],
            "message": message,
            "deduplicated": False
        }

        if feedback_plan:
            result["modalities"] = feedback_plan[0].get("modalities", [])

        return result

    async def execute_feedback(self, feedback_result: Dict[str, Any]) -> None:
        """
        执行反馈（兼容测试脚本接口）

        Args:
            feedback_result: generate_feedback返回的结果
        """
        message = feedback_result.get("message", "")
        modalities = feedback_result.get("modalities", [])

        if not modalities:
            return

        # 构造反馈计划
        feedback_plan = [{
            "modalities": modalities,
            "synchronization": "simultaneous" if len(modalities) > 1 else "none",
        }]

        # 根据模态添加具体反馈内容
        if "audio" in modalities:
            feedback_plan[0]["audio"] = {
                "message": message,
                "urgency": "medium"
            }

        if "vibration" in modalities:
            feedback_plan[0]["vibration"] = {
                "pattern": "gentle_reminder",
                "duration": 0.5
            }

        if "visual" in modalities:
            feedback_plan[0]["visual"] = {
                "type": "info",
                "content": message,
                "duration": 2.0
            }

        # 执行反馈计划
        await self._execute_feedback_plan(feedback_plan)

    async def _generate_feedback_plan(
        self,
        alerts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        生成反馈计划

        Args:
            alerts: 告警列表

        Returns:
            反馈计划列表
        """
        # 按严重程度排序
        sorted_alerts = sorted(
            alerts,
            key=lambda x: self._get_severity_priority(x["severity"]),
            reverse=True
        )

        feedback_plan = []

        for alert in sorted_alerts:
            # 检查是否需要抑制（重复告警）
            if self._should_suppress(alert):
                continue

            severity = alert["severity"]

            if severity == "critical":
                # 关键错误：语音 + 强烈震动 + 视觉警告（同步）
                feedback_plan.append({
                    "modalities": ["audio", "vibration", "visual"],
                    "synchronization": "simultaneous",
                    "audio": {
                        "message": alert["message"],
                        "urgency": "high"
                    },
                    "vibration": {
                        "pattern": "strong_warning",
                        "duration": 1.0
                    },
                    "visual": {
                        "type": "error",
                        "content": alert["message"],
                        "duration": 3.0
                    }
                })

            elif severity == "warning":
                # 警告：语音 + 双击震动（同步）
                feedback_plan.append({
                    "modalities": ["audio", "vibration"],
                    "synchronization": "simultaneous",
                    "audio": {
                        "message": alert["message"],
                        "urgency": "medium"
                    },
                    "vibration": {
                        "pattern": "double_click",
                        "duration": 0.5
                    }
                })

            elif severity == "info":
                # 信息：仅语音
                feedback_plan.append({
                    "modalities": ["audio"],
                    "synchronization": "none",
                    "audio": {
                        "message": alert["message"],
                        "urgency": "low"
                    }
                })

        return feedback_plan

    async def _execute_feedback_plan(
        self,
        feedback_plan: List[Dict[str, Any]]
    ) -> None:
        """
        执行反馈计划

        Args:
            feedback_plan: 反馈计划列表
        """
        for item in feedback_plan:
            modalities = item["modalities"]
            sync = item["synchronization"]

            tasks = []

            # 准备任务
            if "audio" in modalities:
                tasks.append(self.tts_agent.speak(item["audio"]))

            if "vibration" in modalities:
                tasks.append(self.haptic_agent.vibrate(item["vibration"]))

            if "visual" in modalities:
                tasks.append(self.ui_agent.display(item["visual"]))

            # 执行任务
            if sync == "simultaneous" and len(tasks) > 1:
                # 并行执行
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                # 串行执行
                for task in tasks:
                    try:
                        await task
                    except Exception as e:
                        print(f"[FeedbackCoordinator] 反馈执行错误: {e}")

    def _get_severity_priority(self, severity: str) -> int:
        """
        获取严重程度优先级

        Args:
            severity: 严重程度

        Returns:
            优先级（数字越小优先级越高）
        """
        priority_map = {
            "critical": FeedbackPriority.CRITICAL,
            "warning": FeedbackPriority.WARNING,
            "info": FeedbackPriority.INFO
        }

        return priority_map.get(severity, FeedbackPriority.INFO)

    def _should_suppress(self, alert: Dict[str, Any]) -> bool:
        """
        判断是否应该抑制告警（重复告警）

        Args:
            alert: 告警对象

        Returns:
            是否抑制
        """
        # 清理过期历史
        current_time = time.time()
        cutoff_time = current_time - self.history_window_sec

        self.feedback_history = [
            a for a in self.feedback_history
            if a["timestamp"] > cutoff_time
        ]

        # 检查最近是否有相同类型的告警
        alert_type = alert.get("type")
        recent_alerts = [
            a for a in self.feedback_history
            if a["type"] == alert_type and a["timestamp"] > cutoff_time
        ]

        # 如果30秒内已有相同告警，抑制
        if len(recent_alerts) > 0:
            return True

        return False

    def _record_feedback(self, alerts: List[Dict[str, Any]]) -> None:
        """
        记录反馈历史

        Args:
            alerts: 告警列表
        """
        current_time = time.time()

        for alert in alerts:
            self.feedback_history.append({
                "type": alert.get("type"),
                "severity": alert.get("severity"),
                "message": alert.get("message"),
                "timestamp": current_time
            })

    async def send_immediate_feedback(
        self,
        message: str,
        urgency: str = "medium"
    ) -> None:
        """
        发送即时反馈（不经过告警系统）

        Args:
            message: 消息文本
            urgency: 紧急程度
        """
        await self.tts_agent.speak({
            "message": message,
            "urgency": urgency
        })

    def set_sensitivity(self, sensitivity: str):
        """
        设置用户敏感度

        Args:
            sensitivity: 敏感度级别（low, medium, high）
        """
        self.user_sensitivity = sensitivity
        print(f"[FeedbackCoordinator] 用户敏感度已设置为: {sensitivity}")

    def adjust_feedback_by_context(
        self,
        feedback: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        根据上下文调整反馈

        Args:
            feedback: 原始反馈
            context: 上下文信息

        Returns:
            调整后的反馈
        """
        # 根据环境噪音调整音量
        if context.get("is_noisy_environment", False):
            if "audio" in feedback:
                feedback["audio"]["volume"] = feedback["audio"].get("volume", 1.0) * 1.5
                feedback["audio"]["add_vibration"] = True

        # 根据时间调整（夜间降低音量）
        current_hour = time.localtime().tm_hour
        if current_hour >= 22 or current_hour <= 6:
            if "audio" in feedback:
                feedback["audio"]["volume"] = feedback["audio"].get("volume", 1.0) * 0.7

        # 根据用户敏感度调整
        if self.user_sensitivity == "low":
            # 低敏感度：仅语音
            feedback["modalities"] = [m for m in feedback["modalities"] if m == "audio"]
        elif self.user_sensitivity == "high":
            # 高敏感度：增加震动
            if "vibration" not in feedback["modalities"] and "audio" in feedback["modalities"]:
                feedback["modalities"].append("vibration")
                feedback["vibration"] = {
                    "pattern": "gentle_reminder",
                    "duration": 0.3
                }

        return feedback

    def clear_history(self):
        """清空反馈历史"""
        self.feedback_history.clear()
        print("[FeedbackCoordinator] 反馈历史已清空")

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据
        """
        # 按严重程度统计
        severity_counts = {}
        for alert in self.feedback_history:
            severity = alert["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_feedbacks": len(self.feedback_history),
            "severity_breakdown": severity_counts,
            "user_sensitivity": self.user_sensitivity
        }

    async def test_all_modalities(self):
        """测试所有反馈模式"""
        print("[FeedbackCoordinator] 测试所有反馈模式...")

        # 测试语音
        await self.send_immediate_feedback("语音系统正常", "low")
        await asyncio.sleep(1)

        # 测试震动
        await self.haptic_agent.vibrate({
            "pattern": "double_click",
            "duration": 0.5
        })
        await asyncio.sleep(1)

        # 测试视觉
        await self.ui_agent.display({
            "type": "info",
            "content": "视觉系统正常",
            "duration": 2.0
        })

        print("[FeedbackCoordinator] 测试完成")

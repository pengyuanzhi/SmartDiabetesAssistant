"""
主智能体 - 智能糖尿病胰岛素注射监测系统

基于LangGraph实现的多智能体协调系统，负责：
1. 会话管理
2. 任务调度
3. 状态协调
4. 智能体编排
"""

import asyncio
import time
from typing import TypedDict, Annotated, Sequence, Dict, Any, List
import operator
from pathlib import Path

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .vision_agent import VisionAgent
from .decision_agent import DecisionAgent
from .tts_agent import TTSAgent
from .haptic_agent import HapticAgent
from .ui_agent import UIAgent


class AgentState(TypedDict):
    """全局状态管理"""
    # 消息历史
    messages: Annotated[Sequence[str], operator.add]

    # 视觉数据
    video_frame: Dict[str, Any]
    pose_data: Dict[str, Any]
    injection_site: Dict[str, Any]

    # 监测指标
    injection_angle: float
    injection_speed: float
    injection_duration: float

    # 状态跟踪
    current_step: str
    step_start_time: float

    # 告警和反馈
    alerts: List[Dict[str, Any]]
    feedback_history: List[Dict[str, Any]]

    # 用户上下文
    user_profile: Dict[str, Any]
    session_id: str


class MainAgent:
    """
    主智能体 - 协调所有子智能体

    实现基于状态图的智能体工作流，管理注射监测的完整流程。
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化主智能体

        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.graph = self._build_graph()

        # 初始化子智能体
        self.vision_agent = VisionAgent(config_path)
        self.decision_agent = DecisionAgent(config_path)
        self.tts_agent = TTSAgent(config_path)
        self.haptic_agent = HapticAgent(config_path)
        self.ui_agent = UIAgent(config_path)

        # 配置状态持久化
        self.memory = SqliteSaver.from_conn_string("data/injection_monitoring.db")

    def _build_graph(self) -> StateGraph:
        """
        构建LangGraph状态图

        工作流:
            视觉处理 → 决策判断 → 反馈生成 → 多模态输出 → END
        """
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("vision_processing", self._vision_processing_node)
        workflow.add_node("decision_making", self._decision_making_node)
        workflow.add_node("feedback_generation", self._feedback_generation_node)
        workflow.add_node("multimodal_output", self._multimodal_output_node)

        # 定义边（工作流）
        workflow.set_entry_point("vision_processing")
        workflow.add_edge("vision_processing", "decision_making")
        workflow.add_edge("decision_making", "feedback_generation")
        workflow.add_edge("feedback_generation", "multimodal_output")
        workflow.add_edge("multimodal_output", END)

        return workflow.compile()

    async def _vision_processing_node(self, state: AgentState) -> AgentState:
        """
        视觉处理节点 - 调用视觉智能体处理图像

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        print(f"[MainAgent] 开始视觉处理...")

        # 提取视频帧
        frame = state.get("video_frame", {})

        # 调用视觉智能体
        vision_results = await self.vision_agent.process_frame(frame)

        # 更新状态
        state["pose_data"] = vision_results.get("pose", {})
        state["injection_site"] = vision_results.get("site", {})

        # 计算注射角度
        if state["pose_data"]:
            state["injection_angle"] = self._calculate_injection_angle(
                state["pose_data"]
            )
        else:
            state["injection_angle"] = 0.0

        # 计算注射速度
        if vision_results.get("flow"):
            state["injection_speed"] = self._calculate_injection_speed(
                vision_results["flow"]
            )
        else:
            state["injection_speed"] = 0.0

        # 更新消息历史
        state["messages"].append(f"视觉处理完成: 角度={state['injection_angle']:.1f}°")

        print(f"[MainAgent] 视觉处理完成: 角度={state['injection_angle']:.1f}°")

        return state

    async def _decision_making_node(self, state: AgentState) -> AgentState:
        """
        决策判断节点 - 调用决策智能体判断操作规范性

        Args:
            state: 当前状态

        Returns:
            更新后的状态（包含告警列表）
        """
        print(f"[MainAgent] 开始决策判断...")

        # 准备决策上下文
        context = {
            "injection_angle": state["injection_angle"],
            "injection_site": state["injection_site"],
            "injection_speed": state["injection_speed"],
            "current_step": state["current_step"],
            "user_profile": state.get("user_profile", {})
        }

        # 调用决策智能体
        alerts = await self.decision_agent.evaluate(context)

        # 更新状态
        state["alerts"] = alerts

        # 更新消息历史
        if alerts:
            state["messages"].append(f"检测到 {len(alerts)} 个告警")
        else:
            state["messages"].append("操作正常，无告警")

        print(f"[MainAgent] 决策判断完成: {len(alerts)} 个告警")

        return state

    async def _feedback_generation_node(self, state: AgentState) -> AgentState:
        """
        反馈生成节点 - 根据告警生成多模态反馈计划

        Args:
            state: 当前状态

        Returns:
            更新后的状态（包含反馈计划）
        """
        print(f"[MainAgent] 生成反馈策略...")

        feedback_plan = []

        # 根据告警严重程度生成反馈
        for alert in state["alerts"]:
            severity = alert.get("severity", "info")

            if severity == "critical":
                # 关键错误：语音 + 强烈震动 + 视觉警告
                feedback_plan.append({
                    "modality": "audio",
                    "message": alert["message"],
                    "urgency": "high",
                    "delay": 0
                })
                feedback_plan.append({
                    "modality": "vibration",
                    "pattern": "strong_warning",
                    "duration": 1.0,
                    "delay": 0
                })
                feedback_plan.append({
                    "modality": "visual",
                    "type": "error",
                    "content": alert["message"],
                    "delay": 0
                })

            elif severity == "warning":
                # 警告：语音 + 双击震动
                feedback_plan.append({
                    "modality": "audio",
                    "message": alert["message"],
                    "urgency": "medium",
                    "delay": 0
                })
                feedback_plan.append({
                    "modality": "vibration",
                    "pattern": "double_click",
                    "duration": 0.5,
                    "delay": 0
                })

            elif severity == "info":
                # 信息：仅语音
                feedback_plan.append({
                    "modality": "audio",
                    "message": alert["message"],
                    "urgency": "low",
                    "delay": 0
                })

        # 如果没有告警，给予正面反馈
        if not state["alerts"] and state["current_step"] in ["injection_deliver", "completed"]:
            feedback_plan.append({
                "modality": "audio",
                "message": "操作正确，请继续保持",
                "urgency": "low",
                "delay": 0
            })

        # 更新状态
        state["feedback_plan"] = feedback_plan

        print(f"[MainAgent] 反馈策略生成完成: {len(feedback_plan)} 个反馈")

        return state

    async def _multimodal_output_node(self, state: AgentState) -> AgentState:
        """
        多模态输出节点 - 协调执行各种反馈

        Args:
            state: 当前状态

        Returns:
            更新后的状态
        """
        print(f"[MainAgent] 执行多模态输出...")

        feedback_plan = state.get("feedback_plan", [])

        # 按延迟分组
        feedback_groups = {}
        for feedback in feedback_plan:
            delay = feedback.get("delay", 0)
            if delay not in feedback_groups:
                feedback_groups[delay] = []
            feedback_groups[delay].append(feedback)

        # 执行反馈
        for delay, group in sorted(feedback_groups.items()):
            if delay > 0:
                await asyncio.sleep(delay)

            # 并发执行同一延迟的反馈
            tasks = []
            for feedback in group:
                modality = feedback["modality"]

                if modality == "audio":
                    tasks.append(self.tts_agent.speak(feedback))
                elif modality == "vibration":
                    tasks.append(self.haptic_agent.vibrate(feedback))
                elif modality == "visual":
                    tasks.append(self.ui_agent.display(feedback))

            # 并行执行
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

        # 记录反馈历史
        state["feedback_history"].append({
            "timestamp": time.time(),
            "feedbacks": feedback_plan
        })

        print(f"[MainAgent] 多模态输出完成")

        return state

    def _calculate_injection_angle(self, pose_data: Dict[str, Any]) -> float:
        """
        计算注射角度

        基于姿态估计的关键点（肩-肘-腕）计算注射角度

        Args:
            pose_data: 姿态数据

        Returns:
            注射角度（度）
        """
        try:
            keypoints = pose_data.get("keypoints", {})

            # 提取关键点
            shoulder = keypoints.get("shoulder")
            elbow = keypoints.get("elbow")
            wrist = keypoints.get("wrist")

            if not all([shoulder, elbow, wrist]):
                return 0.0

            # 计算三点角度
            angle = self._calculate_angle_3points(shoulder, elbow, wrist)

            # 转换为与垂直方向的夹角
            vertical_angle = abs(90 - angle)

            return vertical_angle

        except Exception as e:
            print(f"[MainAgent] 计算角度错误: {e}")
            return 0.0

    def _calculate_angle_3points(
        self,
        p1: List[float],
        p2: List[float],
        p3: List[float]
    ) -> float:
        """
        计算三点形成的角度

        Args:
            p1: 点1坐标 [x, y]
            p2: 点2坐标（顶点）
            p3: 点3坐标 [x, y]

        Returns:
            角度（度）
        """
        import math

        # 计算向量
        v1 = [p1[0] - p2[0], p1[1] - p2[1]]
        v2 = [p3[0] - p2[0], p3[1] - p2[1]]

        # 计算点积
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]

        # 计算模长
        norm1 = math.sqrt(v1[0]**2 + v1[1]**2)
        norm2 = math.sqrt(v2[0]**2 + v2[1]**2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # 计算角度（弧度）
        cos_angle = dot_product / (norm1 * norm2)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # 限制在[-1, 1]
        angle_rad = math.acos(cos_angle)

        # 转换为度
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    def _calculate_injection_speed(self, flow_data: Dict[str, Any]) -> float:
        """
        计算注射速度

        基于光流数据计算针头运动速度

        Args:
            flow_data: 光流数据

        Returns:
            速度（像素/帧）
        """
        try:
            # 提取运动向量
            flow_vectors = flow_data.get("vectors", [])

            if not flow_vectors:
                return 0.0

            # 计算平均速度
            speeds = []
            for vector in flow_vectors:
                dx = vector.get("dx", 0)
                dy = vector.get("dy", 0)
                speed = (dx**2 + dy**2) ** 0.5
                speeds.append(speed)

            avg_speed = sum(speeds) / len(speeds) if speeds else 0.0

            return avg_speed

        except Exception as e:
            print(f"[MainAgent] 计算速度错误: {e}")
            return 0.0

    async def start_monitoring(
        self,
        session_id: str,
        user_profile: Dict[str, Any]
    ) -> None:
        """
        启动监测会话

        Args:
            session_id: 会话ID
            user_profile: 用户配置
        """
        print(f"[MainAgent] 启动监测会话: {session_id}")

        # 初始化状态
        initial_state: AgentState = {
            "messages": [],
            "video_frame": {},
            "pose_data": {},
            "injection_site": {},
            "injection_angle": 0.0,
            "injection_speed": 0.0,
            "injection_duration": 0.0,
            "current_step": "idle",
            "step_start_time": time.time(),
            "alerts": [],
            "feedback_history": [],
            "user_profile": user_profile,
            "session_id": session_id
        }

        # 配置检查点
        config = {"configurable": {"thread_id": session_id}}

        # 启动初始消息
        await self.tts_agent.speak({
            "message": "开始监测，请按照标准流程操作",
            "urgency": "low"
        })

        print(f"[MainAgent] 监测会话已启动")

        # 返回初始状态（供外部使用）
        return initial_state

    async def process_frame(
        self,
        frame: Dict[str, Any],
        state: AgentState
    ) -> AgentState:
        """
        处理单帧视频（核心接口）

        Args:
            frame: 视频帧数据
            state: 当前状态

        Returns:
            更新后的状态
        """
        # 更新帧数据
        state["video_frame"] = frame

        # 运行智能体图
        result = await self.graph.ainvoke(state, config={"recursion_limit": 100})

        return result

    def get_session_summary(self, state: AgentState) -> Dict[str, Any]:
        """
        获取会话摘要

        Args:
            state: 最终状态

        Returns:
            会话摘要
        """
        return {
            "session_id": state["session_id"],
            "duration": time.time() - state.get("step_start_time", time.time()),
            "total_alerts": len(state["alerts"]),
            "feedback_count": len(state["feedback_history"]),
            "messages": state["messages"]
        }

"""
智能体模块
"""

from .vision_agent import VisionAgent
from .decision_agent import DecisionAgent
from .tts_agent import TTSAgent
from .haptic_agent import HapticAgent
from .ui_agent import UIAgent

# main_agent 需要 langgraph，可选导入
try:
    from .main_agent import MainAgent, AgentState
    _has_langgraph = True
except ImportError:
    _has_langgraph = False
    MainAgent = None
    AgentState = None

__all__ = [
    "VisionAgent",
    "DecisionAgent",
    "TTSAgent",
    "HapticAgent",
    "UIAgent"
]

# 如果 langgraph 可用，导出 main_agent 相关类
if _has_langgraph:
    __all__.extend(["MainAgent", "AgentState"])

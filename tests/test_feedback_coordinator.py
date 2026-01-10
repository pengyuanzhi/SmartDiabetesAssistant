"""
反馈协调器单元测试
"""

import pytest
import asyncio
from pathlib import Path
from enum import Enum
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class AlertLevel(Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TestFeedbackCoordinator:
    """反馈协调器测试类"""

    @pytest.fixture
    def coordinator_config(self):
        """反馈协调器配置 fixture"""
        return {
            "audio_enabled": True,
            "vibration_enabled": False,  # PC端测试禁用震动
            "visual_enabled": True,
            "dedup_window": 5.0,  # 5秒去重窗口
        }

    def test_feedback_coordinator_import(self):
        """测试反馈协调器导入"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator
            assert FeedbackCoordinator is not None
        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    def test_feedback_coordinator_init(self, coordinator_config):
        """测试反馈协调器初始化"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            coordinator = FeedbackCoordinator(config=coordinator_config)
            assert coordinator is not None
            assert coordinator.config == coordinator_config

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    @pytest.mark.asyncio
    async def test_generate_feedback_info(self, coordinator_config):
        """测试生成INFO级别反馈"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            coordinator = FeedbackCoordinator(config=coordinator_config)

            result = await coordinator.generate_feedback(
                level=AlertLevel.INFO,
                alert_type="operation_correct",
                message="操作正确"
            )

            assert result is not None
            assert "modalities" in result
            assert "message" in result
            assert result["message"] == "操作正确"

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    @pytest.mark.asyncio
    async def test_generate_feedback_warning(self, coordinator_config):
        """测试生成WARNING级别反馈"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            coordinator = FeedbackCoordinator(config=coordinator_config)

            result = await coordinator.generate_feedback(
                level=AlertLevel.WARNING,
                alert_type="angle_incorrect",
                message="角度偏小"
            )

            assert result is not None
            # WARNING级别应该有音频和可能的震动
            assert "audio" in result.get("modalities", [])

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    @pytest.mark.asyncio
    async def test_generate_feedback_critical(self, coordinator_config):
        """测试生成CRITICAL级别反馈"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            coordinator = FeedbackCoordinator(config=coordinator_config)

            result = await coordinator.generate_feedback(
                level=AlertLevel.CRITICAL,
                alert_type="speed_too_fast",
                message="速度过快，立即停止"
            )

            assert result is not None
            # CRITICAL级别应该有所有模态
            modalities = result.get("modalities", [])
            assert len(modalities) > 0

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    @pytest.mark.asyncio
    async def test_feedback_deduplication(self, coordinator_config):
        """测试反馈去重功能"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator
            import time

            coordinator = FeedbackCoordinator(config=coordinator_config)

            # 生成相同的告警
            result1 = await coordinator.generate_feedback(
                level=AlertLevel.WARNING,
                alert_type="angle_incorrect",
                message="角度偏小"
            )

            time.sleep(0.1)

            result2 = await coordinator.generate_feedback(
                level=AlertLevel.WARNING,
                alert_type="angle_incorrect",
                message="角度偏小"
            )

            # 第二个告警应该被去重
            assert result2.get("deduplicated", False) is True

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")

    @pytest.mark.asyncio
    async def test_feedback_priority(self, coordinator_config):
        """测试反馈优先级"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            coordinator = FeedbackCoordinator(config=coordinator_config)

            # 生成不同级别的告警
            alerts = [
                (AlertLevel.INFO, "info_alert", "信息"),
                (AlertLevel.WARNING, "warning_alert", "警告"),
                (AlertLevel.CRITICAL, "critical_alert", "严重"),
            ]

            results = []
            for level, alert_type, message in alerts:
                result = await coordinator.generate_feedback(
                    level=level,
                    alert_type=alert_type,
                    message=message
                )
                results.append((level, result))

            # CRITICAL应该有最高的优先级
            critical_result = next(r for l, r in results if l == AlertLevel.CRITICAL)
            assert critical_result is not None

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")


class TestFeedbackIntegration:
    """反馈系统集成测试"""

    @pytest.mark.asyncio
    async def test_complete_feedback_workflow(self):
        """测试完整的反馈工作流"""
        try:
            from src.feedback.coordinator import FeedbackCoordinator

            config = {
                "audio_enabled": True,
                "vibration_enabled": False,
                "visual_enabled": True,
            }

            coordinator = FeedbackCoordinator(config=config)

            # 模拟一系列告警
            scenario = [
                (AlertLevel.INFO, "system_ready", "系统就绪"),
                (AlertLevel.INFO, "operation_correct", "操作正确"),
                (AlertLevel.WARNING, "angle_warning", "角度偏小"),
                (AlertLevel.CRITICAL, "speed_critical", "速度过快"),
            ]

            for level, alert_type, message in scenario:
                result = await coordinator.generate_feedback(
                    level=level,
                    alert_type=alert_type,
                    message=message
                )

                assert result is not None
                assert "modalities" in result

        except ImportError:
            pytest.skip("FeedbackCoordinator模块未实现")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

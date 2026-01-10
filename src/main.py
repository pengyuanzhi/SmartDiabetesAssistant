"""
智能糖尿病胰岛素注射监测系统 - 主程序入口

Usage:
    python src/main.py [--config CONFIG_PATH] [--debug]
"""

import asyncio
import sys
import argparse
from pathlib import Path

from loguru import logger

from agents import MainAgent
from processing import VideoProcessingPipeline
from feedback import FeedbackCoordinator
from storage import DatabaseManager


class InjectionMonitoringSystem:
    """
    注射监测系统主类

    整合所有模块，提供完整的监测功能。
    """

    def __init__(self, config_path: str = "config", debug: bool = False):
        """
        初始化系统

        Args:
            config_path: 配置文件目录
            debug: 调试模式
        """
        self.config_path = config_path
        self.debug = debug

        # 初始化组件
        self.main_agent = None
        self.video_pipeline = None
        self.feedback_coordinator = None
        self.database = None

        # 运行状态
        self.running = False

        logger.info(f"[系统] 初始化智能糖尿病胰岛素注射监测系统")
        logger.info(f"[系统] 配置路径: {config_path}")
        logger.info(f"[系统] 调试模式: {debug}")

    async def initialize(self):
        """初始化所有组件"""
        logger.info("[系统] 正在初始化组件...")

        try:
            # 初始化主智能体
            self.main_agent = MainAgent(
                config_path=f"{self.config_path}/model_config.yaml"
            )
            logger.info("[系统] ✓ 主智能体已初始化")

            # 初始化反馈协调器
            self.feedback_coordinator = FeedbackCoordinator(
                config_path=self.config_path
            )
            logger.info("[系统] ✓ 反馈协调器已初始化")

            # 初始化数据库
            self.database = DatabaseManager(
                db_path="data/injection_monitoring.db"
            )
            logger.info("[系统] ✓ 数据库已初始化")

            logger.info("[系统] 所有组件初始化完成")

        except Exception as e:
            logger.error(f"[系统] 组件初始化失败: {e}")
            raise

    async def start(self, camera_id: int = 0):
        """
        启动监测系统

        Args:
            camera_id: 摄像头ID
        """
        logger.info("[系统] 启动监测系统...")

        try:
            # 启动监测会话
            session_id = f"session_{int(asyncio.get_event_loop().time())}"
            user_profile = {}  # TODO: 从数据库加载用户配置

            initial_state = await self.main_agent.start_monitoring(
                session_id=session_id,
                user_profile=user_profile
            )

            logger.info(f"[系统] 监测会话已启动: {session_id}")

            # 初始化视频处理管道
            self.video_pipeline = VideoProcessingPipeline(
                camera_id=camera_id,
                queue_size=30,
                target_fps=30
            )

            # 定义帧处理回调
            async def process_frame(frame_data):
                """处理每一帧"""
                # 调用主智能体处理
                result = await self.main_agent.process_frame(frame_data, initial_state)

                # 如果有告警，发送反馈
                if result.get("alerts"):
                    await self.feedback_coordinator.send_feedback(result["alerts"])

            # 启动视频处理
            await self.video_pipeline.start(process_frame)

            self.running = True
            logger.info("[系统] ✓ 监测系统已启动")

            # 保持运行
            await self._run_loop()

        except Exception as e:
            logger.error(f"[系统] 启动失败: {e}")
            raise

    async def _run_loop(self):
        """主运行循环"""
        logger.info("[系统] 系统运行中，按Ctrl+C停止...")

        try:
            while self.running:
                await asyncio.sleep(1)

                # 定期打印统计信息
                if self.debug and self.video_pipeline:
                    stats = self.video_pipeline.get_stats()
                    logger.debug(f"[系统] 帧率: {stats['avg_fps']:.1f} FPS, "
                              f"延迟: {stats['avg_latency_ms']:.1f} ms")

        except asyncio.CancelledError:
            logger.info("[系统] 收到停止信号")

    async def stop(self):
        """停止监测系统"""
        logger.info("[系统] 正在停止监测系统...")

        self.running = False

        # 停止视频处理
        if self.video_pipeline:
            await self.video_pipeline.stop()

        # 获取会话摘要
        if self.main_agent:
            # TODO: 保存会话数据到数据库
            pass

        logger.info("[系统] ✓ 监测系统已停止")

    async def test_feedback(self):
        """测试反馈系统"""
        logger.info("[系统] 测试反馈系统...")

        # 测试所有模态
        await self.feedback_coordinator.test_all_modalities()

        logger.info("[系统] 反馈系统测试完成")


async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="智能糖尿病胰岛素注射监测系统")
    parser.add_argument("--config", default="config", help="配置文件目录")
    parser.add_argument("--camera", type=int, default=0, help="摄像头ID")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    parser.add_argument("--test", action="store_true", help="测试模式（仅测试反馈）")

    args = parser.parse_args()

    # 配置日志
    logger.remove()
    logger.add(
        sys.stderr,
        level="DEBUG" if args.debug else "INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )

    # 创建系统实例
    system = InjectionMonitoringSystem(
        config_path=args.config,
        debug=args.debug
    )

    try:
        # 初始化系统
        await system.initialize()

        if args.test:
            # 测试模式
            await system.test_feedback()
        else:
            # 正常运行
            await system.start(camera_id=args.camera)

    except KeyboardInterrupt:
        logger.info("[系统] 用户中断")
    except Exception as e:
        logger.error(f"[系统] 运行错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
    finally:
        # 清理资源
        await system.stop()
        logger.info("[系统] 程序退出")


if __name__ == "__main__":
    # Windows环境下设置事件循环策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # 运行主程序
    asyncio.run(main())

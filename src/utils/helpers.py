"""
工具函数模块
"""

import sys
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent


def get_config_path(config_name: str = "model_config.yaml") -> Path:
    """获取配置文件路径"""
    return get_project_root() / "config" / config_name


def ensure_dir(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def setup_logger(level: str = "INFO"):
    """配置日志"""
    from loguru import logger

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<level>{message}</level>"
    )

    return logger


def is_pc_platform() -> bool:
    """检查是否为PC平台"""
    return sys.platform not in ["linux", "darwin"] or not Path("/proc/device-tree/model").exists()


def get_camera_device_id(default: int = 0) -> int:
    """获取摄像头设备ID（可从环境变量读取）"""
    import os

    camera_id = os.getenv("CAMERA_ID", str(default))

    try:
        return int(camera_id)
    except ValueError:
        return default


def format_duration(seconds: float) -> str:
    """格式化时长"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def truncate_text(text: str, max_length: int = 30) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

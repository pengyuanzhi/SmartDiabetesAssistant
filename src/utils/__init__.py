"""
工具模块
"""

from .helpers import (
    get_project_root,
    get_config_path,
    ensure_dir,
    setup_logger,
    is_pc_platform,
    get_camera_device_id,
    format_duration,
    truncate_text
)

__all__ = [
    "get_project_root",
    "get_config_path",
    "ensure_dir",
    "setup_logger",
    "is_pc_platform",
    "get_camera_device_id",
    "format_duration",
    "truncate_text"
]

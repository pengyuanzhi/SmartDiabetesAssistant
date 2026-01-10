"""
pytest配置文件
"""

import pytest
import sys
from pathlib import Path


# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


@pytest.fixture(scope="session")
def project_root():
    """项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def config_dir(project_root):
    """配置目录"""
    return project_root / "config"


@pytest.fixture(scope="session")
def data_dir(project_root):
    """数据目录"""
    return project_root / "data"

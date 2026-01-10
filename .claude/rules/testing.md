# 测试规范

本文档定义项目的测试约定和最佳实践。

## 测试原则

1. **测试先行** - 新功能先写测试
2. **独立运行** - 每个测试可以独立运行
3. **快速执行** - 单元测试应该快速
4. **清晰明确** - 测试名称和断言要清晰
5. **真实场景** - 集成测试模拟真实使用场景

## 测试类型

### 单元测试

测试单个函数或方法的行为。

```python
# tests/test_vision_agent.py
import pytest
import numpy as np
from src.agents.vision_agent import VisionAgent

@pytest.fixture
def vision_agent():
    """创建VisionAgent实例"""
    return VisionAgent(config_path="config/model_config.yaml")

@pytest.fixture
def sample_frame():
    """创建示例帧"""
    return np.zeros((720, 1280, 3), dtype=np.uint8)

class TestVisionAgent:
    """VisionAgent测试套件"""

    def test_initialization(self, vision_agent):
        """测试初始化"""
        assert vision_agent is not None
        assert vision_agent.config is not None

    @pytest.mark.asyncio
    async def test_process_frame(self, vision_agent, sample_frame):
        """测试帧处理"""
        frame_data = {
            "image": sample_frame,
            "timestamp": 1234567890.0,
            "frame_id": 1
        }

        result = await vision_agent.process_frame(frame_data)

        assert result is not None
        assert "pose" in result
        assert "site" in result
        assert "flow" in result

    def test_angle_calculation(self, vision_agent):
        """测试角度计算"""
        p1 = [0, 0]
        p2 = [1, 1]
        p3 = [2, 0]

        angle = vision_agent._calculate_angle_3points(p1, p2, p3)

        assert abs(angle - 90.0) < 0.1  # 应该接近90度
```

### 集成测试

测试多个组件协作。

```python
# tests/test_integration.py
import pytest
from src.agents.main_agent import MainAgent

@pytest.mark.asyncio
async def test_injection_monitoring_workflow():
    """测试完整的注射监测工作流"""
    # 初始化
    agent = MainAgent(config_path="config/model_config.yaml")
    state = await agent.start_monitoring(
        session_id="test_session",
        user_profile={}
    )

    # 模拟视频帧
    frame_data = {
        "image": create_test_frame(),
        "timestamp": 1234567890.0,
        "frame_id": 1
    }

    # 处理帧
    result = await agent.process_frame(frame_data, state)

    # 验证结果
    assert "injection_angle" in result
    assert "alerts" in result

    # 获取摘要
    summary = agent.get_session_summary(result)
    assert summary["session_id"] == "test_session"
```

### 性能测试

测试性能是否满足要求。

```python
# tests/test_performance.py
import pytest
import time
from src.models.model_manager import ModelManager

@pytest.mark.performance
def test_model_inference_speed():
    """测试模型推理速度"""
    model = ModelManager()
    model.get_model("pose_estimator")

    # 准备测试数据
    test_data = np.random.rand(1, 3, 256, 256).astype(np.float32)

    # 预热
    for _ in range(3):
        model.predict("pose_estimator", test_data)

    # 测试推理速度
    start_time = time.time()
    iterations = 100

    for _ in range(iterations):
        result = model.predict("pose_estimator", test_data)

    elapsed = time.time() - start_time
    avg_time = elapsed / iterations

    # 验证性能目标
    assert avg_time < 0.020  # 应该小于20ms
    print(f"平均推理时间: {avg_time*1000:.2f}ms")
```

## 测试结构

```
tests/
├── unit/              # 单元测试
│   ├── test_vision_agent.py
│   ├── test_decision_agent.py
│   └── test_model_manager.py
├── integration/       # 集成测试
│   ├── test_workflow.py
│   └── test_feedback.py
├── performance/       # 性能测试
│   └── test_inference_speed.py
└── fixtures/          # 测试数据
    ├── images/
    └── models/
```

## Fixtures使用

### 配置Fixture

```python
# tests/conftest.py
import pytest
import numpy as np
from pathlib import Path

@pytest.fixture
def test_config_path(tmp_path):
    """创建测试配置"""
    config_file = tmp_path / "test_config.yaml"
    # 写入测试配置
    return str(config_file)

@pytest.fixture
def sample_image():
    """创建测试图像"""
    return np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)

@pytest.fixture
def mock_model(monkeypatch):
    """模拟模型"""
    class MockModel:
        def predict(self, input_data):
            return {"result": "mock"}

    monkeypatch.setattr("src.models.model_manager.TensorRTModel", MockModel)
    return MockModel()
```

## 异步测试

使用pytest-asyncio测试异步代码：

```python
@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await async_function()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_execution():
    """测试并发执行"""
    tasks = [
        async_function(i)
        for i in range(10)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 10
```

## Mock使用

### 模拟外部依赖

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    """使用Mock测试"""
    # 创建Mock对象
    mock_model = Mock()
    mock_model.predict.return_value = {"angle": 45.0}

    # 使用Mock
    result = process_with_model(mock_model, test_data)

    # 验证调用
    mock_model.predict.assert_called_once()

def test_with_patch():
    """使用patch模拟"""
    with patch('src.agents.vision_agent.cv2.imread') as mock_imread:
        mock_imread.return_value = np.zeros((720, 1280, 3))

        result = load_image("test.jpg")

        mock_imread.assert_called_once_with("test.jpg")
```

## 参数化测试

使用不同输入运行相同测试：

```python
@pytest.mark.parametrize("angle,expected", [
    (45, True),    # 边界值
    (67, True),    # 正常值
    (90, True),    # 边界值
    (44, False),   # 过小
    (91, False),   # 过大
])
def test_angle_validation(angle, expected):
    """测试角度验证"""
    result = is_valid_angle(angle)
    assert result == expected
```

## 异常测试

测试错误处理：

```python
def test_invalid_input():
    """测试无效输入"""
    with pytest.raises(ValueError):
        process_angle(-10)  # 负角度应该抛出异常

def test_model_not_found():
    """测试模型未找到"""
    with pytest.raises(FileNotFoundError):
        manager = ModelManager()
        manager.get_model("non_existent_model")
```

## 测试覆盖率

目标：单元测试覆盖率 > 80%

```bash
# 查看覆盖率报告
pytest --cov=src --cov-report=html tests/

# 在浏览器中查看
open htmlcov/index.html
```

### 排除不需要测试的代码

```python
# .coveragerc
[run]
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

## 测试标记

使用标记分类测试：

```python
@pytest.mark.unit
def test_single_function():
    """单元测试"""
    pass

@pytest.mark.integration
def test_workflow():
    """集成测试"""
    pass

@pytest.mark.slow
def test_large_dataset():
    """慢速测试"""
    pass

# 运行特定标记的测试
# pytest -m unit
# pytest -m "not slow"
```

## 测试数据管理

### 使用小数据集

```python
@pytest.fixture
def small_dataset():
    """创建小型测试数据集"""
    return {
        "images": [np.random.rand(100, 100, 3) for _ in range(10)],
        "labels": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    }
```

### 清理测试数据

```python
@pytest.fixture
def temp_database(tmp_path):
    """创建临时数据库"""
    db_path = tmp_path / "test.db"

    # 创建数据库
    db = DatabaseManager(str(db_path))

    yield db

    # 清理
    Path(db_path).unlink()
```

## CI/CD集成

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 测试最佳实践

### 1. 测试命名

```python
# 好的命名
def test_angle_calculation_with_valid_points():
    pass

def test_angle_calculation_with_invalid_points_raises_error():
    pass

# 不好的命名
def test1():
    pass

def test_angle():
    pass
```

### 2. AAA模式

Arrange（准备）- Act（执行）- Assert（断言）

```python
def test_angle_calculation():
    # Arrange：准备测试数据
    p1 = [0, 0]
    p2 = [1, 1]
    p3 = [2, 0]

    # Act：执行被测试的函数
    result = calculate_angle(p1, p2, p3)

    # Assert：验证结果
    assert abs(result - 90.0) < 0.1
```

### 3. 一个测试一个断言

```python
# 好：每个测试只验证一件事
def test_angle_upper_bound():
    assert is_valid_angle(90) == True

def test_angle_exceeds_upper_bound():
    assert is_valid_angle(91) == False

# 不好：一个测试验证多件事
def test_angle_bounds():
    assert is_valid_angle(90) == True
    assert is_valid_angle(91) == False
    assert is_valid_angle(45) == True
```

### 4. 使用描述性断言

```python
# 好：描述性错误消息
assert angle > 0, f"角度应该大于0，实际为{angle}"

# 不好：没有上下文
assert angle > 0
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_vision_agent.py

# 运行特定测试
pytest tests/test_vision_agent.py::TestVisionAgent::test_process_frame

# 显示print输出
pytest -s

# 失败时进入调试器
pytest --pdb

# 并行运行（需要pytest-xdist）
pytest -n auto

# 只运行失败的测试
pytest --lf

# 生成HTML报告
pytest --html=report.html
```

## 测试检查清单

提交代码前确认：

- [ ] 新功能有对应的测试
- [ ] 测试覆盖率没有下降
- [ ] 所有测试通过
- [ ] 异步函数有异步测试
- [ ] 关键路径有集成测试
- [ ] 性能关键部分有性能测试
- [ ] 测试可以在CI环境中运行

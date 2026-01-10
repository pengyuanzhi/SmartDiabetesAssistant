# Python编码规范

本文档定义项目必须遵守的Python编码规范，基于PEP 8并添加项目特定约定。

## 基本规范

### 1. 缩进和空格

- 使用4个空格缩进，不使用Tab
- 每行最大长度：100字符
- 运算符前后加空格：`x = y + z`
- 逗号后加空格：`func(a, b, c)`
- 冒号、分号前不加空格，后加空格

```python
# 正确
result = function(arg1, arg2, arg3)

# 错误
result=function(arg1,arg2,arg3)
x=y+z  # 运算符前后需要空格
```

### 2. 命名规范

#### 文件和模块命名
- 全小写，使用下划线：`video_pipeline.py`
- 包名简短，全小写：`smart_diabetes`

#### 类命名
- 首字母大写驼峰：`VisionAgent`, `ModelManager`

```python
class VideoCamera:
    pass
```

#### 函数和变量命名
- 全小写，使用下划线：`process_frame`, `frame_count`
- 私有成员前缀单下划线：`_internal_method`
- 常量全大写：`MAX_RETRIES`, `DEFAULT_TIMEOUT`

```python
# 正确
def process_video_stream():
    max_retries = 3

# 错误
def ProcessVideoStream():  # 函数不应使用驼峰
    MaxRetries = 3  # 变量不应全大写
```

### 3. 类型注解

所有函数必须添加类型提示：

```python
from typing import List, Dict, Any, Optional

def process_frame(
    frame: np.ndarray,
    config: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """处理视频帧"""
    if frame is None:
        return None
    # ...
    return result

# 异步函数
async def fetch_data(url: str) -> Dict[str, Any]:
    """获取数据"""
    # ...
```

### 4. 文档字符串

使用Google风格的docstring：

```python
def calculate_angle(p1: List[float], p2: List[float], p3: List[float]) -> float:
    """
    计算三点形成的角度

    Args:
        p1: 点1坐标 [x, y]
        p2: 点2坐标（顶点）
        p3: 点3坐标 [x, y]

    Returns:
        角度（度），范围0-180

    Raises:
        ValueError: 如果点坐标无效

    Example:
        >>> angle = calculate_angle([0, 0], [1, 1], [2, 0])
        >>> print(angle)
        90.0
    """
    pass

class VisionAgent:
    """
    视觉智能体

    负责图像采集、模型推理和结果解析。

    Attributes:
        config: 配置字典
        model: AI模型实例

    Example:
        agent = VisionAgent(config_path="config.yaml")
        result = await agent.process_frame(frame)
    """
    pass
```

## 导入规范

### 导入顺序

1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入
4. 每组之间空一行

```python
# 标准库
import asyncio
import time
from typing import Dict, List

# 第三方库
import cv2
import numpy as np
import yaml
from loguru import logger

# 本地导入
from .base_agent import BaseAgent
from ..models.model_manager import ModelManager
```

### 禁止通配符导入

```python
# 错误
from os import *

# 正确
import os
from os import path
```

## 异步编程规范

### 异步函数定义

```python
async def process_frame(frame: np.ndarray) -> Dict[str, Any]:
    """异步处理帧"""
    result = await self.model.infer(frame)
    return result
```

### 并发执行

```python
# 并发执行多个异步任务
tasks = [
    self.pose_estimator.detect(frame),
    self.site_detector.detect(frame),
    self.flow_calculator.calculate(frame)
]

results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 异步上下文管理器

```python
async with asyncio.Lock():
    # 临界区
    pass
```

## 错误处理

### 异常捕获

```python
# 正确：捕获特定异常
try:
    result = model.predict(input_data)
except ModelLoadError as e:
    logger.error(f"模型加载失败: {e}")
    return None
except ValueError as e:
    logger.warning(f"输入数据无效: {e}")
    return default_value

# 错误：捕获所有异常
try:
    result = model.predict(input_data)
except Exception:  # 不要这样
    pass
```

### 异常链

```python
try:
    process_data(data)
except ValueError as e:
    raise DataProcessingError("数据处理失败") from e
```

## 日志规范

使用loguru而不是print：

```python
from loguru import logger

# 不同级别
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 结构化日志
logger.info("处理完成", extra={
    "frame_id": frame_id,
    "processing_time_ms": elapsed * 1000
})
```

## 类设计规范

### 初始化方法

```python
class VideoProcessor:
    """视频处理器"""

    def __init__(self, config_path: str, debug: bool = False):
        """
        初始化视频处理器

        Args:
            config_path: 配置文件路径
            debug: 是否启用调试模式
        """
        self.config_path = Path(config_path)
        self.debug = debug
        self.model = None
        self._load_config()
        self._initialize()
```

### 属性访问

```python
class DatabaseManager:
    """数据库管理器"""

    @property
    def connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._connection is None:
            self._connection = self._connect()
        return self._connection
```

## 代码组织

### 模块结构

```python
# 1. 模块文档字符串
"""模块描述"""

# 2. 导入
import sys
from typing import Dict

# 3. 常量
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# 4. 全局变量
_global_state = {}

# 5. 类定义
class MyClass:
    pass

# 6. 函数定义
def my_function():
    pass

# 7. 主程序入口
if __name__ == "__main__":
    pass
```

## 性能优化

### 避免不必要的计算

```python
# 低效
for i in range(len(data)):
    process(data[i])

# 高效
for item in data:
    process(item)
```

### 使用生成器

```python
# 节省内存
def process_large_file(file_path: str):
    with open(file_path) as f:
        for line in f:  # 生成器，不一次性加载
            yield process_line(line)
```

### 缓存结果

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(x: int, y: int) -> int:
    """计算密集型函数"""
    return x ** y
```

## 代码审查清单

提交代码前检查：

- [ ] 代码符合PEP 8规范
- [ ] 所有函数有类型注解
- [ ] 所有公共函数有docstring
- [ ] 没有print语句，使用logger
- [ ] 异步函数使用async/await
- [ ] 异常处理完善
- [ ] 没有硬编码路径
- [ ] 常量定义在模块顶部
- [ ] 没有表情符号
- [ ] 测试覆盖充分

## 代码格式化工具

项目使用以下工具自动检查和格式化代码：

```bash
# 格式化代码
black src/

# 检查代码风格
flake8 src/

# 类型检查
mypy src/
```

## 特定约定

### 医疗数据处理

```python
# 处理医疗数据时必须记录日志
def process_medical_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """处理医疗数据"""
    logger.info("处理医疗数据", extra={
        "patient_id": hash_value(data["patient_id"]),  # 匿名化
        "timestamp": datetime.now().isoformat()
    })

    # 验证数据
    if not validate_data(data):
        logger.error("医疗数据验证失败")
        raise InvalidDataError("数据格式错误")

    # 处理数据
    result = _process(data)

    logger.info("医疗数据处理完成")
    return result
```

### AI模型调用

```python
# 所有模型调用必须有超时和错误处理
async def model_inference(model: BaseModel, input_data: np.ndarray) -> Any:
    """模型推理"""
    try:
        async with asyncio.timeout(5.0):  # 5秒超时
            result = await model.predict(input_data)
            return result
    except asyncio.TimeoutError:
        logger.error("模型推理超时")
        raise ModelTimeoutError("推理超时")
    except ModelError as e:
        logger.error(f"模型推理失败: {e}")
        raise
```

## 禁止事项

1. **禁止使用表情符号** - 代码、注释、文档中不使用emoji
2. **禁止print** - 使用logger记录日志
3. **禁止全局变量** - 使用类或配置文件管理状态
4. **禁止硬编码路径** - 使用Path和配置文件
5. **禁止忽略类型提示** - 所有函数必须有类型注解
6. **禁止裸except** - 必须指定异常类型
7. **禁止在循环中执行I/O** - 使用异步或批处理

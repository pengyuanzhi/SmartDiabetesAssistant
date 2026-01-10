# PC端快速启动指南

## 5分钟快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd SmartDiabetesAssistant

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装PC调试依赖
pip install -r requirements-pc.txt
```

### 2. 测试摄像头

```bash
# 检测可用的摄像头
python scripts/test_camera.py
```

### 3. 快速启动

```bash
# 使用默认摄像头（ID=0）
python scripts/quick_start.py

# 指定摄像头ID
python scripts/quick_start.py 1
```

### 4. 运行完整系统

```bash
# 调试模式
python src/main.py --config config --camera 0 --debug

# 正常模式
python src/main.py --config config --camera 0
```

## 功能清单

### 已实现（PC端可调试）

- 摄像头视频流采集
- 实时图像处理
- 姿态估计（模拟数据）
- 目标检测（模拟数据）
- 决策规则引擎
- 多模态反馈协调
- 数据库存储
- 日志记录

### 待完善（需要实际模型）

- 真实的RTMPose模型推理
- 真实的YOLOv8模型推理
- 光流计算
- TTS语音合成
- 硬件驱动（实际部署时）

## PC端调试限制

### 模拟功能

| 功能 | PC端 | 实际硬件 |
|------|------|----------|
| 摄像头 | USB摄像头 | Sony IMX500 |
| 显示 | OpenCV窗口 | OLED屏 |
| 语音 | 系统TTS | Coqui TTS |
| 震动 | 无 | LRA马达 |
| AI模型 | 模拟数据 | TensorRT/TFLite |

### 注意事项

1. **模拟数据**: 当前使用模拟数据演示功能
2. **性能差异**: PC端性能不代表边端性能
3. **GPU加速**: PC端可使用CUDA加速（需NVIDIA显卡）

## 开发建议

### 循序渐进

1. **第一阶段**: 熟悉代码结构
   - 运行 `quick_start.py` 查看效果
   - 阅读核心模块代码
   - 理解智能体架构

2. **第二阶段**: 集成真实模型
   - 下载预训练模型
   - 替换模拟推理
   - 测试模型性能

3. **第三阶段**: 功能完善
   - 训练自定义模型
   - 优化推理性能
   - 准备硬件部署

### 调试技巧

启用详细日志：
```bash
python src/main.py --debug 2>&1 | tee debug.log
```

使用VS Code调试器：
- 在 `src/main.py` 设置断点
- 使用VS Code的Python调试器
- 查看变量值和调用栈

性能分析：
```bash
# 使用cProfile分析性能
python -m cProfile -o profile.stats src/main.py

# 查看结果
python -m pstats profile.stats
```

## 数据集准备

### 1. 收集训练数据

使用PC摄像头收集样本数据：
```bash
python scripts/collect_data.py \
    --output data/raw \
    --categories abdomen thigh upper_arm \
    --samples-per-category 100
```

### 2. 数据增强

```python
from scripts.augment_data import augment_dataset

augment_dataset(
    input_dir="data/raw",
    output_dir="data/augmented",
    augment_factor=5
)
```

## 模型训练（可选）

### 1. 准备环境

```bash
# 安装训练依赖
pip install torch torchvision ultralytics mmpose

# 下载预训练模型
python scripts/download_pretrained.py
```

### 2. 训练自定义模型

```bash
# 训练YOLOv8检测器
python scripts/train_detector.py \
    --data data/injection_sites.yaml \
    --epochs 50 \
    --batch-size 16

# 训练姿态估计模型
python scripts/train_pose.py \
    --data data/pose_dataset \
    --epochs 100
```

## 常见问题

### Q1: 摄像头无法打开

**解决方案**:
```bash
# 列出可用摄像头
python scripts/list_cameras.py

# 尝试不同的camera_id
python src/main.py --camera 1  # 或 2, 3...
```

### Q2: 模型推理速度慢

**解决方案**:
- 降低输入分辨率
- 使用量化模型（INT8）
- 启用GPU加速（如果有NVIDIA显卡）
- 减少模型数量

### Q3: 内存不足

**解决方案**:
- 减小batch size
- 降低视频分辨率
- 关闭不必要的应用

## 部署到硬件

PC开发完成后，部署到Jetson或Raspberry Pi：

1. **导出模型**
```bash
python scripts/export_models.py \
    --format onnx \
    --output models/exported
```

2. **传输文件**
```bash
# 使用scp传输到Jetson
scp -r SmartDiabetesAssistant/ jetson@192.168.1.100:/home/jetson/

# 或使用rsync
rsync -avz --exclude 'venv' --exclude '__pycache__' \
    SmartDiabetesAssistant/ jetson@192.168.1.100:/home/jetson/
```

3. **在目标设备上安装依赖**
```bash
# Jetson
ssh jetson@192.168.1.100
cd SmartDiabetesAssistant
pip install -r requirements-jetson.txt

# Raspberry Pi
ssh pi@192.168.1.100
cd SmartDiabetesAssistant
pip install -r requirements-pi.txt
```

## 性能基准

### PC端预期性能（Intel i7, 16GB RAM）

| 模型 | 推理时间 | FPS |
|------|---------|-----|
| RTMPose-Lite | ~50ms | 20 |
| YOLOv8n | ~10ms | 100 |
| LiteFlowNet | ~30ms | 33 |

### 边端设备预期性能

| 设备 | RTMPose | YOLOv8 | 总延迟 |
|------|---------|--------|--------|
| Jetson Orin Nano | 15ms | 2ms | <50ms |
| Pi 5 + 26T | 25ms | 5ms | <80ms |

## 下一步

1. 完成PC端环境搭建
2. 运行基础测试
3. 收集真实数据
4. 训练自定义模型（可选）
5. 采购硬件设备
6. 部署到边端设备

## 参考资源

- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [YOLOv8文档](https://docs.ultralytics.com/)
- [OpenCV教程](https://docs.opencv.org/4.x/)
- [PyTorch入门](https://pytorch.org/tutorials/)

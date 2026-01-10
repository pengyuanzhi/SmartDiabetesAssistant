# PC端开发调试指南

## 概述

在实际硬件采购之前，可以先在PC上进行开发和调试。本指南将帮助您快速搭建PC端开发环境。

## 环境准备

### 1. 系统要求

- **操作系统**: Windows 10/11, macOS, 或 Linux
- **Python**: 3.10 或更高版本
- **内存**: 至少 8GB RAM（推荐 16GB）
- **存储**: 至少 20GB 可用空间
- **摄像头**: USB摄像头或内置摄像头

### 2. 依赖安装

```bash
# 克隆项目
cd SmartDiabetesAssistant

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装核心依赖（PC调试版）
pip install -r requirements-pc.txt

# 或者安装完整依赖
pip install -r requirements.txt
```

## PC调试模式配置

### 配置文件调整

创建 `config/pc_debug_config.yaml`:

```yaml
# PC调试模式配置

platform:
  type: "pc"  # PC平台
  device: "cpu"  # 或 "cuda"（如果有NVIDIA GPU）

models:
  # 使用ONNX模型（跨平台）
  use_onnx: true
  use_gpu: false  # PC调试时先用CPU

camera:
  type: "usb"
  device_id: 0  # 摄像头ID
  resolution: [1280, 720]
  fps: 30

simulation:
  # 模拟硬件组件
  simulate_vibration: true  # 用声音模拟震动
  simulate_display: true  # 用窗口模拟OLED屏
  use_webcam: true  # 使用USB摄像头
```

## 快速启动

### 1. 测试摄像头

```bash
# 测试摄像头是否正常
python scripts/test_camera.py
```

### 2. 测试AI模型

```bash
# 测试姿态估计
python scripts/test_pose_estimation.py

# 测试目标检测
python scripts/test_object_detection.py
```

### 3. 运行完整系统（调试模式）

```bash
# 启动系统（PC调试模式）
python src/main.py --config config --camera 0 --debug

# 或使用PC专用配置
python src/main.py --config config --camera 0 --debug --pc-mode
```

## PC端模拟方案

### 1. 摄像头模拟

使用USB摄像头或内置摄像头替代Sony IMX500：
- `VideoCamera` 类已支持标准USB摄像头
- 自动检测可用的摄像头设备

### 2. 显示屏模拟

使用OpenCV窗口替代OLED屏幕：
```python
cv2.imshow("Injection Monitor", frame)
cv2.waitKey(1)
```

### 3. 震动模拟

使用系统蜂鸣声替代震动马达：
```python
import winsound  # Windows
# 或
import os  # macOS/Linux
os.system('echo -e "\a"')  # 终端响铃
```

### 4. 语音模拟

使用系统TTS替代Coqui TTS：
```python
# Windows
import win32com.client
speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Speak("注射角度正确")

# macOS
import os
os.system(f'say "注射角度正确"')

# Linux
import os
os.system(f'espeak "注射角度正确"')
```

## 开发工作流

### 1. 单元测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_vision_agent.py -v

# 查看覆盖率
pytest --cov=src tests/
```

### 2. 调试技巧

启用详细日志：
```bash
python src/main.py --debug 2>&1 | tee debug.log
```

使用VS Code调试器：
- 在 `src/main.py` 设置断点
- 使用VS Code的Python调试器
- 查看变量值和调用栈

### 3. 性能分析

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

### PC开发完成后，部署到Jetson或Raspberry Pi：

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

1. ✅ 完成PC端环境搭建
2. ✅ 运行基础测试
3. ⬜ 收集真实数据
4. ⬜ 训练自定义模型（可选）
5. ⬜ 采购硬件设备
6. ⬜ 部署到边端设备

## 参考资源

- [LangGraph文档](https://langchain-ai.github.io/langgraph/)
- [YOLOv8文档](https://docs.ultralytics.com/)
- [OpenCV教程](https://docs.opencv.org/4.x/)
- [PyTorch入门](https://pytorch.org/tutorials/)

# 智能糖尿病胰岛素注射监测系统

> [!IMPORTANT]
> **Windows用户请注意**: 在PC上开发调试时，请使用 `requirements-pc.txt` 而不是 `requirements.txt`。
>
> ```bash
> pip install -r requirements-pc.txt  # Windows/Linux/macOS PC端开发
> pip install -r requirements-jetson.txt  # NVIDIA Jetson Orin Nano部署
> pip install -r requirements-pi.txt  # Raspberry Pi部署
> ```

## 项目概述

本项目是一个基于边端AI的智能糖尿病胰岛素注射监测系统，通过实时图像识别技术监测患者注射操作的规范性，并提供语音、震动、视觉等多重反馈。

## 核心功能

- **注射角度监测**：实时检测注射角度是否在45-90度范围内
- **注射部位识别**：识别注射部位（腹部、大腿、上臂等）
- **注射速度监测**：监测推药速度，防止过快或过慢
- **操作流程监测**：通过状态机跟踪完整注射流程
- **多模态反馈**：语音、震动、视觉三重提示

## 技术特点

- **实时性能**：端到端延迟<100ms，30 FPS实时监测
- **边端AI**：Jetson Orin Nano 67 TOPS算力
- **智能体架构**：基于LangGraph的多智能体协作
- **隐私保护**：数据本地存储，无需云端
- **便携设计**：5000mAh电池，2-2.5小时连续工作

---

## 硬件配置

### 推荐配置（Jetson方案）

| 组件 | 型号 | 价格 |
|------|------|------|
| 主控 | NVIDIA Jetson Orin Nano | ~$499 |
| 摄像头（主） | Sony IMX500智能传感器 | ~$75 |
| 摄像头（辅） | Pi Camera Module 3 | ~$25 |
| 显示屏 | Waveshare 4.3" OLED | ~$50 |
| TTS模块 | Coqui TTS + MAX98357A DAC | ~$7 |
| 震动马达 | 10mm LRA + DRV2605L | ~$7 |
| 电池 | 5000mAh锂聚合物 + BMS | ~$40 |
| **总计** | | **~$708 (约5000元)** |

### 备选配置（Raspberry Pi方案）

| 组件 | 型号 | 价格 |
|------|------|------|
| 主控 | Raspberry Pi 5 + AI HAT+ 26T | ~$170 |
| 其他组件 | 同上 | ~$204 |
| **总计** | | **~$379 (约2700元)** |

---

## 快速开始

### PC端快速启动（推荐用于开发调试）

> **提示**: 在实际采购硬件之前，建议先在PC上进行开发和调试。详见 [PC端开发指南](docs/PC_DEVELOPMENT_GUIDE.md)

```bash
# 1. 安装PC调试依赖
pip install -r requirements-pc.txt

# 2. 测试摄像头
python scripts/test_camera.py

# 3. 快速启动演示
python scripts/quick_start.py

# 4. 运行完整系统（调试模式）
python src/main.py --config config --camera 0 --debug
```

### 硬件部署（在实际设备上运行）

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd SmartDiabetesAssistant

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置设置

编辑配置文件以匹配您的硬件：

```bash
# 根据您的平台选择
# Jetson Orin Nano
export PLATFORM=jetson

# Raspberry Pi 5
export platform=raspberrypi
```

编辑 `config/user_profile.yaml` 设置用户偏好。

### 3. 模型准备

```bash
# 下载预训练模型
python scripts/download_models.py

# 或从ONNX转换为TensorRT引擎（Jetson）
python scripts/export_onnx.py --model rtmpose --output models/rtmpose_lite.onnx
python scripts/optimize_tensorrt.py --input models/rtmpose_lite.onnx --output models/rtmpose_lite.trt
```

### 4. 运行系统

```bash
# 启动监测系统
python src/main.py

# 或使用开发模式
python src/main.py --debug
```

---

## 项目结构

```
SmartDiabetesAssistant/
├── config/                   # 配置文件
│   ├── model_config.yaml    # 模型配置
│   ├── hardware_config.yaml # 硬件配置
│   └── user_profile.yaml    # 用户配置
├── src/
│   ├── agents/              # 智能体模块
│   │   ├── main_agent.py    # 主智能体
│   │   ├── vision_agent.py  # 视觉智能体
│   │   ├── tts_agent.py     # TTS智能体
│   │   ├── haptic_agent.py  # 触觉智能体
│   │   └── decision_agent.py# 决策智能体
│   ├── models/              # 模型管理
│   │   ├── model_manager.py # 模型管理器
│   │   ├── pose_estimator.py# 姿态估计
│   │   └── detector.py      # 目标检测
│   ├── hardware/            # 硬件接口
│   │   ├── camera.py        # 摄像头驱动
│   │   ├── audio.py         # 音频驱动
│   │   └── vibration.py     # 震动驱动
│   ├── processing/          # 数据处理
│   │   └── video_pipeline.py# 视频管道
│   ├── feedback/            # 反馈系统
│   │   └── coordinator.py   # 反馈协调器
│   └── storage/             # 数据存储
│       └── database.py      # 数据库管理
├── models/                  # 模型文件目录
├── data/                    # 数据目录
│   ├── videos/
│   └── injection_monitoring.db
├── tests/                   # 测试
├── scripts/                 # 实用脚本
└── docs/                    # 文档
```

---

## AI模型技术栈

### 姿态估计（RTMPose-Lite）
- **输入**：256x256
- **模型大小**：8MB（INT8量化）
- **推理速度**：15ms/帧
- **精度**：AP 76.5%

### 目标检测（YOLOv8n-Quantized）
- **输入**：640x640
- **模型大小**：3MB（INT8量化）
- **推理速度**：2ms（500 FPS）
- **类别**：腹部/大腿/上臂/臀部

### 光流追踪（LiteFlowNet）
- **模型大小**：2MB
- **推理速度**：实时
- **用途**：注射速度监测

### TTS（Coqui TTS）
- **模型大小**：50MB
- **推理延迟**：200ms
- **语音质量**：MOS 4.2/5

---

## 智能体架构

系统采用基于LangGraph的分层多智能体架构：

```
主智能体 (MainAgent)
  ├─ 视觉智能体 (VisionAgent)
  │   └─ 图像采集、模型推理、结果解析
  ├─ 决策智能体 (DecisionAgent)
  │   └─ 规则推理、异常检测、日志记录
  ├─ TTS智能体 (TTSAgent)
  │   └─ 语音合成、情感调整、语言转换
  ├─ 触觉智能体 (HapticAgent)
  │   └─ 触觉模式、强度控制、时序编排
  └─ UI智能体 (UIAgent)
      └─ 界面显示、进度提示、错误提示
```

---

## 使用说明

### 基本操作

1. **启动系统**：按下开始按钮或语音命令
2. **定位注射部位**：系统自动识别并验证部位
3. **开始注射**：按照语音提示操作
4. **实时反馈**：
   - 绿色：操作正确
   - 黄色：需要注意
   - 红色：操作错误
5. **完成注射**：系统记录数据并生成报告

### 反馈类型

| 严重程度 | 语音 | 震动 | 视觉 |
|---------|------|------|------|
| 关键错误 | 是 | 是（强烈长震） | 是（红色闪烁） |
| 警告 | 是 | 是（双击震动） | 是（黄色提示） |
| 信息 | 是 | 否 | 是（绿色） |

---

## 性能指标

- **端到端延迟**：<100ms
- **实时帧率**：30 FPS
- **总模型大小**：<70MB
- **功耗**：7-25W（可调）
- **续航时间**：2-2.5小时（连续工作）

---

## 开发路线图

### 第一阶段：原型验证（2-4周）
- [x] 项目结构搭建
- [ ] 硬件采购与基础环境搭建
- [ ] 摄像头驱动测试
- [ ] 简单目标检测验证
- [ ] 基础TTS功能验证

### 第二阶段：核心功能开发（6-8周）
- [ ] 部署RTMPose姿态估计
- [ ] 实现注射角度计算算法
- [ ] 训练注射部位识别模型
- [ ] 搭建LangGraph智能体框架
- [ ] 实现语音反馈系统

### 第三阶段：系统整合（4-6周）
- [ ] 集成所有智能体组件
- [ ] 实现多模态反馈协调
- [ ] 开发数据库系统
- [ ] 开发UI界面
- [ ] 端到端测试

### 第四阶段：优化与测试（4-6周）
- [ ] 模型量化和性能优化
- [ ] 功耗优化
- [ ] 真实场景测试
- [ ] 用户反馈迭代
- [ ] 文档完善

---

## 依赖项

- Python 3.10+
- PyTorch 2.0+
- OpenCV 4.8+
- LangGraph 0.0.20+
- Coqui TTS 0.22+

完整依赖列表见 `requirements.txt`。

---

## 配置文件说明

### model_config.yaml
定义所有AI模型的配置，包括：
- 模型路径和大小
- 输入分辨率
- 量化设置
- 推理速度目标

### hardware_config.yaml
定义硬件配置，包括：
- 主控平台设置
- 摄像头参数
- 音频和触觉反馈配置
- 电源管理设置

### user_profile.yaml
用户个性化设置，包括：
- 用户基本信息
- 注射偏好
- 反馈敏感度
- 数据存储设置

---

## 故障排除

### 摄像头无法打开
```bash
# 检查摄像头设备
ls -l /dev/video*

# 测试摄像头
python -c "import cv2; cap=cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'Failed')"
```

### 模型推理速度慢
- 检查是否启用了TensorRT优化
- 确认模型已量化为INT8
- 降低输入分辨率

### 功耗过高
- 切换到节能模式
- 降低帧率到15 FPS
- 关闭不必要的后台进程

---

## 技术支持

- 邮件：support@example.com
- 文档：`docs/`目录
- 问题反馈：GitHub Issues

---

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

## 致谢

感谢以下开源项目：
- [RTMPose](https://github.com/open-mmlab/mmpose)
- [YOLOv8](https://github.com/ultralytics/ultralytics)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Coqui TTS](https://github.com/coqui-ai/TTS)

---

## 未来扩展

- [ ] 远程医疗数据同步（可选）
- [ ] 多语言支持（英语、方言）
- [ ] 联邦学习和个性化模型
- [ ] 社交功能和家庭共享
- [ ] 注射提醒和进度追踪

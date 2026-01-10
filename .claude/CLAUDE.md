# 智能糖尿病胰岛素注射监测系统 - 项目说明

## 项目概述

本项目是一个基于边端AI的智能糖尿病胰岛素注射监测系统，通过实时图像识别技术监测患者注射操作的规范性，并提供语音、震动、视觉等多重反馈。

## 技术栈

- **语言**: Python 3.10+
- **AI框架**: PyTorch, TensorRT, TFLite
- **智能体**: LangGraph (状态图架构)
- **计算机视觉**: OpenCV, RTMPose, YOLOv8
- **硬件平台**: NVIDIA Jetson Orin Nano / Raspberry Pi 5

## 核心模块

### 智能体系统 (src/agents/)
- `main_agent.py` - 主智能体，协调所有子智能体
- `vision_agent.py` - 视觉处理，姿态估计和目标检测
- `decision_agent.py` - 决策判断，规则引擎
- `tts_agent.py` - 文本转语音
- `haptic_agent.py` - 震动反馈控制
- `ui_agent.py` - 用户界面显示

### 核心功能 (src/)
- `models/model_manager.py` - AI模型统一管理
- `processing/video_pipeline.py` - 实时视频流处理
- `feedback/coordinator.py` - 多模态反馈协调
- `storage/database.py` - SQLite数据存储

## 开发指南

### PC端开发
在实际硬件采购前，先在PC上进行开发和调试：

```bash
# 安装PC调试依赖
pip install -r requirements-pc.txt

# 测试摄像头
python scripts/test_camera.py

# 快速启动演示
python scripts/quick_start.py
```

### 硬件部署
部署到Jetson或Raspberry Pi时，需要：
1. 导出模型为TensorRT或TFLite格式
2. 安装硬件特定依赖（requirements.txt）
3. 配置硬件驱动（摄像头、震动马达等）

## 编码规范

请严格遵守 `.claude/rules/` 目录下的规范：
- `code-style.md` - Python编码风格（PEP 8）
- `testing.md` - 测试约定
- `security.md` - 安全要求（特别是医疗数据）

## 重要约定

1. **不要使用表情符号** - 代码、注释、文档中不使用emoji
2. **类型提示** - 所有函数必须添加类型注解
3. **文档字符串** - 使用Google风格的docstring
4. **异步优先** - I/O操作使用async/await
5. **错误处理** - 所有外部调用必须有异常处理
6. **日志规范** - 使用loguru，不要用print

## AI模型说明

当前使用模拟数据进行演示。真实部署时需要：
- RTMPose-Lite (姿态估计)
- YOLOv8n-INT8 (目标检测)
- LiteFlowNet (光流计算)
- Coqui TTS (语音合成)

模型文件应放在 `models/` 目录，配置在 `config/model_config.yaml`。

## 数据隐私

- 所有数据仅本地存储（SQLite）
- 不上传任何视频或图像到云端
- 用户数据加密存储
- 遵守HIPAA/GDPR等医疗数据规范

## 性能目标

- 端到端延迟: < 100ms
- 实时帧率: 30 FPS
- 模型总大小: < 70MB
- 功耗: 7-25W（可调）

## 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_vision_agent.py -v

# 查看覆盖率
pytest --cov=src tests/
```

## 文档结构

- `README.md` - 项目概述和快速开始
- `QUICKSTART.md` - 5分钟快速启动指南
- `docs/PC_DEVELOPMENT_GUIDE.md` - PC端开发完整指南
- `config/` - 配置文件目录

## 常见任务

### 添加新的告警规则
编辑 `src/agents/decision_agent.py` 中的 `_check_*` 方法

### 修改反馈策略
编辑 `src/feedback/coordinator.py` 中的反馈生成逻辑

### 更新模型配置
编辑 `config/model_config.yaml`

### 添加新的AI模型
1. 在 `src/models/model_manager.py` 中注册
2. 在 `config/model_config.yaml` 中配置
3. 在对应的智能体中调用

## 贡献流程

1. 创建功能分支
2. 遵守编码规范
3. 添加单元测试
4. 运行测试确保通过
5. 提交Pull Request

## 许可证

MIT License

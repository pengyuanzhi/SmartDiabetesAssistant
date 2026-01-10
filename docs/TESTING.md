# 测试指南

本文档介绍如何使用项目中的测试脚本验证系统各组件功能。

## 目录

- [快速测试](#快速测试)
- [摄像头测试](#摄像头测试)
- [音频系统测试](#音频系统测试)
- [TTS智能体测试](#tts智能体测试)
- [反馈系统测试](#反馈系统测试)
- [完整系统测试](#完整系统测试)

---

## 快速测试

运行快速启动脚本进行基础功能验证：

```bash
python scripts/quick_start.py
```

---

## 摄像头测试

### 功能

- 检测所有可用摄像头
- 显示摄像头参数（分辨率、帧率、后端）
- 保存测试帧图像
- 测试视频流性能

### 使用方法

```bash
python scripts/test_camera.py
```

### Windows用户注意

- 脚本会自动使用DirectShow后端
- 使用无GUI模式，避免OpenCV显示问题
- 测试帧保存为 `camera_X_test.jpg`

### 输出示例

```
=== 检测可用的摄像头 ===

[OK] 摄像头 0:
  - 分辨率: 1280x720
  - 帧率: 30
  - 后端: DSHOW

=== 测试摄像头 0 ===
实际分辨率: 1280x720
实际帧率: 30
开始读取帧...

已读取 150 帧 | FPS: 29.8

=== 测试结果 ===
总帧数: 150
总时长: 5.03 秒
平均帧率: 29.82 FPS
[成功] 摄像头工作正常
```

---

## 音频系统测试

### 功能

- 检测音频输出设备
- 测试系统TTS（pyttsx3）
- 测试Coqui TTS（可选）
- 测试音频录制功能（可选）

### 使用方法

```bash
python scripts/test_audio.py
```

### 依赖安装

```bash
# 系统TTS（必需）
pip install pyttsx3

# Coqui TTS（可选，提供更自然的语音）
pip install TTS

# 音频录制（可选）
pip install pyaudio
```

### Windows用户注意

- 系统TTS开箱即用
- Coqui TTS首次运行会下载模型（约50MB）
- pyaudio安装可能需要额外步骤，参考 [安装指南](INSTALLATION.md)

### 输出示例

```
=== 检测音频设备 ===

[成功] Windows音频系统可用
提示: 使用系统默认音频输出设备

=== 测试系统TTS ===

检测到 3 个可用语音:

语音 0:
  - ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ZH-CN_XIAOXIANG_11.0
  - 名称: Microsoft Xiaoxiang - Chinese (Simplified, PRC)
  - 语言: ['zh-CN']

[成功] 使用中文语音: Microsoft Xiaoxiang - Chinese (Simplified, PRC)

开始语音测试...

[1/3] 正在播放: 智能糖尿病助手启动
[2/3] 正在播放: 请保持45度角注射
[3/3] 正在播放: 注射速度过快，请减慢

[成功] 系统TTS测试完成
```

---

## TTS智能体测试

### 功能

- 测试TTS智能体基本功能
- 测试情感语音合成（neutral/positive/negative/urgent）
- 测试语音队列功能
- 测试多语言切换
- 性能测试
- 保存语音文件

### 使用方法

```bash
python scripts/test_tts_agent.py
```

### 交互式菜单

```
=== TTS智能体测试工具 ===

可用测试:
  1. 基本功能测试
  2. 情感语音测试
  3. 语音队列测试
  4. 多语言切换测试
  5. 性能测试
  6. 保存功能测试
  7. 运行所有测试
  0. 退出

请选择测试 (0-7):
```

### 测试场景

**1. 基本功能测试**

测试文本到语音的基本转换功能。

**2. 情感语音测试**

测试不同情感的语音合成：
- `neutral`: 中性情感，用于一般信息
- `positive`: 积极情感，用于正面反馈
- `negative`: 负面情感，用于警告
- `urgent`: 紧急情感，用于严重错误

**3. 语音队列测试**

测试连续语音提示的队列处理。

**4. 多语言切换测试**

测试中英文切换功能。

**5. 性能测试**

测量语音合成的响应时间，确保满足实时性要求。

**6. 保存功能测试**

将语音文件保存到磁盘，供后续使用。

---

## 反馈系统测试

### 功能

- 测试音频反馈
- 测试震动反馈（PC端使用模拟模式）
- 测试视觉反馈
- 测试反馈协调器
- 测试优先级处理
- 完整集成场景测试

### 使用方法

```bash
python scripts/test_feedback.py
```

### 测试场景

**1. 音频反馈测试**

测试不同告警级别的语音输出：
- `INFO`: 系统就绪、操作正确
- `WARNING`: 角度警告、速度偏快
- `CRITICAL`: 紧急停止、严重错误

**2. 震动反馈测试**

测试不同震动模式：
- `gentle_reminder`: 轻柔提醒
- `strong_warning`: 强烈警告
- `double_click`: 双重点击
- `gradual`: 渐强震动

注意: PC端使用模拟模式，在控制台输出震动模式信息。

**3. 视觉反馈测试**

生成测试图像验证视觉反馈：
- 文本提示
- 警告框
- 错误框
- 成功提示

输出文件保存到 `test_visual_outputs/` 目录。

**4. 反馈协调器测试**

测试多模态反馈的协调和优先级处理。

**5. 优先级处理测试**

测试告警去重和优先级排序。

**6. 集成场景测试**

模拟完整的注射监测流程，测试所有反馈组件的协作。

### 场景示例

```
模拟完整注射流程...

场景: 用户进行胰岛素注射
系统实时监测并提供反馈

1. 系统启动
  级别: info
  消息: 智能糖尿病助手已启动
  状态: [反馈已生成]

2. 检测到注射器
  级别: info
  消息: 检测到注射器，请准备注射
  状态: [反馈已生成]

3. 角度检测（角度偏小）
  级别: warning
  消息: 注射角度偏小，请调整至45度以上
  状态: [反馈已生成]

...
```

---

## 完整系统测试

### 前置条件

确保已通过所有组件测试：

1. [x] 摄像头测试通过
2. [x] 音频系统测试通过
3. [x] TTS智能体测试通过
4. [x] 反馈系统测试通过

### 运行完整系统

```bash
# 使用摄像头 0
python src/main.py --camera 0

# 调试模式
python src/main.py --camera 0 --debug

# 指定配置文件
python src/main.py --camera 0 --config config/user_profile.yaml
```

### 测试流程

1. **启动系统**

   系统初始化，播放启动提示音

2. **准备阶段**

   - 将注射器对准摄像头
   - 系统识别注射器
   - 提示"可以开始注射"

3. **角度监测**

   - 调整注射角度到45-90度
   - 系统实时反馈角度信息
   - 角度过小时触发警告

4. **速度监测**

   - 开始推药
   - 保持均匀速度（>5秒）
   - 速度过快触发警告

5. **完成注射**

   - 拔出针头
   - 按压注射部位
   - 系统播放完成提示

---

## 故障排查

### 摄像头问题

**问题**: 未检测到摄像头

**解决方案**:
1. 检查摄像头连接
2. 关闭其他使用摄像头的程序
3. Windows用户检查设备管理器
4. 尝试重启摄像头

**问题**: OpenCV GUI错误

**解决方案**: 测试脚本已使用无GUI模式，如果仍有问题：
```bash
# 手动保存测试帧
python -c "import cv2; cap = cv2.VideoCapture(0, cv2.CAP_DSHOW); _, frame = cap.read(); cv2.imwrite('test.jpg', frame); cap.release()"
```

### 音频问题

**问题**: 无法播放声音

**解决方案**:
1. 检查系统音量设置
2. 确认音频输出设备已连接
3. Windows用户检查声音设置

**问题**: Coqui TTS下载失败

**解决方案**:
1. 检查网络连接
2. 使用系统TTS代替
3. 手动下载模型并指定路径

**问题**: pyaudio安装失败

**解决方案**:
```bash
# Windows
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt install python3-pyaudio

# macOS
brew install portaudio
pip install pyaudio
```

### TTS智能体问题

**问题**: 导入TTS智能体失败

**解决方案**:
1. 确保已安装所有依赖: `pip install -r requirements-pc.txt`
2. 检查Python路径是否正确
3. 确认在项目根目录运行脚本

**问题**: 语音合成速度过慢

**解决方案**:
1. 使用系统TTS而非Coqui TTS
2. 检查CPU使用率
3. 调整TTS配置参数

### 反馈系统问题

**问题**: 震动反馈无效果

**说明**: PC端使用模拟模式，实际硬件上才会有真实震动

**问题**: 视觉反馈显示异常

**解决方案**:
1. 检查OpenCV版本: `python -c "import cv2; print(cv2.__version__)"`
2. 确认numpy正常工作
3. 检查输出目录权限

---

## 性能基准

### 摄像头性能

- 分辨率: 1280x720
- 帧率: 30 FPS
- 延迟: <50ms

### 音频性能

- 系统TTS响应: <200ms
- Coqui TTS响应: <500ms
- 音频播放延迟: <50ms

### TTS智能体性能

- 语音合成: <1s
- 队列处理: 实时
- 内存占用: <100MB

### 反馈系统性能

- 反馈生成: <100ms
- 多模态协调: <200ms
- 去重处理: <10ms

---

## 持续测试

### 自动化测试

项目包含单元测试和集成测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_camera.py
pytest tests/test_tts_agent.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 性能测试

```bash
# 摄像头性能测试
python scripts/test_camera.py --performance

# TTS性能测试
python scripts/test_tts_agent.py --performance

# 端到端性能测试
python src/main.py --camera 0 --benchmark
```

---

## 获取帮助

如果测试过程中遇到问题：

1. 查看本文档的故障排查部分
2. 检查 [安装指南](INSTALLATION.md)
3. 查看 [PC开发指南](PC_DEVELOPMENT_GUIDE.md)
4. 查看项目Issues页面
5. 提交新的Issue

---

## 下一步

完成所有测试后：

1. 查看 [快速开始](../QUICKSTART.md)
2. 阅读 [配置指南](CONFIGURATION.md)
3. 了解 [架构设计](ARCHITECTURE.md)
4. 开始自定义开发

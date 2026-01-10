# 安装指南

## Windows 安装

### 前置要求

1. **Python 版本**: 推荐 Python 3.10 或 3.11（避免使用 3.12+，因为很多包还不兼容）
2. **Visual Studio**: 安装 Desktop C++ 工作负载
3. **CMake**: 从 https://cmake.org/download/ 下载安装

### 安装步骤

#### 1. 安装 PC 调试依赖

```bash
# 进入项目目录
cd SmartDiabetesAssistant

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip

# 安装核心依赖（Windows）
pip install -r requirements-pc.txt
```

#### 2. 解决常见问题

**问题 1: TTS (Coqui TTS) 安装失败**

```bash
# 解决方案: 使用系统TTS代替
# 项目默认使用 pyttsx3（系统TTS），无需安装 Coqui TTS

# 如果确实需要 Coqui TTS:
# 1. Windows 需要先安装 Visual Studio C++ Build Tools
# 2. 然后运行: pip install TTS
# 3. 首次使用会下载模型（约50MB），确保网络畅通

# 推荐方案: 直接使用 pyttsx3
pip install pyttsx3
```

**问题 2: pyaudio 安装失败**

```bash
# 方案 A: 使用预编译的 wheel 文件
pip install pipwin
pipwin install pyaudio

# 方案 B: 手动下载 wheel 文件
# 访问 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# 下载对应版本的 .whl 文件
pip install path\to\pyaudio‑xxx.whl
```

**问题 3: OpenCV 安装失败**

```bash
# 使用预编译的 wheel 文件
pip install opencv-python‑python
```

**问题 4: mmpose/mmdet 安装失败**

```bash
# 先安装 openmim
pip install openmim

# 然后使用 mim 安装
mim install mmpose
mim install mmdet

# 或者跳过这些包，仅使用 YOLOv8
pip install ultralytics
```

**问题 5: Python 3.14 兼容性问题**

```bash
# 建议降级到 Python 3.10 或 3.11
# 从 https://www.python.org/downloads/ 下载安装

# 重新创建虚拟环境
python3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements-pc.txt
```

### 快速测试安装

```bash
# 安装完成后测试
python -c "import cv2; print('OpenCV OK')"
python -c "import torch; print('PyTorch OK')"
python -c "import onnxruntime; print('ONNX Runtime OK')"

# 测试摄像头
python scripts/test_camera.py
```

---

## macOS 安装

### 前置要求

1. **Homebrew**: https://brew.sh/
2. **Xcode Command Line Tools**: `xcode-select --install`

### 安装步骤

```bash
# 安装 Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3.10
brew install python@3.10

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements-pc.txt

# 安装 PortAudio（用于 pyaudio）
brew install portaudio

# 安装 pyaudio
pip install pyaudio
```

---

## Linux (Ubuntu) 安装

### 安装步骤

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
sudo apt install -y python3.10 python3.10-venv python3-pip
sudo apt install -y build-essential cmake git
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y portaudio19-dev python3-pyaudio

# 创建虚拟环境
python3.10 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements-pc.txt
```

---

## NVIDIA Jetson Orin Nano 安装

### 前置要求

- JetPack 5.x 或更高版本
- Python 3.8+（系统自带）

### 安装步骤

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Jetson 专用依赖
pip install -r requirements-jetson.txt

# 验证 TensorRT
python -c "import tensorrt; print('TensorRT OK')"
```

---

## Raspberry Pi 5 安装

### 前置要求

- Raspberry Pi OS 64-bit
- Python 3.9+（系统自带）

### 安装步骤

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
sudo apt install -y python3-dev python3-pip
sudo apt install -y build-essential cmake
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y portaudio19-dev python3-pyaudio
sudo apt install -y python3-libcamera

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装 Pi 专用依赖
pip install -r requirements-pi.txt
```

---

## 验证安装

运行以下命令验证安装是否成功：

```bash
# 激活虚拟环境后
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import onnxruntime; print('ONNX Runtime: OK')"
python -c "import langgraph; print('LangGraph: OK')"

# 测试摄像头
python scripts/test_camera.py

# 运行快速启动演示
python scripts/quick_start.py
```

---

## 常见问题解决

### Q1: pip install 速度慢

**解决方案**: 使用国内镜像源

```bash
# 清华源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements-pc.txt

# 或永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 编译错误 (Microsoft Visual C++ 14.0 is required)

**解决方案**: 安装 Visual Studio Build Tools

1. 下载 Visual Studio Installer
2. 安装 "Desktop C++" 工作负载
3. 重新运行 pip install

### Q3: OpenSSL 相关错误

**解决方案**: 使用预编译的 wheel 文件

```bash
pip install pipwin
pipwin install <package_name>
```

### Q4: 内存不足错误

**解决方案**: 减少并行编译数量

```bash
pip install --no-binary :all: <package_name>
```

### Q5: 权限错误

**解决方案**: 使用用户安装模式

```bash
pip install --user -r requirements-pc.txt
```

---

## 最小化安装（仅核心功能）

如果完整安装遇到问题，可以先安装最小依赖：

```bash
# 仅安装核心依赖
pip install langchain langgraph
pip install pyyaml loguru
pip install opencv-python numpy
```

然后根据需要逐步添加其他依赖。

---

## 卸载

如果需要完全卸载：

```bash
# 退出虚拟环境
deactivate

# 删除虚拟环境
rm -rf venv

# 或 Windows
rmdir /s venv
```

---

## 获取帮助

如果遇到其他问题：

1. 查看错误日志
2. 检查 Python 版本兼容性
3. 访问项目 Issues 页面
4. 查阅相关文档

**建议**: 对于 PC 端开发，建议使用 Python 3.10 以获得最佳兼容性。

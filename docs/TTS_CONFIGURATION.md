# TTS语音合成配置说明

## 概述

系统支持两种TTS引擎，默认优先使用系统TTS（pyttsx3）。

## TTS引擎对比

### pyttsx3（系统TTS）- 推荐用于开发

**优点:**
- ✅ 开箱即用，无需额外安装
- ✅ 无需下载模型
- ✅ 启动速度快
- ✅ 跨平台兼容（Windows/macOS/Linux）
- ✅ 无网络依赖
- ✅ 自动选择系统语音

**缺点:**
- ⚠️ 语音质量取决于操作系统
- ⚠️ 情感表达有限

**适用场景:**
- PC端开发调试
- 快速原型验证
- 对语音质量要求不高的场景

**安装:**
```bash
pip install pyttsx3
```

### Coqui TTS - 推荐用于生产

**优点:**
- ✅ 语音自然流畅
- ✅ 支持多语言和方言
- ✅ 支持语音克隆
- ✅ 情感表达丰富
- ✅ 可定制化强

**缺点:**
- ⚠️ 需要下载模型（约50MB）
- ⚠️ Windows安装可能需要额外配置
- ⚠️ 首次使用需要网络
- ⚠️ 推理速度较慢

**适用场景:**
- 生产环境部署
- 需要高质量语音
- 需要语音克隆功能
- 边端设备（Jetson/Raspberry Pi）

**安装:**
```bash
# Windows
pip install TTS

# Linux
pip install TTS

# 可能需要先安装依赖
# Windows: Visual Studio C++ Build Tools
# Linux: build-essential, cmake
```

## 配置文件

在 `config/model_config.yaml` 中配置TTS:

```yaml
tts:
  # TTS引擎选择
  engine: "pyttsx3"  # "pyttsx3" 或 "coqui"

  # Coqui TTS配置（仅当engine="coqui"时使用）
  coqui_model_path: "tts_models/multilingual/multi-dataset/your_tts"
  language: "zh-CN"

  # pyttsx3配置（系统TTS，默认）
  pyttsx3:
    auto_select_chinese_voice: true  # 自动选择中文语音
    default_rate: 150  # 默认语速
    default_volume: 1.0  # 默认音量 (0.0-1.0)
```

## 使用示例

### 方式1: 使用默认配置（pyttsx3）

```python
from src.agents.tts_agent import TTSAgent

# 自动使用配置文件中的引擎
agent = TTSAgent()

# 播放语音
feedback = {
    "message": "智能糖尿病助手启动",
    "urgency": "low",
    "delay": 0
}
await agent.speak(feedback)
```

### 方式2: 强制使用pyttsx3

```python
# 创建临时配置
import tempfile
import yaml

config = {
    "tts": {
        "engine": "pyttsx3",
        "pyttsx3": {
            "auto_select_chinese_voice": True,
            "default_rate": 150,
            "default_volume": 1.0
        }
    }
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    yaml.dump(config, f)
    config_path = f.name

agent = TTSAgent(config_path=config_path)
```

### 方式3: 使用Coqui TTS

```python
# 配置使用Coqui TTS
config = {
    "tts": {
        "engine": "coqui",
        "coqui_model_path": "tts_models/multilingual/multi-dataset/your_tts",
        "language": "zh-CN"
    }
}

with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    yaml.dump(config, f)
    config_path = f.name

agent = TTSAgent(config_path=config_path)
```

## 紧急程度设置

系统支持三种紧急程度，会自动调整语音语速：

| 紧急程度 | 语速 | 使用场景 |
|---------|------|----------|
| `low` | 0.8x | 常规提示、完成确认 |
| `medium` | 1.0x | 正常提示、操作引导 |
| `high` | 1.3x | 紧急警告、错误提示 |

```python
# 低紧急度（温和提示）
await agent.speak({
    "message": "注射完成，请按压注射部位",
    "urgency": "low"
})

# 中紧急度（正常提示）
await agent.speak({
    "message": "请开始注射操作",
    "urgency": "medium"
})

# 高紧急度（紧急警告）
await agent.speak({
    "message": "注射速度过快，请立即减速",
    "urgency": "high"
})
```

## 故障排查

### pyttsx3无法播放

**症状**: 没有语音输出

**解决方案**:
1. 检查系统音量设置
2. 确认音频输出设备已连接
3. Windows: 检查语音设置中的默认输出设备
4. Linux: 安装 `alsa-utils`
5. macOS: 检查系统声音设置

### Coqui TTS加载失败

**症状**: 提示"TTS模型加载失败"

**解决方案**:
1. 检查网络连接（首次使用需要下载模型）
2. 确认已安装 TTS 包: `pip install TTS`
3. Windows: 安装 Visual Studio C++ Build Tools
4. 降级到 pyttsx3: 设置 `engine: "pyttsx3"`

### 中文语音问题

**症状**: 播放的是英文语音

**解决方案**:
1. Windows: 确保安装了中文语音包
   - 设置 → 时间和语言 → 语言 → 添加中文语言
2. 使用 Coqui TTS（原生支持中文）
3. 配置中设置 `auto_select_chinese_voice: true`

## 性能对比

| 指标 | pyttsx3 | Coqui TTS |
|------|---------|-----------|
| 启动时间 | ~100ms | ~2s（首次） |
| 首词延迟 | ~50ms | ~500ms |
| 内存占用 | ~10MB | ~200MB |
| 语音质量 | 3.0/5.0 | 4.2/5.0 |
| 离线工作 | ✅ | ✅（首次下载后） |

## 最佳实践

1. **开发阶段**: 使用 pyttsx3
   - 快速迭代
   - 无需等待模型下载
   - 便于调试

2. **测试阶段**: 使用 pyttsx3
   - 验证功能逻辑
   - 测试不同场景

3. **生产部署**: 根据需求选择
   - PC端: pyttsx3（够用）
   - 边端设备: Coqui TTS（更自然）
   - 语音克隆: 必须使用 Coqui TTS

4. **混合使用**:
   ```python
   # 默认使用pyttsx3
   agent = TTSAgent()

   # 重要提示使用Coqui TTS
   if is_critical_message:
       # 切换到Coqui TTS
       critical_agent = TTSAgent(config_path="config/coqui_tts.yaml")
       await critical_agent.speak(feedback)
   ```

## 更新日志

- **2026-01-11**: 默认引擎更改为 pyttsx3
- **2026-01-11**: 添加引擎自动降级机制
- **2026-01-11**: 支持配置文件选择引擎

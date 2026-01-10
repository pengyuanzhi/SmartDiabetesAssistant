# 安全规范

本文档定义项目必须遵守的安全要求，特别关注医疗数据和隐私保护。

## 数据安全

### 1. 医疗数据处理

#### 数据匿名化

所有医疗数据必须匿名化处理：

```python
def anonymize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    匿名化患者数据

    移除或哈希所有可识别个人身份的信息(PII)

    Args:
        data: 原始患者数据

    Returns:
        匿名化后的数据
    """
    import hashlib

    # 哈希敏感字段
    sensitive_fields = ["name", "id_card", "phone", "email"]

    anonymized = data.copy()

    for field in sensitive_fields:
        if field in anonymized:
            # 使用SHA-256哈希
            value = str(anonymized[field]).encode()
            hashed = hashlib.sha256(value).hexdigest()
            anonymized[field] = f"hashed_{hashed[:16]}"

    return anonymized
```

#### 数据加密

敏感数据必须加密存储：

```python
from cryptography.fernet import Fernet

class SecureStorage:
    """安全存储"""

    def __init__(self, key: bytes):
        """使用Fernet对称加密"""
        self.cipher = Fernet(key)

    def encrypt_data(self, data: str) -> bytes:
        """加密数据"""
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """解密数据"""
        return self.cipher.decrypt(encrypted_data).decode()

    def store_record(self, record: Dict[str, Any]) -> None:
        """加密后存储"""
        # 序列化
        json_data = json.dumps(record)

        # 加密
        encrypted = self.encrypt_data(json_data)

        # 存储
        with open("data/encrypted.dat", "wb") as f:
            f.write(encrypted)
```

### 2. 数据存储

#### 本地存储优先

所有数据必须本地存储，禁止上传云端：

```python
class LocalDatabase:
    """本地数据库"""

    def __init__(self, db_path: str):
        """
        初始化本地数据库

        Args:
            db_path: 本地文件系统路径

        Raises:
            ValueError: 如果路径是网络路径
        """
        # 验证是本地路径
        if db_path.startswith(("http://", "https://", "ftp://")):
            raise ValueError("禁止使用网络存储，必须使用本地文件系统")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 设置文件权限（仅所有者可读写）
        self.db_path.chmod(0o600)
```

#### 数据保留策略

自动清理旧数据：

```python
class DataRetentionPolicy:
    """数据保留策略"""

    MAX_RETENTION_DAYS = 90  # 最多保留90天
    MAX_VIDEO_SIZE_GB = 10   # 视频文件最大10GB

    def cleanup_old_data(self, db: DatabaseManager) -> None:
        """
        清理旧数据

        Args:
            db: 数据库管理器
        """
        logger.info(f"清理{self.MAX_RETENTION_DAYS}天前的数据")
        db.cleanup_old_data(days=self.MAX_RETENTION_DAYS)

    def check_storage_limit(self, data_dir: Path) -> None:
        """
        检查存储限制

        Args:
            data_dir: 数据目录

        Raises:
            StorageLimitExceeded: 超过存储限制
        """
        total_size = sum(
            f.stat().st_size
            for f in data_dir.rglob("*")
            if f.is_file()
        )

        total_gb = total_size / (1024**3)

        if total_gb > self.MAX_VIDEO_SIZE_GB:
            raise StorageLimitExceeded(
                f"存储空间超过限制：{total_gb:.2f}GB > {self.MAX_VIDEO_SIZE_GB}GB"
            )
```

### 3. 访问控制

#### 权限管理

```python
class AccessControl:
    """访问控制"""

    PERMISSIONS = {
        "read": 0o400,  # 只读
        "write": 0o200, # 只写
        "execute": 0o100 # 执行
    }

    def set_secure_permissions(self, file_path: Path) -> None:
        """
        设置安全文件权限

        仅所有者可读写，禁止其他用户访问

        Args:
            file_path: 文件路径
        """
        # 仅所有者可读写
        file_path.chmod(0o600)

        # 确保目录权限正确
        if file_path.is_file():
            file_path.parent.chmod(0o700)
```

#### 会话管理

```python
class SessionManager:
    """会话管理"""

    MAX_SESSION_DURATION = 3600  # 1小时
    SESSION_TIMEOUT = 300        # 5分钟无活动超时

    def __init__(self):
        """初始化会话管理器"""
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()

    async def create_session(self, user_id: str) -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID

        Returns:
            会话令牌
        """
        import secrets

        token = secrets.token_urlsafe(32)

        async with self.lock:
            self.sessions[token] = {
                "user_id": user_id,
                "created_at": time.time(),
                "last_activity": time.time()
            }

        return token

    async def validate_session(self, token: str) -> bool:
        """
        验证会话

        Args:
            token: 会话令牌

        Returns:
            是否有效
        """
        async with self.lock:
            if token not in self.sessions:
                return False

            session = self.sessions[token]

            # 检查是否超时
            if time.time() - session["last_activity"] > self.SESSION_TIMEOUT:
                del self.sessions[token]
                return False

            # 检查是否超过最大时长
            if time.time() - session["created_at"] > self.MAX_SESSION_DURATION:
                del self.sessions[token]
                return False

            # 更新活动时间
            session["last_activity"] = time.time()
            return True
```

## 网络安全

### 1. 禁止网络传输

```python
class NetworkSecurityPolicy:
    """网络安全策略"""

    BLOCKED_PROTOCOLS = ["http", "https", "ftp", "ssh", "tcp", "udp"]

    def validate_operation(self, operation: str) -> bool:
        """
        验证操作是否安全

        Args:
            operation: 操作描述

        Returns:
            是否安全

        Raises:
            SecurityError: 如果操作不安全
        """
        operation_lower = operation.lower()

        for protocol in self.BLOCKED_PROTOCOLS:
            if protocol in operation_lower:
                raise SecurityError(
                    f"禁止的网络操作: {operation}"
                )

        return True
```

### 2. USB设备限制

```python
class DeviceSecurity:
    """设备安全"""

    AUTHORIZED_DEVICES = [
        "vendor_id_1:product_id_1",  # 授权的摄像头
        "vendor_id_2:product_id_2"   # 授权的传感器
    ]

    def check_usb_device(self, device_id: str) -> bool:
        """
        检查USB设备是否授权

        Args:
            device_id: 设备ID

        Returns:
            是否授权
        """
        if device_id not in self.AUTHORIZED_DEVICES:
            logger.warning(f"未授权的USB设备: {device_id}")
            return False

        return True
```

## AI模型安全

### 1. 模型验证

```python
class ModelValidator:
    """模型验证器"""

    def validate_model(self, model_path: Path) -> bool:
        """
        验证模型文件

        检查模型签名、来源和完整性

        Args:
            model_path: 模型文件路径

        Returns:
            是否有效

        Raises:
            SecurityError: 模型不安全
        """
        # 1. 检查文件签名
        if not self._verify_signature(model_path):
            raise SecurityError("模型签名无效")

        # 2. 检查文件哈希
        if not self._verify_hash(model_path):
            raise SecurityError("模型文件已损坏")

        # 3. 检查来源
        if not self._verify_source(model_path):
            raise SecurityError("模型来源不明")

        return True

    def _verify_signature(self, model_path: Path) -> bool:
        """验证数字签名"""
        # 实现签名验证逻辑
        pass

    def _verify_hash(self, model_path: Path) -> bool:
        """验证文件哈希"""
        import hashlib

        sha256 = hashlib.sha256()
        with open(model_path, "rb") as f:
            sha256.update(f.read())

        # 与预存的哈希比较
        expected_hash = self._load_expected_hash(model_path)
        return sha256.hexdigest() == expected_hash

    def _verify_source(self, model_path: Path) -> bool:
        """验证模型来源"""
        # 检查模型是否来自可信源
        pass
```

### 2. 输入验证

```python
class InputValidator:
    """输入验证器"""

    MAX_IMAGE_SIZE = (3840, 2160)  # 4K
    MIN_IMAGE_SIZE = (320, 240)
    ALLOWED_FORMATS = [".jpg", ".jpeg", ".png"]

    def validate_image(self, image: np.ndarray) -> bool:
        """
        验证图像输入

        Args:
            image: 输入图像

        Returns:
            是否有效

        Raises:
            InvalidInputError: 输入无效
        """
        # 检查尺寸
        height, width = image.shape[:2]

        if height > self.MAX_IMAGE_SIZE[1] or width > self.MAX_IMAGE_SIZE[0]:
            raise InvalidInputError(f"图像过大: {width}x{height}")

        if height < self.MIN_IMAGE_SIZE[1] or width < self.MIN_IMAGE_SIZE[0]:
            raise InvalidInputError(f"图像过小: {width}x{height}")

        # 检查通道数
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise InvalidInputError("图像必须是3通道BGR格式")

        # 检查数据类型
        if image.dtype != np.uint8:
            raise InvalidInputError("图像必须是uint8类型")

        return True
```

## 日志安全

### 1. 敏感信息过滤

```python
class SecureLogger:
    """安全日志记录器"""

    # 敏感字段模式
    SENSITIVE_PATTERNS = [
        r"password\s*=\s*\S+",
        r"token\s*=\s*\S+",
        r"key\s*=\s*\S+",
        r"\d{15,19}",  # 身份证号
        r"\d{11}",     # 手机号
    ]

    def __init__(self):
        """初始化"""
        self.logger = logger
        self._compile_patterns()

    def _compile_patterns(self):
        """编译正则表达式模式"""
        import re

        self.patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.SENSITIVE_PATTERNS
        ]

    def sanitize(self, message: str) -> str:
        """
        清理日志消息

        移除敏感信息

        Args:
            message: 原始消息

        Returns:
            清理后的消息
        """
        sanitized = message

        for pattern in self.patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)

        return sanitized

    def info(self, message: str, **kwargs):
        """记录INFO日志"""
        sanitized = self.sanitize(message)
        self.logger.info(sanitized, **kwargs)

    def error(self, message: str, **kwargs):
        """记录ERROR日志"""
        sanitized = self.sanitize(message)
        self.logger.error(sanitized, **kwargs)
```

### 2. 日志级别控制

```python
# 生产环境使用WARNING或更高级别
LOG_LEVELS = {
    "development": "DEBUG",
    "testing": "INFO",
    "production": "WARNING"
}

def setup_logger(environment: str):
    """
    配置日志记录器

    Args:
        environment: 环境名称
    """
    level = LOG_LEVELS.get(environment, "INFO")

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )
```

## 代码安全

### 1. 禁止危险的Python特性

```python
# 禁止使用eval
def dangerous_function(user_input: str):
    # 错误：不安全
    result = eval(user_input)

    # 正确：使用ast.literal_eval
    import ast
    result = ast.literal_eval(user_input)

# 禁止使用exec
def load_module(code: str):
    # 错误：不安全
    exec(code)

    # 正确：使用import
    import importlib
    module = importlib.import_module(module_name)

# 禁止使用pickle加载不可信数据
def load_data(data: bytes):
    # 错误：不安全
    import pickle
    obj = pickle.loads(data)

    # 正确：使用JSON
    import json
    obj = json.loads(data)
```

### 2. SQL注入防护

```python
def safe_query(user_id: str):
    """安全的数据库查询"""

    # 正确：使用参数化查询
    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    # 错误：直接拼接字符串（SQL注入风险）
    # cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
```

### 3. 路径遍历防护

```python
class SecurePath:
    """安全路径处理"""

    ALLOWED_DIRS = [
        Path("/data/videos"),
        Path("/data/images")
    ]

    def validate_path(self, file_path: Path) -> bool:
        """
        验证路径安全

        防止路径遍历攻击

        Args:
            file_path: 文件路径

        Returns:
            是否安全

        Raises:
            SecurityError: 路径不安全
        """
        # 解析为绝对路径
        absolute = file_path.resolve()

        # 检查是否在允许的目录内
        for allowed_dir in self.ALLOWED_DIRS:
            try:
                absolute.relative_to(allowed_dir)
                return True
            except ValueError:
                continue

        raise SecurityError(f"路径不在允许的目录内: {absolute}")
```

## 合规性

### 1. 医疗数据合规

```python
class ComplianceChecker:
    """合规性检查器"""

    def check_hipaa_compliance(self, data: Dict[str, Any]) -> bool:
        """
        检查HIPAA合规性

        Args:
            data: 待检查的数据

        Returns:
            是否合规

        Raises:
            ComplianceError: 不合规
        """
        # 检查是否有未加密的PHI（受保护健康信息）
        phi_fields = ["name", "ssn", "medical_record"]

        for field in phi_fields:
            if field in data and not self._is_encrypted(data[field]):
                raise ComplianceError(
                    f"PHI字段未加密: {field}"
                )

        return True

    def check_gdpr_compliance(self, consent: Dict[str, Any]) -> bool:
        """
        检查GDPR合规性

        Args:
            consent: 同意记录

        Returns:
            是否合规
        """
        # 检查是否有明确的用户同意
        required_fields = ["purpose", "retention", "rights"]

        for field in required_fields:
            if field not in consent:
                raise ComplianceError(
                    f"GDPR同意缺少字段: {field}"
                )

        return True
```

### 2. 审计日志

```python
class AuditLogger:
    """审计日志记录器"""

    def __init__(self, log_path: str):
        """初始化审计日志"""
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # 设置只追加权限
        self.log_path.touch()
        self.log_path.chmod(0o200)

    def log_access(self, user_id: str, resource: str, action: str):
        """
        记录访问日志

        Args:
            user_id: 用户ID（匿名化）
            resource: 访问的资源
            action: 执行的操作
        """
        import json

        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": self._anonymize(user_id),
            "resource": resource,
            "action": action,
            "ip": "127.0.0.1"  # 本地系统
        }

        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _anonymize(self, user_id: str) -> str:
        """匿名化用户ID"""
        import hashlib
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
```

## 安全检查清单

代码提交前检查：

- [ ] 所有敏感数据已加密
- [ ] 没有硬编码的密钥或密码
- [ ] 使用参数化查询
- [ ] 验证所有用户输入
- [ ] 日志中不包含敏感信息
- [ ] 文件权限设置正确
- [ ] 遵循最小权限原则
- [ ] 有适当的审计日志
- [ ] 符合HIPAA/GDPR要求
- [ ] 通过安全测试

## 事件响应

### 安全事件处理流程

```python
class SecurityIncidentResponder:
    """安全事件响应器"""

    async def handle_breach(self, incident: Dict[str, Any]):
        """
        处理安全事件

        Args:
            incident: 事件详情
        """
        # 1. 记录事件
        logger.critical(f"安全事件: {incident}")

        # 2. 隔离受影响的系统
        await self._isolate_system()

        # 3. 保留证据
        await self._preserve_evidence(incident)

        # 4. 通知相关人员
        await self._notify_stakeholders(incident)

        # 5. 启动恢复程序
        await self._initiate_recovery()
```

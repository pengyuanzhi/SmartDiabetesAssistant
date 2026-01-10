"""
模型管理器 - 统一管理所有AI模型的加载、优化和推理

功能：
1. 模型加载和初始化
2. TensorRT/TFLite优化
3. 批量推理管理
4. 模型性能监控
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml

import numpy as np


class BaseModel:
    """模型基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        self.loaded = False

    def load(self):
        """加载模型（子类实现）"""
        raise NotImplementedError

    def predict(self, input_data: np.ndarray) -> Any:
        """推理（子类实现）"""
        raise NotImplementedError

    def is_loaded(self) -> bool:
        """检查是否已加载"""
        return self.loaded


class TensorRTModel(BaseModel):
    """TensorRT模型（Jetson平台）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.engine_path = config.get("model_path")
        self.input_shape = config.get("input_shape", (1, 3, 640, 640))

    def load(self):
        """加载TensorRT引擎"""
        try:
            import tensorrt as trt
            import pycuda.driver as cuda
            import pycuda.autoinit

            # 加载引擎
            with open(self.engine_path, "rb") as f:
                runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
                self.engine = runtime.deserialize_cuda_engine(f.read())

            self.context = self.engine.create_execution_context()

            # 分配内存
            self._allocate_buffers()

            self.loaded = True
            print(f"[TensorRTModel] 模型加载成功: {self.engine_path}")

        except Exception as e:
            print(f"[TensorRTModel] 加载失败: {e}")
            self.loaded = False

    def _allocate_buffers(self):
        """分配GPU内存"""
        import pycuda.driver as cuda

        self.buffers = []
        for binding in self.engine:
            size = trt.volume(self.engine.get_binding_shape(binding)) * self.engine.max_batch_size
            dtype = trt.nptype(self.engine.get_binding_dtype(binding))

            # 分配设备内存
            device_mem = cuda.mem_alloc(size)
            self.buffers.append({
                "device": device_mem,
                "host": np.zeros(size, dtype=dtype),
                "binding": binding
            })

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """执行推理"""
        import pycuda.driver as cuda

        # 拷贝输入数据
        np.copyto(self.buffers[0]["host"], input_data.ravel())
        cuda.memcpy_htod(self.buffers[0]["device"], self.buffers[0]["host"])

        # 执行推理
        self.context.execute_v2([buf["device"] for buf in self.buffers])

        # 获取输出
        output = self.buffers[1]["host"]
        return output


class TFLiteModel(BaseModel):
    """TFLite模型（Raspberry Pi平台）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_path = config.get("model_path")

    def load(self):
        """加载TFLite模型"""
        try:
            import tflite_runtime.interpreter as tflite

            # 加载模型
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()

            # 获取输入输出详情
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            self.loaded = True
            print(f"[TFLiteModel] 模型加载成功: {self.model_path}")

        except Exception as e:
            print(f"[TFLiteModel] 加载失败: {e}")
            self.loaded = False

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """执行推理"""
        # 设置输入
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)

        # 推理
        self.interpreter.invoke()

        # 获取输出
        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        return output


class ONNXModel(BaseModel):
    """ONNX模型（通用平台）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_path = config.get("onnx_path")

    def load(self):
        """加载ONNX模型"""
        try:
            import onnxruntime as ort

            # 创建会话
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            self.session = ort.InferenceSession(
                self.model_path,
                providers=providers
            )

            self.loaded = True
            print(f"[ONNXModel] 模型加载成功: {self.model_path}")

        except Exception as e:
            print(f"[ONNXModel] 加载失败: {e}")
            self.loaded = False

    def predict(self, input_data: np.ndarray) -> np.ndarray:
        """执行推理"""
        input_name = self.session.get_inputs()[0].name
        output = self.session.run(None, {input_name: input_data})
        return output[0]


class ModelManager:
    """
    模型管理器 - 统一管理所有AI模型

    支持：
    - 延迟加载（首次使用时加载）
    - 多平台支持（TensorRT/TFLite/ONNX）
    - 批量推理
    - 性能监控
    """

    def __init__(self, config_path: str = "config/model_config.yaml"):
        """
        初始化模型管理器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)

        # 模型注册表
        self.models: Dict[str, BaseModel] = {}

        # 性能统计
        self.stats = {
            "inference_times": {},
            "inference_counts": {}
        }

        # 初始化模型配置
        self._initialize_models()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _initialize_models(self):
        """初始化模型配置"""
        platform = self.config.get("optimization", {}).get("platform", "jetson")

        # 姿态估计模型
        self.model_configs = {
            "pose_estimator": {
                "type": "TensorRTModel" if platform == "jetson" else "TFLiteModel",
                "config": self.config.get("pose_estimation", {})
            },
            "site_detector": {
                "type": "TensorRTModel" if platform == "jetson" else "TFLiteModel",
                "config": self.config.get("object_detection", {})
            },
            "flow_calculator": {
                "type": "ONNXModel",
                "config": self.config.get("optical_flow", {})
            }
        }

    def get_model(self, model_name: str) -> BaseModel:
        """
        获取模型（延迟加载）

        Args:
            model_name: 模型名称

        Returns:
            模型实例
        """
        # 如果已加载，直接返回
        if model_name in self.models and self.models[model_name].is_loaded():
            return self.models[model_name]

        # 创建并加载模型
        if model_name not in self.model_configs:
            raise ValueError(f"未知的模型: {model_name}")

        config = self.model_configs[model_name]
        model_type = config["type"]
        model_config = config["config"]

        # 创建模型实例
        model_class = globals()[model_type]
        model = model_class(model_config)

        # 加载模型
        model.load()

        if model.is_loaded():
            self.models[model_name] = model
        else:
            raise RuntimeError(f"模型加载失败: {model_name}")

        return model

    async def predict(
        self,
        model_name: str,
        input_data: np.ndarray,
        preprocess: bool = True
    ) -> Any:
        """
        执行模型推理

        Args:
            model_name: 模型名称
            input_data: 输入数据
            preprocess: 是否预处理

        Returns:
            推理结果
        """
        start_time = time.time()

        try:
            # 获取模型
            model = self.get_model(model_name)

            # 预处理
            if preprocess:
                input_data = self._preprocess_input(model_name, input_data)

            # 推理
            result = model.predict(input_data)

            # 更新统计
            inference_time = time.time() - start_time
            self._update_stats(model_name, inference_time)

            return result

        except Exception as e:
            print(f"[ModelManager] 推理错误 ({model_name}): {e}")
            return None

    async def batch_predict(
        self,
        model_name: str,
        input_batch: List[np.ndarray]
    ) -> List[Any]:
        """
        批量推理

        Args:
            model_name: 模型名称
            input_batch: 输入批次

        Returns:
            推理结果列表
        """
        results = []

        for input_data in input_batch:
            result = await self.predict(model_name, input_data)
            results.append(result)

        return results

    def _preprocess_input(
        self,
        model_name: str,
        input_data: np.ndarray
    ) -> np.ndarray:
        """
        输入预处理

        Args:
            model_name: 模型名称
            input_data: 原始输入

        Returns:
            预处理后的输入
        """
        # 根据模型类型进行预处理
        if model_name == "pose_estimator":
            # 姿态估计：调整大小到256x256
            input_data = cv2.resize(input_data, (256, 256))
            input_data = input_data.transpose(2, 0, 1)  # HWC -> CHW
            input_data = input_data.astype(np.float32) / 255.0
            input_data = np.expand_dims(input_data, axis=0)  # 添加batch维度

        elif model_name == "site_detector":
            # 目标检测：调整大小到640x640
            input_data = cv2.resize(input_data, (640, 640))
            input_data = input_data.transpose(2, 0, 1)
            input_data = input_data.astype(np.float32) / 255.0
            input_data = np.expand_dims(input_data, axis=0)

        return input_data

    def _update_stats(self, model_name: str, inference_time: float):
        """更新性能统计"""
        if model_name not in self.stats["inference_times"]:
            self.stats["inference_times"][model_name] = []
            self.stats["inference_counts"][model_name] = 0

        self.stats["inference_times"][model_name].append(inference_time)
        self.stats["inference_counts"][model_name] += 1

        # 保持最近100次记录
        if len(self.stats["inference_times"][model_name]) > 100:
            self.stats["inference_times"][model_name].pop(0)

    def get_stats(self, model_name: str = None) -> Dict[str, Any]:
        """
        获取性能统计

        Args:
            model_name: 模型名称（None表示全部）

        Returns:
            统计数据
        """
        if model_name:
            times = self.stats["inference_times"].get(model_name, [])
            count = self.stats["inference_counts"].get(model_name, 0)

            return {
                "model": model_name,
                "inference_count": count,
                "avg_time_ms": np.mean(times) * 1000 if times else 0,
                "min_time_ms": np.min(times) * 1000 if times else 0,
                "max_time_ms": np.max(times) * 1000 if times else 0
            }
        else:
            return {
                name: self.get_stats(name)
                for name in self.stats["inference_counts"].keys()
            }

    def unload_model(self, model_name: str):
        """
        卸载模型释放内存

        Args:
            model_name: 模型名称
        """
        if model_name in self.models:
            del self.models[model_name]
            print(f"[ModelManager] 模型已卸载: {model_name}")

    def unload_all(self):
        """卸载所有模型"""
        for model_name in list(self.models.keys()):
            self.unload_model(model_name)

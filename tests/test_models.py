"""
模型管理器单元测试
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelManager:
    """模型管理器测试类"""

    @pytest.fixture
    def model_config(self):
        """模型配置 fixture"""
        return {
            "pose_estimation": {
                "model_name": "rtmpose_lite",
                "model_path": "models/rtmpose_lite.onnx",
                "input_resolution": [256, 256],
                "quantization": "INT8"
            },
            "object_detection": {
                "model_name": "yolov8n",
                "model_path": "models/yolov8n.onnx",
                "input_resolution": [640, 640],
                "confidence_threshold": 0.5
            }
        }

    def test_model_manager_import(self):
        """测试模型管理器导入"""
        try:
            from src.models.model_manager import ModelManager
            assert ModelManager is not None
        except ImportError:
            pytest.skip("ModelManager模块未实现")

    def test_model_manager_init(self, model_config):
        """测试模型管理器初始化"""
        try:
            from src.models.model_manager import ModelManager

            manager = ModelManager(config=model_config)
            assert manager is not None
            assert manager.config == model_config

        except ImportError:
            pytest.skip("ModelManager模块未实现")

    def test_model_load_not_found(self, model_config, tmp_path):
        """测试加载不存在的模型"""
        try:
            from src.models.model_manager import ModelManager

            # 修改配置指向不存在的模型
            config = model_config.copy()
            config["pose_estimation"]["model_path"] = str(tmp_path / "nonexistent.onnx")

            manager = ModelManager(config=config)

            # 尝试加载模型应该失败
            with pytest.raises(FileNotFoundError):
                manager.load_model("pose_estimation")

        except ImportError:
            pytest.skip("ModelManager模块未实现")

    def test_onnx_runtime_available(self):
        """测试ONNX Runtime是否可用"""
        try:
            import onnxruntime as ort
            assert ort.__version__ is not None

            # 检查可用的执行提供者
            providers = ort.get_available_providers()
            assert len(providers) > 0

        except ImportError:
            pytest.skip("ONNX Runtime未安装")

    def test_numpy_available(self):
        """测试NumPy是否可用"""
        import numpy as np
        assert np.__version__ is not None

    def test_cv2_available(self):
        """测试OpenCV是否可用"""
        import cv2
        assert cv2.__version__ is not None


class TestModelInference:
    """模型推理测试"""

    @pytest.fixture
    def dummy_input(self):
        """创建虚拟输入"""
        # 创建一个随机的RGB图像 (256x256)
        return np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

    def test_image_preprocessing(self, dummy_input):
        """测试图像预处理"""
        # 模拟预处理流程
        assert dummy_input.shape == (256, 256, 3)
        assert dummy_input.dtype == np.uint8

        # 转换为float32并归一化
        processed = dummy_input.astype(np.float32) / 255.0
        assert processed.dtype == np.float32
        assert processed.max() <= 1.0
        assert processed.min() >= 0.0

    def test_image_resize(self, dummy_input):
        """测试图像调整大小"""
        import cv2

        # 调整到不同尺寸
        target_sizes = [
            (640, 640),  # YOLO输入
            (256, 256),  # RTMPose输入
            (1280, 720),  # 原始摄像头分辨率
        ]

        for target_size in target_sizes:
            resized = cv2.resize(dummy_input, target_size)
            assert resized.shape[:2] == target_size
            assert resized.shape[2] == 3  # 保持3通道

    def test_batch_processing(self):
        """测试批量处理"""
        # 创建批次图像
        batch_size = 4
        batch = np.random.randint(0, 255, (batch_size, 256, 256, 3), dtype=np.uint8)

        assert batch.shape[0] == batch_size
        assert len(batch.shape) == 4  # 批次维度

        # 逐个处理
        for i in range(batch_size):
            img = batch[i]
            assert img.shape == (256, 256, 3)


class TestModelPerformance:
    """模型性能测试"""

    def test_inference_speed_simulation(self):
        """模拟推理速度测试"""
        import time

        # 模拟图像
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

        # 模拟推理过程（简单的图像处理）
        iterations = 10
        times = []

        for _ in range(iterations):
            start = time.time()

            # 模拟一些计算
            result = dummy_image.astype(np.float32) / 255.0
            result = result.mean()

            end = time.time()
            times.append(end - start)

        # 计算统计信息
        avg_time = sum(times) / len(times)
        avg_fps = 1.0 / avg_time if avg_time > 0 else 0

        assert avg_time < 1.0  # 每次处理应该<1秒
        assert avg_fps > 0

    def test_memory_usage(self):
        """测试内存使用"""
        import sys

        # 创建大型张量
        large_tensor = np.zeros((1000, 1000, 3), dtype=np.float32)

        # 获取内存大小
        memory_size = large_tensor.nbytes
        memory_mb = memory_size / (1024 * 1024)

        # 应该大约12MB
        assert 10 < memory_mb < 15

        # 删除张量释放内存
        del large_tensor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

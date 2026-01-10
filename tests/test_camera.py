"""
摄像头单元测试
"""

import pytest
import cv2
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCamera:
    """摄像头测试类"""

    @pytest.fixture
    def camera_id(self):
        """摄像头ID fixture"""
        return 0

    @pytest.fixture
    def test_frame_path(self, tmp_path):
        """测试帧路径 fixture"""
        return tmp_path / "test_frame.jpg"

    def test_camera_import(self):
        """测试摄像头模块导入"""
        try:
            from src.hardware.camera import Camera
            assert Camera is not None
        except ImportError:
            pytest.skip("Camera模块未实现")

    def test_opencv_available(self):
        """测试OpenCV是否可用"""
        assert cv2.__version__ is not None
        assert len(cv2.__version__) > 0

    def test_camera_open(self, camera_id):
        """测试摄像头打开"""
        import platform

        # Windows: 使用DirectShow后端
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(camera_id)

        try:
            is_opened = cap.isOpened()
            # 注意：如果实际没有摄像头，这个测试会失败
            # 在CI环境中应该skip
            if not is_opened:
                pytest.skip(f"摄像头 {camera_id} 不可用")
            assert is_opened is True
        finally:
            cap.release()

    def test_camera_capture_frame(self, camera_id, test_frame_path):
        """测试摄像头捕获帧"""
        import platform

        # Windows: 使用DirectShow后端
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(camera_id)

        try:
            if not cap.isOpened():
                pytest.skip(f"摄像头 {camera_id} 不可用")

            ret, frame = cap.read()

            if not ret or frame is None:
                pytest.skip("无法读取帧")

            # 验证帧属性
            assert frame is not None
            assert len(frame.shape) == 3  # BGR格式
            assert frame.shape[2] == 3  # 3通道
            assert frame.shape[0] > 0  # 高度>0
            assert frame.shape[1] > 0  # 宽度>0

            # 保存测试帧
            cv2.imwrite(str(test_frame_path), frame)
            assert test_frame_path.exists()

        finally:
            cap.release()

    def test_camera_properties(self, camera_id):
        """测试摄像头属性获取"""
        import platform

        # Windows: 使用DirectShow后端
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(camera_id)

        try:
            if not cap.isOpened():
                pytest.skip(f"摄像头 {camera_id} 不可用")

            # 获取摄像头属性
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            # 验证属性
            assert width > 0
            assert height > 0
            assert fps >= 0

        finally:
            cap.release()

    @pytest.mark.skipif(
        sys.platform == "linux",
        reason="Linux CI环境可能没有摄像头"
    )
    def test_camera_multiple_frames(self, camera_id):
        """测试连续读取多帧"""
        import platform
        import time

        # Windows: 使用DirectShow后端
        if platform.system() == "Windows":
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(camera_id)

        try:
            if not cap.isOpened():
                pytest.skip(f"摄像头 {camera_id} 不可用")

            frame_count = 0
            start_time = time.time()
            test_duration = 1.0  # 测试1秒

            while time.time() - start_time < test_duration:
                ret, frame = cap.read()
                if ret and frame is not None:
                    frame_count += 1
                else:
                    break

            # 验证读取了至少一些帧
            assert frame_count > 0

            # 计算实际帧率
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            assert fps > 0

        finally:
            cap.release()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# src/hardware/mock_camera.py
class MockCamera:
    def capture(self):
        print("MOCK: taking picture")
        return "mock_image"

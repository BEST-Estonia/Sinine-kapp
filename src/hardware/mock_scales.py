# src/hardware/mock_scales.py
import random
class MockScale:
    def __init__(self, level="unknown"):
        self.level = level
    def read_weight(self):
        # return a mock weight in kg
        return round(random.uniform(0.5, 5.0), 2)

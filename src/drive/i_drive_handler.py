from abc import ABC, abstractmethod
from farm_ng.canbus.canbus_pb2 import Twist2d

class IDriveHandler(ABC):
    @abstractmethod
    def send_speed(self,twist : Twist2d):
        """sends twist"""
        pass
    @abstractmethod
    def set_speed(self):
        """sets speed"""
        pass
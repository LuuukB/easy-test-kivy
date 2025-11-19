from abc import ABC, abstractmethod
class IDriveHandler(ABC):
    @abstractmethod
    def send_speed(self,twist : Twist2d):
        """sends twist"""
        pass
    @abstractmethod
    def set_speed(self):
        """sets speed"""
        pass
from abc import ABC, abstractmethod
from farm_ng.canbus.canbus_pb2 import Twist2d

class ICanHandler(ABC):
    @abstractmethod
    async def start(self):
        """Start listening on all relevant topics"""

    @abstractmethod
    def register_callback(self, destination: str, callback):
        """Callback voor een topic"""

    @abstractmethod
    async def send_twist(self, message : Twist2d):
        """Stuur een Protobuf message naar een topic"""
    @abstractmethod
    async def send_to_microcontroller(self, destination, message):
        """Stuur een Protobuf message naar een topic"""

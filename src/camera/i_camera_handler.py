from abc import ABC, abstractmethod

class ICameraHandler(ABC):
    @abstractmethod
    def start(self):
        pass
    @abstractmethod
    def get_frame(self):
        pass
    @abstractmethod
    def stop(self):
        pass
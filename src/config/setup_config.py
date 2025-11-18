from factory.camera_factory import CameraFactory
from factory.can_bus_factory import CanBusFactory
class SetupConfig:
    def __init__(self):
        self.cameras = []
        self.robot_online = True
        self.check_robot_status()
        self.camera_factory = CameraFactory()
        self.can_bus_factory = CanBusFactory()

    def initialize(self):
        if self.robot_online:
            #can = self.can_bus_factory.create_online("can")
            self.camera_factory.add_camera_online("oak0")
            print("add camera online")
            self.camera_factory.start_all()
            can = None
            self.cameras.append(self.camera_factory.get_camera("oak0"))
            return self.cameras, can
        else:
            self.camera_factory.add_camera_offline("video")
            self.cameras.append(self.camera_factory.get_camera("video"))
            can = self.can_bus_factory.create_offline()
            self.camera_factory.start_all()
            return self.cameras, can

    def deinitialize(self):
        self.camera_factory.stop_all()
        #self.can_bus_factory

    def check_robot_status(self):
        #check robot status
        self.robot_online = True
        return self.robot_online





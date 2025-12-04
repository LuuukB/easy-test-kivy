from factory.camera_factory import CameraFactory
from factory.can_bus_factory import CanBusFactory
from factory.drive_factory import DriveFactory
from typing import List

class SetupConfig:
    def __init__(self):
        self.cameras = []
        self.robot_online = False
        self.check_robot_status()
        self.camera_factory = CameraFactory()
        self.can_bus_factory = CanBusFactory()
        self.drive_factory = DriveFactory()

    async def initialize(self):
        if self.robot_online:
            can = None
            #can = self.can_bus_factory.create_online()
            self.camera_factory.add_camera_online("oak0")
            print("add camera online")
            await self.camera_factory.start_all()
            can_handler = None
            #drive_handler = self.drive_factory.create_online()
            drive_handler = None
            self.cameras.append(self.camera_factory.get_camera("oak0"))
            return self.cameras, can, drive_handler
        else:
            self.camera_factory.add_camera_offline("video")
            self.cameras.append(self.camera_factory.get_camera("video"))
            #can_handler = self.can_bus_factory.create_offline()
            self.camera_factory.start_all()
            drive_handler = None
            can_handler = None
            return self.cameras, can_handler, drive_handler

    def deinitialize(self):
        self.camera_factory.stop_all()
        #self.can_bus_factory

    def check_robot_status(self):
        #check robot status
        self.robot_online = True
        return self.robot_online


from factory.camera_factory import CameraFactory
from camera.i_camera_handler import ICameraHandler


class Setup:
    def __init__(self):
        self.robot_online = self.check_status()
        self.camera_factory = CameraFactory()
        self.cameras : List[ICameraHandler]= []
        self.camera_handler = None

    async def initialize(self, camera_names : List[str] = None):
        """"
        camera_names must be the names of the corresponding camera in service_config.json
        """
        if self.robot_online:
            #setup camera's
            self.cameras = [self.camera_factory.add_camera_online(name) for name in camera_names]
            await self.camera_factory.start_all()

            #setup canbus

            return self.cameras
        else:
            #setup mock camera(s)
            self.cameras = [self.camera_factory.add_camera_offline() for _ in range(len(camera_names))]

            #setup mock canbus

            return self.cameras

    def check_status(self):
        return False





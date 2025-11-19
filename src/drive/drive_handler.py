from drive.i_drive_handler import IDriveHandler

from pathlib import Path

from farm_ng.canbus.canbus_pb2 import Twist2d
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file

class DriveHandler(IDriveHandler):
    def __init__(self):
        service_config_path = Path() / 'service_config.json'
        config = proto_from_json_file(service_config_path, EventServiceConfigList())
        self.max_speed = 0.05
        self.max_angular_rate = 0.05

        for cfg in config.configs:
            if cfg.name == "canbus":
                self.client = EventClient(cfg)
                print("canbus started")

    async def send_speed(self, twist: Twist2d):
        await self.client.request_reply("twist", twist)
        await asyncio.sleep(0.02)

    async def set_speed(self, linear_velocity_x, angular_velocity):
        twist = Twist2d()
        twist.linear_velocity_x = self.max_speed * linear_velocity_x
        twist.angular_velocity = self.max_angular_rate * angular_velocity
        await self.send_speed(twist)
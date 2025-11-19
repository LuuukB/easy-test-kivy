from drive.i_drive_handler import IDriveHandler
import asyncio
from pathlib import Path

from farm_ng.canbus.canbus_pb2 import Twist2d
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.events_file_reader import proto_from_json_file
from farm_ng.core.events_file_reader import payload_to_protobuf
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.canbus.packet import AmigaRpdo1
from farm_ng.canbus.packet import AmigaTpdo1
from farm_ng.canbus.packet import AmigaControlState
from farm_ng.core.uri_pb2 import Uri


class DriveHandler(IDriveHandler):
    def __init__(self):
        service_config_path = Path() / 'service_config.json'
        config = proto_from_json_file(service_config_path, EventServiceConfigList())
        self.max_speed = 0.1
        self.max_angular_rate = 0.1

        for cfg in config.configs:
            if cfg.name == "canbus":
                self.client = EventClient(cfg)
                print("canbus started")

    async def send_speed(self, twist: Twist2d):
        await self.client.request_reply("twist", twist)


    async def set_speed(self, linear_velocity_x, angular_velocity):
            twist = Twist2d()
            twist.linear_velocity_x = self.max_speed * linear_velocity_x
            twist.angular_velocity = self.max_angular_rate * angular_velocity
            await self.send_speed(twist)

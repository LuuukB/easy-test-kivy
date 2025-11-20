import asyncio
from pathlib import Path
from canbus.i_can_handler import ICanHandler
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.event_service_pb2 import EventServiceConfig
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage
from farm_ng.core.uri_pb2 import Uri
from farm_ng.canbus.canbus_pb2 import Twist2d
from farm_ng.core.events_file_reader import proto_from_json_file

class CanHandler(ICanHandler):
    def __init__(self):
        service_config_path = Path() / 'service_config.json'
        print("canbus")
        config = proto_from_json_file(service_config_path, EventServiceConfigList())
        for cfg in config.configs:
            if cfg.name == "canbus":
                self.client = EventClient(cfg)
                print("canbus started")
                self.callbacks = {}
                self._listening = False

    async def start(self):
        if not self._listening:
            asyncio.create_task(self._listen("/twist"))
            asyncio.create_task(self._listen("/can_message"))
            self._listening = True

    def register_callback(self, destination, callback):
        if destination not in self.callbacks:
            self.callbacks[destination] = []
        self.callbacks[destination].append(callback)

    async def send_twist(self, message : Twist2d):
        await self.client.request_reply("/twist", message)

    async def set_speed(self, linear_velocity_x, angular_velocity):
        twist = Twist2d()
        twist.linear_velocity_x = self.max_speed * linear_velocity_x
        twist.angular_velocity = self.max_angular_rate * angular_velocity
        await self.send_twist(twist)

    async def send_to_microcontroller(self, message: RawCanbusMessage):
        print(f"{message}")
        print("blalblallba")
        await self.client.request_reply("/raw_messages", message)

    async def _listen(self, destination):
        req = SubscribeRequest(uri=Uri(path=destination), every_n=1)
        async for event, payload in self.client.subscribe(req, decode=True):
            msg = payload_to_protobuf(event, payload)
            if destination in self.callbacks:
                for cb in self.callbacks[destination]:
                    cb(msg)

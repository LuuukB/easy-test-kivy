import asyncio
from pathlib import Path
from canbus.i_can_handler import ICanHandler
from farm_ng.core.event_client import EventClient
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.event_service_pb2 import EventServiceConfig
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage
from farm_ng.canbus.packet import AmigaRpdo1
from farm_ng.canbus.packet import AmigaTpdo1
from farm_ng.core.uri_pb2 import Uri
from farm_ng.canbus.canbus_pb2 import Twist2d
from farm_ng.core.events_file_reader import proto_from_json_file

class CanHandler(ICanHandler):
    def __init__(self):
        service_config_path = Path() / 'service_config.json'
        print("canbus")
        config = proto_from_json_file(service_config_path, EventServiceConfigList())
        self.max_speed = 0.1
        self.max_angular_rate = 0.1

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
        uri = Uri(path="/state")
        sub = SubscribeRequest(uri=uri, every_n=1)
        async for event, payload in self.client.subscribe(sub, decode=False):
            # payload is RawCanbusMessage
            tpdo = AmigaTpdo1.from_raw_canbus_message(payload)
            if tpdo is None:
                continue

            state = tpdo.control_state
            # Kijk naar de naam van de state
            state_name = AmigaControlState.Name(state)
            print("Amiga state:", state_name)
            if state == AmigaControlState.STATE_AUTO_READY:
                print("✅ Amiga is in Auto Ready state!")
                rpdo = AmigaRpdo1()
                from farm_ng.canbus.packet import AmigaControlState
                rpdo.control_state = AmigaControlState.STATE_AUTO_ACTIVE

                msg: RawCanbusMessage = rpdo.to_raw_canbus_message()
                print("send active")
                await self.client.request_reply("/can_message", msg, decode=False)
                print("send message")
                await self.client.request_reply("/raw_message", message)
            else:
                print("❌ Amiga is NIET in Auto Ready, maar in:", state_name)


    async def _listen(self, destination):
        req = SubscribeRequest(uri=Uri(path=destination), every_n=1)
        async for event, payload in self.client.subscribe(req, decode=True):
            msg = payload_to_protobuf(event, payload)
            if destination in self.callbacks:
                for cb in self.callbacks[destination]:
                    cb(msg)

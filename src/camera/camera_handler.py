import numpy as np
import cv2
from pathlib import Path
from farm_ng_core.event_client import EventClient
from farm_ng.core.event_service_pb2 import EventServiceConfig
from farm_ng.core.event_service_pb2 import EventServiceConfigList
from farm_ng.core.event_service_pb2 import SubscribeRequest
from farm_ng.core.events_file_reader import payload_to_protobuf
from farm_ng.core.events_file_reader import proto_from_json_file
from i_camera_handler import ICameraHandler
from turbojpeg import TurboJPEG

class CameraHandler(ICameraHandler):
    def __init__(self, name : str, stream_name: str = "rgb"):

        self.service_config_path = Path() / "src" / "service_config.json"
        if not service_config_path.exists():
            raise FileNotFoundError("Service config not found!")
        self.config_name = name
        self.stream_name = stream_name
        self.client = None
        self.running = False
        self.image_decoder = TurboJPEG()

    async def start(self):

        config = proto_from_json_file(self.service_config_path,EventServiceConfigList())
        for cfg in config.configs:
            if cfg.name == self.config_name:
                self.client = EventClient(cfg)
                print("client started")
                self.running = True

    async def get_frame(self):
        if not self.client:
            raise RuntimeError("Client niet gestart")
        rate = self.client.config.subscriptions[0].every_n
        async for event, payload in self.client.subscribe(
                uri=f"{self.service_config_path}/{self.stream_name}",
                every_n=rate,
                decode=False):
            message = payload_to_protobuf(event, payload)
            img = self.image_decoder.decode_image(message.image_data)
            return img
        raise RuntimeError("Stream beëindigd")

    async def stop(self):
        self.running = False
        if self.client:
            await self.client.close()
            self.client = None
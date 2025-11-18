import asyncio
from i_can_handler import ICanHandler
from farm_ng.core.event_client import EventClient
from farm_ng.core.subscription_pb2 import SubscribeRequest
from farm_ng.core.uri_pb2 import Uri
from farm_ng.core.proto_utils import payload_to_protobuf

class CanHandler(ICanHandler):
    def __init__(self, config):
        self.client = EventClient(config)
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

    async def send(self, destination, message):
        await self.client.request_reply(destination, message)

    async def _listen(self, destination):
        req = SubscribeRequest(uri=Uri(path=destination), every_n=1)
        async for event, payload in self.client.subscribe(req, decode=True):
            msg = payload_to_protobuf(event, payload)
            if destination in self.callbacks:
                for cb in self.callbacks[destination]:
                    cb(msg)

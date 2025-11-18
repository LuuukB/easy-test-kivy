import asyncio
from can.i_can_handler import ICanHandler
from collections import defaultdict

class MockCanHandler(ICanHandler):
    def __init__(self):
        self.callbacks = defaultdict(list)
        self.queues = defaultdict(asyncio.Queue)
    async def start(self):
        for destination, queue in self.queues.items():
            asyncio.create_task(self._loop(destination, queue))

    def register_callback(self, destination, callback):
        self.callbacks[destination].append(callback)

    async def send(self, destination, message):
        print(f"send message {message} to {destination}")
        await self.queues[destination].put(message)

    async def _loop(self, destination, queue):
        while True:
            message = await queue.get()
            for cb in self.callbacks[destination]:
                cb(message)

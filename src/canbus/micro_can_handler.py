import asyncio
from farm_ng.canbus import CanBusClient
from farm_ng.canbus.packet import Frame, Packet


class AsyncCanHandler:

    def __init__(self):
        self.client = CanBusClient()
        self.send_queue = asyncio.Queue()
        self._running = False

        self.callbacks = {}
        self.special_cob_ids = set()

    # ----------------------------
    # Callbacks
    # ----------------------------
    def register_callback(self, cob_id, callback):
        self.callbacks.setdefault(cob_id, []).append(callback)

    def register_specials(self, cob_id_list):
        self.special_cob_ids.update(cob_id_list)

    # ----------------------------
    # VERZENDEN
    # ----------------------------
    async def send_packet(self, packet: Packet, cob_id: int):
        frame = Frame(
            id=cob_id,
            data=packet.to_can_data(),
            is_extended=False,
        )
        await self.send_queue.put(frame)

    async def _send_task(self):
        while self._running:
            frame = await self.send_queue.get()
            try:
                await self.client.send_frame(frame)
                print(f"[CAN] Sent: COB_ID=0x{frame.id:X}, data={frame.data}")
            except Exception as e:
                print(f"[CAN] Send error: {e}")

    # ----------------------------
    # RUN / STOP
    # ----------------------------
    async def run(self):
        self._running = True
        asyncio.create_task(self._send_task())

    def stop(self):
        self._running = False

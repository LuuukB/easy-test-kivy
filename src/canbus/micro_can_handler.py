import asyncio
import can
from farm_ng.canbus.packet import Packet # jouw base Packet class

class AsyncCanHandler:
    """
    Async CAN handler die Packets kan versturen naar een microcontroller.
    Ondersteunt COB-ID gebaseerde berichten.
    Geen callbacks nodig voor alleen verzenden.
    """
    def __init__(self, channel="can0", bustype="socketcan", bitrate=250_000):
        # python-can bus setup
        self.bus = can.Bus(channel=channel, bustype=bustype, bitrate=bitrate)

        # async send queue
        self.send_queue = asyncio.Queue()
        self._running = False

        # receiving via notifier
        #self.reader = can.AsyncBufferedReader()
        #self.notifier = can.Notifier(
        #    self.bus,
        #    [self.reader],
        #    timeout=0.01
        #)

        # optioneel: callbacks per cob_id
        self.callbacks = {}
        self.special_cob_ids = set()

    # ----------------------------
    # Callbacks registratie (optioneel)
    # ----------------------------
    def register_callback(self, cob_id, callback):
        if cob_id not in self.callbacks:
            self.callbacks[cob_id] = []
        self.callbacks[cob_id].append(callback)

    def register_specials(self, cob_id_list):
        self.special_cob_ids.update(cob_id_list)

    # ----------------------------
    # Verzenden
    # ----------------------------
    async def send_packet(self, packet: Packet, cob_id: int):
        """
        Plaatst een Packet in de send queue om naar de microcontroller te sturen
        """
        print("can on queue")
        msg = can.Message(
            arbitration_id=cob_id,
            data=packet.to_can_data(),
            is_extended_id=False
        )
        await self.send_queue.put(msg)

    async def _send_task(self):
        while self._running:
            msg = await self.send_queue.get()
            try:
                self.bus.send(msg)
                print(f"[CAN] Sent: COB_ID=0x{msg.arbitration_id:X}, data={msg.data}")
            except Exception as e:
                print(f"[CAN] Send error: {e}")
            await asyncio.sleep(0.001)

    # ----------------------------
    # Ontvangen (optioneel)
    # ----------------------------
    async def _dispatch(self, msg):
        cob_id = msg.arbitration_id

        # Specifieke callbacks
        if cob_id in self.callbacks:
            for cb in self.callbacks[cob_id]:
                cb(msg)

        # Broadcast special COB_IDs
        if cob_id in self.special_cob_ids:
            for cb_list in self.callbacks.values():
                for cb in cb_list:
                    cb(msg)

    async def _receive_task(self):
        while self._running:
            msg = await self.reader.get_message()
            if msg:
                await self._dispatch(msg)
            await asyncio.sleep(0.001)

    # ----------------------------
    # Run / stop
    # ----------------------------
    async def run(self):
        """
        Start de send/receive loop
        """
        self._running = True
        asyncio.create_task(self._send_task())


    def stop(self):
        self._running = False
        #self.notifier.stop()
        self.bus.shutdown()
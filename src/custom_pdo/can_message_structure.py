import struct
from utils.packet import Packet

class SetupPdo(Packet):
    """
    pdo used to let microcontroller know that it either
    needs to move the steppermotor (1) or give water (0)
    """
    def __init__(self, command: int = 0, amount: int = 0):
        self.command = command  # 0–255
        self.amount = amount    # 0–65535

    def to_can_data(self) -> bytes:
        """
        returns data in correct format
         - B for uint8 (command)
         - H for uint16 (amount)
        """
        return struct.pack("<BH", self.command, self.amount)

    @classmethod
    def from_can_data(cls, payload: bytes):
        """
        checks correct amount of bits and then turns message into a SetupPdo
        for easy access to the data
        """
        if len(payload) != 3:
            raise ValueError(f"Payload lengte ongeldig voor SetupPdo: {len(payload)} bytes")
        command, amount = struct.unpack("<BH", payload)
        return cls(command=command, amount=amount)

class GenericPdo(Packet):
    """
    pdo used to send generic pdo's, these are all the pdo's that only need 1 atribuut,
    cob_id is crusial to what needs to be done
    """
    def __init__(self, command: int = 0):
        self.command = command  #0-65535

    def to_can_data(self) -> bytes:
        """
         - H for uint16 (command)
        """
        return struct.pack("<H", self.command)

    @classmethod
    def from_can_data(cls, payload: bytes):
        """
        checks correct amount of bits and then turns message into a EmergencyPdo
        for easy access to the data
        """
        if len(payload) != 2:
            raise ValueError(f"Payload lengte ongeldig voor SetupPdo: {len(payload)} bytes")
        command, = struct.unpack("<H", payload)
        return cls(command=command)



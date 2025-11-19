class CanBusFactory:

    @staticmethod
    def create_online():
        from canbus.can_handler import CanHandler
        return CanHandler()

    @staticmethod
    def create_offline():
        from canbus.mock_can_handler import MockCanHandler
        return MockCanHandler()
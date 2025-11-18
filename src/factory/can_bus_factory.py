class CanBusFactory:

    @staticmethod
    def create_online():
            from can.can_handler import CanHandler
            print("can factory")
            return CanHandler()

    @staticmethod
    def create_offline():
        from can.mock_can_handler import MockCanHandler
        return MockCanHandler()
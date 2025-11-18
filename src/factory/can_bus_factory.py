class CanBusFactory:
    @staticmethod
    def create_online(config):
            from can.can_handler import CanHandler
            return CanHandler(config)

    @staticmethod
    def create_offline():
        from can.mock_can_handler import MockCanHandler
        return MockCanHandler()
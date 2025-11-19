class DriveFactory:

    @staticmethod
    def create_online():
        from drive.drive_handler import DriveHandler
        return DriveHandler()
    @staticmethod
    def create_offline():
        from drive.mock_drive_handler import MockDriveHandler
        return MockDriveHandler()
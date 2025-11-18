from camera.i_camera_handler import ICameraHandler
import cv2

class OfflineCameraHandler(ICameraHandler):
    def __init__(self, video_path: str = None):
        self.video_path = video_path
        if self.video_path is None:
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.video_path = "/home/luukb/python/video/2025_10_03_11_38_03_013649_smart-sprout.0000.rgb.mp4"
                self.cap = cv2.VideoCapture(self.video_path)
        else:
            self.cap = cv2.VideoCapture(self.video_path)

    async def start(self):
        if not self.cap.isOpened():
            raise ValueError(f"Kan video niet openen: {self.video_path}")

    async def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            # herstart video
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Kan geen frame meer ophalen uit video")
        return frame

    async def stop(self):
        self.cap.release()

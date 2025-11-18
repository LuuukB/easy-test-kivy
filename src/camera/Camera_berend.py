class CameraHandler(ICameraHandler):
    """
    Manages continuous subscriptions to the four Oak‑D camera streams.
    Allows easy access to the latest snapshot of all fours streams. :)    """
    STREAM_NAMES = ("rgb", "disparity", "left", "right")

    def __init__(self, logger: ILogger, image_converter: IImageConverter):
        self.logger = logger
        self.image_converter = image_converter

        self._image = Image(None, None, None, None)  # The latest image. Only access under lock.
        self._lock = asyncio.Lock()
        self._oak_client: Optional[
            EventClient] = None  # This is the oak0 client that will be created in the init client method :)
        self._bg_task: Optional[
            asyncio.Task] = None  # Keep a reference to the background task so we can cancel it later.

    def start_streaming(self):
        """Spawn the background task that keeps the four subscriptions alive."""
        if self._bg_task is None or self._bg_task.done():
            self._bg_task = asyncio.create_task(self._run())
            self.logger.info("Camera streaming task started")

    async def get_camera_data(self) -> Image:
        """Return a shallow copy of the latest image data."""
        async with self._lock:
            return Image(
                rgb=self._image.rgb,
                disparity=self._image.disparity,
                left=self._image.left,
                right=self._image.right,
                result=None,
            )

    def stop_streaming(self) -> None:
        """Cancel the background task."""
        if self._bg_task:
            self._bg_task.cancel()
        for t in getattr(self, "_reader_tasks", []):
            t.cancel()
        self.logger.info("Camera streaming task cancelled")

    async def _run(self) -> None:
        await self._init_client()
        if not self._oak_client:
            return

        self.generators = {
            name: self._oak_client.subscribe(
                SubscribeRequest(
                    uri={"path": f"{self._oak_client.config.name}/{name}"},
                    every_n=self._oak_client.config.subscriptions[0].every_n,
                ),
                decode=False,
            )
            for name in self.STREAM_NAMES
        }

        # Start a persistent reader for each stream (rgb, disparity, left & right).
        self._reader_tasks = [
            asyncio.create_task(self._read_loop(name, gen))
            for name, gen in self.generators.items()
        ]

        # Wait until the whole handler is cancelled.
        await asyncio.gather(*self._reader_tasks)

    async def _read_loop(self, stream_name: str, gen):
        async for event, payload in gen:
            try:
                msg = payload_to_protobuf(event, payload)
                cv_img = self.image_converter.oak_data_to_opencv(msg)

                # Set the np.ndarray data to the correct stream_name. :)
                async with self._lock:
                    setattr(self._image, stream_name, cv_img)

                self.logger.info(f"Received {stream_name} frame – shape {cv_img.shape}")
            except Exception as exc:
                self.logger.error(f"Failed to decode {stream_name}: {exc}")

    async def _init_client(self) -> None:
        """Load the service config."""

        service_config_path = Path() / "src" / "res" / "service_config_oak0.json"
        if not service_config_path.exists():
            raise FileNotFoundError("Service config not found!")

        cfg_list = proto_from_json_file(service_config_path, EventServiceConfigList())
        for cfg in cfg_list.configs:

            # If found:
            if cfg.name == "oak0":
                self._oak_client = EventClient(cfg)
                self.logger.info("oak0 client created")
                return

                # If not found:
        self.logger.error("oak0 client not found in service config")
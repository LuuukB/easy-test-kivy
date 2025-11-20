# Copyright (c) farm-ng, inc. Amiga Development Kit License, Version 0.1
import argparse
import asyncio
import os
import time
import cv2
import asyncio
from typing import List
from amiga_package import ops

# import internal libs

# Must come before kivy imports
os.environ["KIVY_NO_ARGS"] = "1"

# gui configs must go before any other kivy import
from kivy.config import Config  # noreorder # noqa: E402

Config.set("graphics", "resizable", False)
Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "800")
Config.set("graphics", "fullscreen", "false")
Config.set("input", "mouse", "mouse,disable_on_activity")
Config.set("kivy", "keyboard_mode", "systemanddock")

# kivy imports
from kivy.app import App  # noqa: E402
from kivy.lang.builder import Builder  # noqa: E402
from kivy.graphics.texture import Texture
from config.setup_config import SetupConfig
from canbus.micro_can_handler import AsyncCanHandler
from custom_pdo.can_message_structure import SetupPdo
from virtual_joystick.joystick import VirtualJoystickWidget
from farm_ng.canbus.canbus_pb2 import RawCanbusMessage



class TemplateApp(App):
    """Base class for the main Kivy app."""


    def __init__(self) -> None:
        super().__init__()
        self.can = None
        self.cameras = {}
        self.counter: int = 0
        self.canhandler : AsyncCanHandler= None
        self.drive_handler = None

        self.async_tasks: List[asyncio.Task] = []

    def build(self):
        return Builder.load_file("res/main.kv")

    def on_exit_btn(self) -> None:
        """Kills the running kivy application."""
        #self.canhandler.stop()
        App.get_running_app().stop()

    async def app_func(self):
        async def run_wrapper() -> None:
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run(async_lib="asyncio")
            for task in self.async_tasks:
                task.cancel()

        setupconfig = SetupConfig()
        self.cameras, self.can, self.drive_handler = await setupconfig.initialize()

        # Placeholder task
        #self.async_tasks.append(asyncio.ensure_future(self.template_function()))
        self.async_tasks.append(asyncio.create_task(self.camera_task()))
        self.async_tasks.append(asyncio.create_task(self.drive_task()))
        self.async_tasks.append(asyncio.create_task(self.canbus_task()))
        return await asyncio.gather(run_wrapper(), *self.async_tasks)

    async def camera_task(self):
        while self.root is None:
            await asyncio.sleep(0.01)
        print("camera")

        while True:
            frame = await self.cameras[0].get_frame()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            texture =Texture.create(
                size=(frame.shape[1], frame.shape[0]), icolorfmt="rgb"
            )
            texture.flip_vertical()
            texture.blit_buffer(
                bytes(frame.data),
               colorfmt="rgb",
               bufferfmt="ubyte",
               mipmap_generation=False,
            )

            self.root.ids.image.texture = texture
            await asyncio.sleep(0.01)

    async def drive_task(self):
        while self.root is None:
            await asyncio.sleep(0.01)

        joystick: VirtualJoystickWidget = self.root.ids["joystick"]
        print("drive")
        count = 0
        while True:
            await self.can.set_speed(joystick.joystick_pose.y, -joystick.joystick_pose.x)
            count += 1
            if count > 100:
                break
            await asyncio.sleep(0.02)


    async def canbus_task(self):
        while self.root is None:
            await asyncio.sleep(0.01)

        msg = RawCanbusMessage()
        msg.stamp = time.montonic()
        msg.id = 0x301
        msg.error = False
        msg.remote_transmission = False
        msg.data = b'\x01\x02\x00\x00'

        while True:
            print("sending cann")
            await self.can.send_to_microcontroller(msg)
            await asyncio.sleep(2)

    async def template_function(self) -> None:
        setupconfig = SetupConfig()
        print("setup_can")
        #self.canhandler = AsyncCanHandler()
        print("setupconfig")
        self.cameras, self.can, drive_handler = await setupconfig.initialize()
        print("start task")
        #asyncio.create_task(self.canhandler.run())
        print("task started")
        while self.root is None:
            await asyncio.sleep(0.01)

        msg = SetupPdo(command = 1, amount = 300)

        joystick: VirtualJoystickWidget = self.root.ids["joystick"]

        while True:
            await drive_handler.set_speed(joystick.joystick_pose.y, -joystick.joystick_pose.x)

            await asyncio.sleep(0.02)
            #print("sending cann")
            #await self.canhandler.send_packet(msg, 0x301)
            #await asyncio.sleep(2)

            #frame = await self.cameras[0].get_frame()
            #frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #texture =Texture.create(
            #    size=(frame.shape[1], frame.shape[0]), icolorfmt="rgb"
            #)
            #texture.flip_vertical()
            #texture.blit_buffer(
            #    bytes(frame.data),
            #    colorfmt="rgb",
            #    bufferfmt="ubyte",
            #    mipmap_generation=False,
            #)

            #self.root.ids.image.texture = texture
            #await asyncio.sleep(0.01)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="template-app")

    # Add additional command line arguments here

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(TemplateApp().app_func())
    except asyncio.CancelledError:
        pass
    loop.close()

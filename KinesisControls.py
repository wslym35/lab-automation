# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 14:58:18 2026

@author: Wesley Mills

Sources: https://github.com/Thorlabs/Motion_Control_Examples/tree/main/Python/Kinesis/Integrated%20Stages/Cage%20Rotator
        and ChatGPT 
"""

import clr
import time
import sys
from System import Decimal

# === Load Thorlabs DLLs ===
KINESIS_PATH = r"C:\Program Files\Thorlabs\Kinesis"
sys.path.append(KINESIS_PATH)

clr.AddReference(KINESIS_PATH + r"\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference(KINESIS_PATH + r"\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference(KINESIS_PATH + r"\Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import (DeviceManagerCLI, DeviceConfiguration) 
from Thorlabs.MotionControl.GenericMotorCLI import MotorDirection
#from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import CageRotator

# =============================================================================
# # Import functions from dlls. 
# # Works as of 15:40 
# from Thorlabs.MotionControl.DeviceManagerCLI import *
# from Thorlabs.MotionControl.GenericMotorCLI import *
# from Thorlabs.MotionControl.GenericMotorCLI import MotorDirection
# from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
# from System import Decimal 
# =============================================================================

class K10CR2:
    """
    Automation wrapper for Thorlabs K10CR2 Cage Rotator
    """

    def __init__(self, serial_number, polling_interval=250):
        self.serial = str(serial_number)
        self.polling_interval = polling_interval
        self.device = None
        self._connected = False

    # -------------------------
    # Connection Handling
    # -------------------------

    def connect(self):
        DeviceManagerCLI.BuildDeviceList()

        self.device = CageRotator.CreateCageRotator(self.serial)
        self.device.Connect(self.serial)

        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)

        self.device.StartPolling(self.polling_interval)
        time.sleep(0.5)

        self.device.EnableDevice()
        time.sleep(1)

        self.device.LoadMotorConfiguration(
            self.serial,
            DeviceConfiguration.DeviceSettingsUseOptionType.UseDeviceSettings
        )

        self._connected = True
        print(f"K10CR2 {self.serial} connected.")

    def disconnect(self):
        if self.device is not None:
            self.device.StopPolling()
            self.device.Disconnect()
            self._connected = False
            print(f"K10CR2 {self.serial} disconnected.")

    # -------------------------
    # Motion Commands
    # -------------------------

    def home(self, timeout=60000):
        self._ensure_connected()
        print("Homing...")
        self.device.Home(timeout)
        print("Home complete.")

    def move_to(self, angle_deg, timeout=60000):
        self._ensure_connected()
        print(f"Moving to {angle_deg} degrees...")
        self.device.MoveTo(Decimal(angle_deg), timeout)
        print("Move complete.")

    def move_relative(self, delta_deg, timeout=60000):
        self._ensure_connected()
        print(f"Moving relative {delta_deg} degrees...")
        self.device.MoveRelative(MotorDirection.Forward, Decimal(delta_deg), timeout)
        print("Move complete.")

    def move_continuous(self, direction="forward"):
        self._ensure_connected()
        dir_enum = MotorDirection.Forward if direction.lower() == "forward" else MotorDirection.Backward
        self.device.MoveContinuous(dir_enum)

    def stop(self):
        self._ensure_connected()
        self.device.StopImmediate()

    # -------------------------
    # Status
    # -------------------------

    def get_position(self):
        self._ensure_connected()
        return float(str(self.device.Position)) 

    def is_connected(self):
        return self._connected

    # -------------------------
    # Internal Safety
    # -------------------------

    def _ensure_connected(self):
        if not self._connected:
            raise RuntimeError("Device not connected. Call connect() first.")

    # -------------------------
    # Context Manager Support
    # -------------------------

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
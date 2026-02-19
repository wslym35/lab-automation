# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 11:08:39 2026

@author: Wesley Mills 
"""

import clr
import sys
import time
import os

class K10CR2:
    def __init__(self, serial_number, polling_rate=250, kinesis_path=r"C:\Program Files\Thorlabs\Kinesis"):
        self.serial = str(serial_number)
        self.polling_rate = polling_rate
        self.kinesis_path = kinesis_path
        self.device = None

        # Add DLL directory for Windows
        if os.path.isdir(self.kinesis_path):
            os.add_dll_directory(self.kinesis_path)
        else:
            raise FileNotFoundError(f"Kinesis path not found: {self.kinesis_path}")

        # Load required DLLs
        clr.AddReference(os.path.join(self.kinesis_path, "Thorlabs.MotionControl.DeviceManagerCLI.dll"))
        clr.AddReference(os.path.join(self.kinesis_path, "Thorlabs.MotionControl.IntegratedStepperMotorsCLI.dll"))

        from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
        from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import IntegratedStepperMotor

        self.DeviceManagerCLI = DeviceManagerCLI
        self.IntegratedStepperMotor = IntegratedStepperMotor

    # ----------------------------
    # Connection / Initialization
    # ----------------------------
    def connect(self, wait_for_settings=True, timeout=5000):
        DM = self.DeviceManagerCLI

        # Build device list
        DM.BuildDeviceList()
        time.sleep(0.5)

        # Instantiate device
        self.device = self.IntegratedStepperMotor()

        # Low-level connection
        self.device.CreateConnectionToDevice(self.serial)
        time.sleep(0.5)

        # Optional: Wait for settings initialized (safe)
        if wait_for_settings:
            try:
                self.device.WaitForSettingsInitialized(timeout)
            except Exception:
                # Older K10CR2 firmware may not support this; ignore safely
                pass

        # Enable and start polling
        self.device.EnableDevice()
        self.device.StartPolling(self.polling_rate)
        time.sleep(0.5)

        print(f"K10CR2 ({self.serial}) connected and polling.")

    def disconnect(self):
        if self.device:
            self.device.StopPolling()
            self.device.Disconnect()
            print("K10CR2 disconnected.")

    # ----------------------------
    # Motion
    # ----------------------------
    def home(self, timeout=60000):
        if self.device.get_NeedsHoming():
            print("Homing...")
            self.device.Home(timeout)
            self._wait_for_motion()
            print("Homing complete.")
        else:
            print("Already homed.")

    def move_absolute(self, angle_deg, timeout=60000):
        print(f"Moving to {angle_deg}°")
        self.device.MoveTo(angle_deg, timeout)
        self._wait_for_motion()
        print("Move complete.")

    def move_relative(self, delta_deg, timeout=60000):
        print(f"Moving by {delta_deg}°")
        self.device.MoveRelative(delta_deg, timeout)
        self._wait_for_motion()
        print("Move complete.")

    def stop(self):
        self.device.StopImmediate()
        print("Motion stopped.")

    def get_position(self):
        return self.device.get_Position()

    # ----------------------------
    # Internal wait for motion
    # ----------------------------
    def _wait_for_motion(self, poll_interval=0.1):
        while self.device.get_IsDeviceBusy():
            time.sleep(poll_interval)

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 2026

@author: Wesley Mills and ChatGPT
"""

import serial
import time

DEFAULT_PORT = "COM6"
DEFAULT_BAUD = 19200


class ChameleonLaser:

    def __init__(self, name, port: str = DEFAULT_PORT, baud: int = DEFAULT_BAUD, timeout: float = 2):
        self.name = name
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.device = None
        self._connected = False

    # ------ Connection Handling ------
    def connect(self):
        try:
            self.device = serial.Serial(self.port, self.baud, timeout=self.timeout)
            # Flush stale welcome/status bytes left over from opening the port,
            # otherwise the first ack read in set_wavelength() consumes garbage
            # instead of the laser's real response.
            self.device.reset_input_buffer()
            self.device.reset_output_buffer()
            time.sleep(0.5)
        except Exception as e:
            print(f"Failed to connect to {self.name}: {e}")
            return
        self._connected = True
        print(f"{self.name} connected on {self.port}.")
        # Prime the connection; without an initial read the laser can ignore
        # the very first set_wavelength() command.
        self.get_wavelength()
        time.sleep(0.2)

    def disconnect(self):
        if self.device is not None:
            self.device.close()
            self._connected = False
            print(f"{self.name} disconnected.")

    # ------ Status ------
    def get_wavelength(self) -> float:
        self._ensure_connected()
        self.device.write(b"?VW\r")
        response = self.device.readline().decode("ascii", errors="replace").strip()
        try:
            return float(response.split()[-1])
        except (ValueError, IndexError):
            print(f"{self.name}: unexpected wavelength response: {response!r}")
            return None

    def is_connected(self) -> bool:
        return self._connected

    # ------ Wavelength Control ------
    def set_wavelength(self, wavelength_nm: float, tolerance_nm: float = 0.5,
                        poll_interval_s: float = 1.0, max_wait_s: float = 20.0) -> bool:
        self._ensure_connected()
        print(f"Setting {self.name} wavelength to {wavelength_nm} nm...")
        ack = self._send_wavelength(wavelength_nm)
        print(f"{self.name} set response: {ack!r}")

        confirmed = None
        n_polls = int(max_wait_s / poll_interval_s)
        for poll_n in range(n_polls):
            time.sleep(poll_interval_s)
            confirmed = self.get_wavelength()
            if confirmed is not None and abs(confirmed - wavelength_nm) <= tolerance_nm:
                print(f"{self.name} wavelength confirmed: {confirmed:.1f} nm")
                return True
            if confirmed is not None:
                print(f"Waiting for {self.name}... current: {confirmed:.1f} nm (target {wavelength_nm:.1f} nm)")
            # If 5 s have passed with no movement, the first command may have
            # been silently dropped; resend it once.
            if poll_n == 4 and confirmed is not None and abs(confirmed - wavelength_nm) > 1.0:
                print(f"{self.name}: no movement detected, resending wavelength command...")
                ack = self._send_wavelength(wavelength_nm)
                print(f"{self.name} set response (retry): {ack!r}")
        print(f"WARNING: {self.name} did not reach {wavelength_nm:.1f} nm within {max_wait_s}s "
              f"(last reading: {confirmed}). Continuing anyway.")
        return False

    def _send_wavelength(self, wavelength_nm: float) -> str:
        self.device.write(f"VW= {int(wavelength_nm)}\r".encode("ascii"))
        return self.device.readline().decode("ascii", errors="replace").strip()

    # ------ Internal Safety ------
    def _ensure_connected(self):
        if not self._connected:
            raise RuntimeError(f"{self.name} not connected. Call connect() first.")

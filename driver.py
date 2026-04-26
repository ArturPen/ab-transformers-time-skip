import subprocess
import time
import re
import logging
import sys
import os
from datetime import datetime, timedelta


def get_adb_path() -> str:
    """
    Returns the correct path to adb.exe whether running:
      - As a plain .py script  → looks next to this file
      - As a PyInstaller .exe  → looks in the temp extraction folder (_MEIPASS)
    """
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "adb.exe")


class GameDriver:

    def __init__(
        self,
        adb_address:   str = "127.0.0.1:5575",
        package_name:  str = "com.rovio.angrybirdstransformers",
        activity_name: str = "com.rovio.angrybirdstransformers.AngryBirdsTransformersActivity",
    ):
        self.adb_address   = adb_address
        self.package_name  = package_name
        self.activity_name = activity_name
        self._adb           = get_adb_path()

    def _check_adb(self) -> bool:
        """Returns True if adb.exe exists at the expected path, logs an error otherwise."""
        if not os.path.isfile(self._adb):
            logging.error("ADB not found! Please check if adb.exe is in the folder.")
            return False
        return True

    def run_cmd(self, command: str) -> str:
        """Executes an ADB shell command and returns the output."""
        if not self._check_adb():
            return ""
        full_cmd = f'"{self._adb}" -s {self.adb_address} {command}'
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def connect(self) -> bool:
        """Establishes connection with the BlueStacks emulator."""
        if not self._check_adb():
            return False
        logging.info(f"Connecting to {self.adb_address}...")
        subprocess.run(
            f'"{self._adb}" connect {self.adb_address}',
            shell=True, capture_output=True,
        )
        state = self.run_cmd("get-state")
        if "device" in state:
            logging.info("Connection established successfully!")
            # Disable automatic time synchronization
            self.run_cmd("shell su -c 'settings put global auto_time 0'")
            return True
        else:
            logging.error("Error: Emulator not found. Check ADB settings in BlueStacks.")
            return False

    def get_device_time(self) -> datetime:
        """Fetches the current time directly from the emulator."""
        raw_res   = self.run_cmd("shell su -c 'date +%m%d%H%M%Y.%S'")
        clean_res = re.sub(r'[^0-9.]', '', raw_res)
        try:
            return datetime.strptime(clean_res, "%m%d%H%M%Y.%S")
        except Exception:
            logging.warning(f"Failed to parse device time ({raw_res}). Falling back to PC time.")
            return datetime.now()

    def set_device_time(self, dt_obj: datetime):
        """Sets the system time inside the rooted emulator."""
        adb_date = dt_obj.strftime("%m%d%H%M%Y.%S")
        self.run_cmd(f"shell su -c 'date {adb_date}'")
        logging.info(f"[TIME] Device time set to: {dt_obj.strftime('%d.%m.%Y %H:%M')}")

    def click(self, x: int, y: int):
        """Emulates a screen tap at the specified coordinates."""
        self.run_cmd(f"shell input tap {x} {y}")
        logging.info(f"[ACTION] Tapped coordinates: X={x}, Y={y}")

    def skip_days(self, days_to_skip: int):
        """Jumps forward a specified number of days from the emulator's current time."""
        current_time = self.get_device_time()
        new_time     = current_time + timedelta(days=days_to_skip)
        self.set_device_time(new_time)
        logging.info(f"[ACTION] Skipped forward {days_to_skip} day(s).")

    def apply_fix(self):
        """Reverts the time to yesterday at 23:59 to trigger the calendar fix."""
        real_yesterday = (datetime.now() - timedelta(days=1)).replace(
            hour=23, minute=59, second=0)
        logging.info("[FIX] Reverting time to yesterday 23:59...")
        self.set_device_time(real_yesterday)

    def is_game_foreground(self) -> bool:
        """
        Returns True if the game's Activity is currently in the foreground.
        Returns False if the game is frozen (ANR dialog) or pushed to background
        by a system dialog.
        """
        output = self.run_cmd("shell dumpsys activity activities")
        for line in output.splitlines():
            if "mResumedActivity" in line or "ResumedActivity" in line:
                return self.package_name in line
        # Fallback: check focused window
        focused = self.run_cmd("shell dumpsys window windows | grep mCurrentFocus")
        return self.package_name in focused

    def stop_game(self):
        """Force-stops the game and clears it from background memory."""
        self.run_cmd(f"shell am force-stop {self.package_name}")
        time.sleep(2)
        logging.info("[ACTION] Game completely stopped.")

    def start_game(self):
        """Launches the game using its specific Activity path."""
        logging.info(f"[ACTION] Launching {self.package_name}...")
        self.run_cmd("shell input keyevent 3")
        time.sleep(1)
        cmd    = f"shell am start -S -W -n {self.package_name}/{self.activity_name}"
        output = self.run_cmd(cmd)
        if "Complete" in output or "Status: ok" in output:
            logging.info("[SUCCESS] Game launched successfully.")
        else:
            logging.warning("Launch command returned unexpected output. Check the emulator screen.")
        time.sleep(7)
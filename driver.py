import subprocess
import time
import re
import logging
from datetime import datetime, timedelta

class GameDriver:
    def __init__(self, adb_address="127.0.0.1:5575"): # Check your adb address in Bluestacks advanced settings
        self.adb_address = adb_address
        self.package_name = "com.rovio.angrybirdstransformers"
        # The specific activity name required to bypass the suspended tab issue
        self.activity_name = "com.rovio.angrybirdstransformers.AngryBirdsTransformersActivity"

    def run_cmd(self, command):
        """Executes an ADB shell command and returns the output."""
        full_cmd = f"adb -s {self.adb_address} {command}"
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()

    def connect(self):
        """Establishes connection with the BlueStacks emulator."""
        logging.info(f"Connecting to {self.adb_address}...")
        subprocess.run(f"adb connect {self.adb_address}", shell=True, capture_output=True)
        
        state = self.run_cmd("get-state")
        if "device" in state:
            logging.info("Connection established successfully!")
            # Disable automatic time synchronization to prevent Android from overriding our jumps
            self.run_cmd("shell su -c 'settings put global auto_time 0'")
            return True
        else:
            logging.error("Error: Emulator not found. Check ADB settings in BlueStacks.")
            return False

    def get_device_time(self):
        """Fetches the current time directly from the emulator."""
        raw_res = self.run_cmd("shell su -c 'date +%m%d%H%M%Y.%S'")
        # Strip any unexpected characters, keeping only digits and the period
        clean_res = re.sub(r'[^0-9.]', '', raw_res)
        
        try:
            return datetime.strptime(clean_res, "%m%d%H%M%Y.%S")
        except Exception as e:
            logging.warning(f"Failed to parse device time ({raw_res}). Falling back to PC time.")
            return datetime.now()

    def set_device_time(self, dt_obj):
        """Sets the system time inside the rooted emulator."""
        adb_date = dt_obj.strftime("%m%d%H%M%Y.%S")
        self.run_cmd(f"shell su -c 'date {adb_date}'")
        logging.info(f"[TIME] Device time set to: {dt_obj.strftime('%d.%m.%Y %H:%M')}")

    def click(self, x, y):
        """Emulates a screen tap at the specified coordinates."""
        self.run_cmd(f"shell input tap {x} {y}")
        logging.info(f"[ACTION] Tapped coordinates: X={x}, Y={y}")

    def skip_days(self, days_to_skip):
        """Jumps forward a specified number of days from the emulator's current time."""
        current_time = self.get_device_time()
        new_time = current_time + timedelta(days=days_to_skip)
        self.set_device_time(new_time)
        logging.info(f"[ACTION] Skipped forward {days_to_skip} day(s).")

    def apply_fix(self):
        """Reverts the time to yesterday at 23:59 based on real-world time to trigger the calendar fix."""
        real_yesterday = (datetime.now() - timedelta(days=1)).replace(hour=23, minute=59, second=0)
        logging.info("[FIX] Reverting time to yesterday 23:59 to prepare for the midnight transition...")
        self.set_device_time(real_yesterday)
    
    def stop_game(self):
        """Force-stops the game and clears it from background memory."""
        self.run_cmd(f"shell am force-stop {self.package_name}")
        time.sleep(2)
        logging.info("[ACTION] Game completely stopped.")

    def start_game(self):
        """Launches the game using its specific Activity path, killing any hung instances."""
        logging.info(f"[ACTION] Attempting to launch {self.package_name}...")
        self.run_cmd("shell input keyevent 3")
        time.sleep(1)
        cmd = f"shell am start -S -W -n {self.package_name}/{self.activity_name}"
        output = self.run_cmd(cmd)
        
        if "Complete" in output or "Status: ok" in output:
            logging.info("[SUCCESS] Game launched successfully.")
        else:
            logging.warning("Something went wrong with the launch command. Please check the emulator screen.")
        time.sleep(7)
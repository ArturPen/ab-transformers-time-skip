from driver import GameDriver

import time
import math
import logging
import platform
import os
import subprocess
import threading


# --- Global stop flag ---
stop_event = threading.Event()


def setup_logging():
    """
    Configures dual-channel logging:
    1. A permanent file log for debugging.
    2. A dynamic console output for user feedback.
    """
    log_file = "farm_log.txt"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # Reset existing handlers

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

    # File Handler: Captures all event details
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console Handler: Filtered output to keep the UI clean
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Automatically open the log file based on the Operating System
    try:
        if platform.system() == 'Windows':
            os.startfile(log_file)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', log_file])
        else:  # Linux/Other
            subprocess.call(['xdg-open', log_file])
    except Exception as e:
        logging.error(f"Could not open log file automatically: {e}")

    return console_handler


def stop_listener():
    """
    Background thread that waits for the user to type 'stop' in the terminal.
    Sets the global stop_event flag when triggered.
    """
    while not stop_event.is_set():
        try:
            user_input = input()
            if user_input.strip().lower() == "stop":
                stop_event.set()
                break
        except (EOFError, OSError):
            # stdin was closed (e.g. running as compiled exe with no console)
            break


def _interruptible_sleep(seconds):
    """Sleep in 1-second ticks, returning True if stop was requested."""
    for _ in range(seconds):
        if stop_event.is_set():
            return True
        time.sleep(1)
    return False


def _run_fix_and_exit(driver, console_handler):
    """Shared logic: execute fix sequence after a stop command."""
    console_handler.setLevel(logging.INFO)
    logging.info("[STOP] Program stopped via 'stop' command. Executing fix before exit...")
    driver.stop_game()
    time.sleep(2)
    driver.apply_fix()
    time.sleep(2)
    driver.start_game()
    logging.info("[STOP] Program was stopped via the 'stop' command.")
    logging.info("[STOP] Fix procedure completed. It is safe to close the program.")
    logging.info("===================================================")
    logging.info("Stay on the map view until your device clock reaches 00:00.")
    logging.info("===================================================")


def start_farming(iterations, mode, console_handler):
    """
    Executes the farming loop and handles the post-farm calendar synchronization.

    Stop-command behaviour by mode:
      Mode 1 (Gems):      'stop' is available from the very first cycle.
      Mode 2 (Resources): 'stop' message and listener are only activated AFTER
                          cycle 14 completes (minimum required for the fix to work).
    """
    driver = GameDriver()

    if not driver.connect():
        return

    # UI coordinates for the 'Claim' button
    BTN_X, BTN_Y = 720, 890

    # Duration estimation (Average cycle time is ~8 seconds)
    total_seconds = iterations * 8
    m, s = divmod(total_seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        est_time = f"{h}h {m}m {s}s"
    elif m > 0:
        est_time = f"{m}m {s}s"
    else:
        est_time = f"{s}s"

    logging.info("=" * 50)
    mode_name = "Gems Farm (+2 Days Jump)" if mode == 1 else "Resources Farm (+1 Day Jump)"
    logging.info(f"FARMING MODE: {mode_name}")
    logging.info(f"TARGET LOOPS: {iterations} cycles.")
    logging.info(f"ESTIMATED TIME: ~{est_time}")
    logging.info("=" * 50)

    # Mode 1: stop is available immediately
    if mode == 1:
        logging.info("[INFO] Type 'stop' and press Enter at any time to safely stop the program.")
        logging.info("[INFO] The fix procedure will be executed before stopping.")

    # Mode 2: remind user that stop will unlock after cycle 14
    if mode == 2:
        logging.info("[INFO] 'stop' command will become available after cycle 14 completes.")
        logging.info("[INFO] (14 days minimum required for the fix to work safely.)")

    # Silence console INFO logs during the loop to avoid terminal clutter
    console_handler.setLevel(logging.WARNING)

    stopped_early = False

    for i in range(iterations):
        current_cycle = i + 1  # 1-based

        # ---- Stop-flag check ----
        # Mode 1: check every cycle.
        # Mode 2: check only after cycle 14 has already finished (i >= 14).
        if mode == 1 and stop_event.is_set():
            stopped_early = True
            break
        if mode == 2 and i >= 14 and stop_event.is_set():
            stopped_early = True
            break

        logging.info(f"--- [Cycle {current_cycle}/{iterations}] ---")

        # Step 1: Time skip
        if mode == 1:
            driver.skip_days(2)
        elif mode == 2:
            driver.skip_days(1)

        # Step 2: Wait for game engine (interruptible where stop is allowed)
        if mode == 1 or (mode == 2 and i >= 14):
            if _interruptible_sleep(5):
                stopped_early = True
                break
        else:
            time.sleep(5)

        # Step 3: Tap claim button
        driver.click(BTN_X, BTN_Y)

        # Step 4: Collection animation grace period
        if mode == 1 or (mode == 2 and i >= 14):
            if _interruptible_sleep(2):
                stopped_early = True
                break
        else:
            time.sleep(2)

        # ---- After cycle 14 completes in Mode 2: unlock stop ----
        if mode == 2 and current_cycle == 14:
            # Activate the listener thread now that it is safe to stop
            listener_thread = threading.Thread(target=stop_listener, daemon=True)
            listener_thread.start()
            # Temporarily re-enable console to show the unlock message
            console_handler.setLevel(logging.INFO)
            logging.info("[INFO] Cycle 14 complete. You may now type 'stop' and press Enter")
            logging.info("[INFO] to safely stop after the current cycle finishes.")
            console_handler.setLevel(logging.WARNING)

    # Re-enable console for finalization output
    console_handler.setLevel(logging.INFO)

    if stopped_early:
        _run_fix_and_exit(driver, console_handler)
        return

    logging.info("[+] Farming phase completed! Initiating calendar fix...")

    driver.stop_game()
    time.sleep(2)
    driver.apply_fix()
    time.sleep(2)
    driver.start_game()

    logging.info("[!] Waiting 25 seconds for the game map to fully load...")
    time.sleep(25)

    logging.info("===================================================")
    logging.info("[SUCCESS] Setup complete. DO NOT touch the device.")
    logging.info("Stay on the map view until your device clock reaches 00:00.")
    logging.info("The game will naturally sync the day change, restoring cycles.")
    logging.info("===================================================")


if __name__ == "__main__":
    console_handler = setup_logging()

    print("\n--- Angry Birds Transformers: Time Skip Auto-Farmer ---")
    print("Select Farming Strategy:")
    print(" [1] Gems Farm (Skips 2 days; targets 5 gems per claim)")
    print(" [2] Resources Farm (Skips 1 day; targets sequential weekly rewards)")

    try:
        mode_input = int(input("\nEnter choice (1 or 2): "))

        if mode_input not in [1, 2]:
            logging.error("Invalid selection. Please run the script again.")

        elif mode_input == 1:
            target = int(input("Enter desired gem amount: "))
            if target <= 0:
                logging.error("Target must be a positive integer.")
            else:
                loops = math.ceil(target / 5)

                # Mode 1: start stop listener immediately
                listener_thread = threading.Thread(target=stop_listener, daemon=True)
                listener_thread.start()

                print("\n[INFO] Farming started. Type 'stop' and press Enter to safely stop.\n")

                start_farming(loops, mode_input, console_handler)

        elif mode_input == 2:
            loops = int(input("Enter number of days to farm (Minimum 15): "))
            if loops <= 14:
                logging.error("Minimum 15 days required for this mode.")
            else:
                # Mode 2: stop listener is started INSIDE start_farming after cycle 14.
                # No listener thread here — it would allow stopping before the safe threshold.
                print("\n[INFO] Farming started. 'stop' command will unlock after cycle 14.\n")

                start_farming(loops, mode_input, console_handler)

    except ValueError:
        logging.error("Input Error: Please enter numeric values only.")

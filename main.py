from driver import GameDriver
import time
import math
import logging
import platform
import os
import subprocess

def setup_logging():
    """
    Configures dual-channel logging: 
    1. A permanent file log for debugging.
    2. A dynamic console output for user feedback.
    """
    log_file = "farm_log.txt"
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear() # Reset existing handlers
    
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
        elif platform.system() == 'Darwin': # macOS
            subprocess.call(['open', log_file])
        else: # Linux/Other
            subprocess.call(['xdg-open', log_file])
    except Exception as e:
        logging.error(f"Could not open log file automatically: {e}")
        
    return console_handler

def start_farming(iterations, mode, console_handler):
    """
    Executes the farming loop and handles the post-farm calendar synchronization.
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
    
    logging.info("="*50)
    mode_name = "Gems Farm (+2 Days Jump)" if mode == 1 else "Resources Farm (+1 Day Jump)"
    logging.info(f"FARMING MODE: {mode_name}")
    logging.info(f"TARGET LOOPS: {iterations} cycles.")
    logging.info(f"ESTIMATED TIME: ~{est_time}")
    logging.info("="*50)

    # Silence console INFO logs during the loop to avoid terminal clutter
    console_handler.setLevel(logging.WARNING)

    for i in range(iterations):
        # Progress is recorded in the log file, but hidden from the console
        logging.info(f"--- [Cycle {i+1}/{iterations}] ---")
        
        # Step 1: Execute Time Skip based on selected strategy
        if mode == 1:
            driver.skip_days(2) # Strategy: Break streak to force Day 1 rewards (Gems)
        elif mode == 2:
            driver.skip_days(1) # Strategy: Progress through the weekly calendar
            
        # Step 2: Sync wait for game engine to register date change
        time.sleep(5)
        
        # Step 3: Interaction with the reward UI
        driver.click(BTN_X, BTN_Y)
        
        # Step 4: Grace period for the collection animation
        time.sleep(2)

    # Re-enable console logging for the finalization phase
    console_handler.setLevel(logging.INFO)

    logging.info("[+] Farming phase completed! Initiating calendar fix...")
    
    # Reset game state to apply time correction safely
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
    print("  [1] Gems Farm      (Skips 2 days; targets 5 gems per claim)")
    print("  [2] Resources Farm (Skips 1 day; targets sequential weekly rewards)")
    
    try:
        mode_input = int(input("\nEnter choice (1 or 2): "))
        
        if mode_input not in [1, 2]:
            logging.error("Invalid selection. Please run the script again.")
        else:
            if mode_input == 1:
                target = int(input("Enter desired gem amount: "))
                if target <= 0:
                    logging.error("Target must be a positive integer.")
                else:
                    # Calculate loops needed (5 gems per loop)
                    loops = math.ceil(target / 5)
                    start_farming(loops, mode_input, console_handler)
                    
            elif mode_input == 2:
                # Sequential farming requires at least 15 claims
                loops = int(input("Enter number of days to farm (Minimum 15): "))
                if loops <= 14:
                    logging.error("Minimum 15 days required for this mode.")
                else:
                    start_farming(loops, mode_input, console_handler)
                    
    except ValueError:
        logging.error("Input Error: Please enter numeric values only.")
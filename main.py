from driver import GameDriver
import time
import math
import logging
import platform
import os
import subprocess

def setup_logging():
    """Configures real-time logging to both the console and a text file."""
    log_file = "farm_log.txt"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # Automatically open the log file for the user to watch
    try:
        if platform.system() == 'Windows':
            os.startfile(log_file)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', log_file])
        else:  # Linux
            subprocess.call(['xdg-open', log_file])
    except Exception as e:
        logging.error(f"Could not open log file automatically: {e}")

def farm_gems(target_gems):
    driver = GameDriver()
    if not driver.connect(): 
        return
        
    # Claim button coordinates (Must match emulator resolution, e.g., 1920x1080)
    BTN_X, BTN_Y = 720, 890

    # Calculate required loops (5 gems per day-1 claim)
    iterations = math.ceil(target_gems / 5)
    
    logging.info("="*50)
    logging.info(f"TARGET: {target_gems} gems.")
    logging.info(f"CALCULATED LOOPS: {iterations} cycles.")
    logging.info("="*50)

    # NOTE: The game must already be running manually before starting the script.
    # The exploit relies on keeping the game running in the background while changing the date Time Skip glitch in Angry Birds T_260419_170522.pdf].
    for i in range(iterations):
        logging.info(f"\n--- [Cycle {i+1}/{iterations}] ---")
        
        # 1. Jump 2 days into the future to break the login streak
        driver.skip_2_days()
        
        # 2. Wait for the game to process the date change and display the reward window
        time.sleep(5)
        
        # 3. Tap the "Claim" button
        driver.click(BTN_X, BTN_Y)
        
        # 4. Short pause to allow collection animation to finish
        time.sleep(2)

    logging.info("\n[+] Farming phase completed! Initiating calendar fix...")
    
    # 1. Close the game entirely before applying the time fix Time Skip glitch in Angry Birds T_260419_170522.pdf]
    driver.stop_game()
    time.sleep(2)
    
    # 2. Set time to 23:59 of the previous real-world day Time Skip glitch in Angry Birds T_260419_170522.pdf]
    driver.apply_fix() 
    time.sleep(2)
    
    # 3. Relaunch the game
    driver.start_game()
    logging.info("[!] Waiting 25 seconds for the game map to fully load...")
    time.sleep(25)
    
    logging.info("===================================================")
    logging.info("[SUCCESS] The game is open. DO NOT touch anything.")
    logging.info("Wait on the map until your phone/emulator clock hits exactly 00:00.")
    logging.info("The game will register the real-time day change, restoring quest and coin cycles Time Skip glitch in Angry Birds T_260419_170522.pdf].")
    logging.info("Once the calendar is fixed, you may turn your internet back on.")
    logging.info("===================================================")

if __name__ == "__main__":
    setup_logging()
    
    print("\n--- Angry Birds Transformers: Time Skip Auto-Farmer ---")
    try:
        user_input = int(input("Enter the total amount of gems you want to farm: "))
        if user_input <= 0:
            logging.error("Please enter a positive number.")
        else:
            farm_gems(user_input)
    except ValueError:
        logging.error("Invalid input. Please enter numbers only.")
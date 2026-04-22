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
    
    try:
        if platform.system() == 'Windows':
            os.startfile(log_file)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', log_file])
        else:
            subprocess.call(['xdg-open', log_file])
    except Exception as e:
        logging.error(f"Could not open log file automatically: {e}")

def start_farming(iterations, mode):
    driver = GameDriver()
    if not driver.connect(): 
        return
        
    BTN_X, BTN_Y = 720, 890
    
    logging.info("="*50)
    mode_name = "Gems Farm (+2 Days Jump)" if mode == 1 else "Resources Farm (+1 Day Jump)"
    logging.info(f"FARMING MODE: {mode_name}")
    logging.info(f"TARGET LOOPS: {iterations} cycles.")
    logging.info("="*50)

    for i in range(iterations):
        logging.info(f"\n--- [Cycle {i+1}/{iterations}] ---")
        
        # 1. Jump into the future based on selected mode
        if mode == 1:
            driver.skip_days(2) # Breaks streak, repeat day 1
        elif mode == 2:
            driver.skip_days(1) # Keeps streak, collects weekly calendar
            
        # 2. Wait for the game to process the date change
        time.sleep(5)
        
        # 3. Tap the "Claim" button
        driver.click(BTN_X, BTN_Y)
        
        # 4. Short pause to allow collection animation to finish
        time.sleep(2)

    logging.info("\n[+] Farming phase completed! Initiating calendar fix...")
    
    driver.stop_game()
    time.sleep(2)
    driver.apply_fix() 
    time.sleep(2)
    driver.start_game()
    
    logging.info("[!] Waiting 25 seconds for the game map to fully load...")
    time.sleep(25)
    
    logging.info("===================================================")
    logging.info("[SUCCESS] The game is open. DO NOT touch anything.")
    logging.info("Wait on the map until your phone/emulator clock hits exactly 00:00.")
    logging.info("The game will register the real-time day change, restoring quest and coin cycles.")
    logging.info("Once the calendar is fixed, you may turn your internet back on.")
    logging.info("===================================================")

if __name__ == "__main__":
    setup_logging()
    
    print("\n--- Angry Birds Transformers: Time Skip Auto-Farmer ---")
    print("Please select your farming mode:")
    print("  [1] Gems Farm      (Skips 2 days to break streak, farms 5 gems per claim)")
    print("  [2] Resources Farm (Skips 1 day to collect sequential weekly rewards)")
    
    try:
        mode_input = int(input("\nEnter mode (1 or 2): "))
        
        if mode_input not in [1, 2]:
            logging.error("Invalid mode selected. Please restart and choose 1 or 2.")
        else:
            if mode_input == 1:
                target = int(input("Enter the total amount of gems you want to farm: "))
                if target <= 0:
                    logging.error("Please enter a positive number.")
                else:
                    loops = math.ceil(target / 5)
                    start_farming(loops, mode_input)
                    
            elif mode_input == 2:
                # For resource farming, asking for days makes more sense than a specific gem target
                loops = int(input("Enter the number of days (claims) you want to process (15 days or more): "))
                if loops <= 14:
                    logging.error("Please enter 15 or more.")
                else:
                    start_farming(loops, mode_input)
                    
    except ValueError:
        logging.error("Invalid input. Please enter numbers only.")
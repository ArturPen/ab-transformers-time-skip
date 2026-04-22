import time
from datetime import datetime, timedelta
from driver import PhoneDriver 

def main():
    device = PhoneDriver() 
    
    # Get current real date from system
    # Script checks today's date automatically
    real_today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Start with real date minus 2 days, so the first loop step 
    # (+= 2 days) lands exactly on today
    current_game_date = real_today - timedelta(days=2)
    days_farmed = 0

    print(f"[SYSTEM] Script started. Real date: {real_today.strftime('%d.%m.%Y')}")

    while True:
        # Jump forward by 2 days
        current_game_date += timedelta(days=2)
        days_farmed += 2
        
        print(f"\n>>> STEP: Jumping to {current_game_date.strftime('%d.%m.%Y')}")
        device.set_date(current_game_date)
        
        # Waiting for game to load on Samsung Galaxy A55
        time.sleep(1.5) 
        device.run_shell("settings put system accelerometer_rotation 0")
        device.run_shell("settings put system user_rotation 0") 
        time.sleep(1.5)
        device.long_tap(900, 900, 500)
        time.sleep(1) # Fixed empty time.sleep()
        print("[FARM] Collecting gems and gold...")

        # If 14 days passed (7 jumps), perform rollback
        if days_farmed >= 14:
            # Цель: вчерашний день относительно РЕАЛЬНОГО сегодня
            target_fix_date = real_today - timedelta(days=1)
            print(f"[SYSTEM] 14-day limit reached. Fixing to: {target_fix_date.strftime('%d.%m.%Y')} 23:59")
            
            # Вызываем фикс
            device.fix_date(target_fix_date) 
            
            # СБРОС: возвращаем текущую игровую дату к "вчера", 
            # чтобы следующий цикл (+2 дня) попал на "завтра" относительно фикса
            days_farmed = 0
            current_game_date = target_fix_date 
            
            print("[INFO] Waiting for midnight transition...")
            time.sleep(70) # Ждем минуту перехода + запас на синхронизацию

if __name__ == "__main__":
    main()
import subprocess
import io
import time
import calendar
from PIL import Image
from datetime import datetime, timedelta

class PhoneDriver:
    PACKAGE = "com.rovio.angrybirdstransformers"

    def __init__(self):
        # If adb.exe is in the project folder, keep "adb"
        # If not, replace with r"C:\platform-tools\adb.exe"
        self.adb = ["adb"]

    def run_shell(self, command):
        cmd = self.adb + ["shell"] + command.split()
        return subprocess.check_output(cmd).decode('utf-8').strip()

    def set_auto_time(self, enable=False):
        val = "1" if enable else "0"
        self.run_shell(f"settings put global auto_time {val}")
        self.run_shell(f"settings put global auto_time_zone {val}")

    def long_tap(self, x, y, duration=1000):
        """
        x, y: coordinates
        duration: hold time in ms (1000 ms = 1 second)
        """
        # Swipe from point to the same point with a specified duration
        self.run_shell(f"input swipe {x} {y} {x} {y} {duration}")
    
    def set_date(self, target_date):
        print(f"[SYSTEM] Moving to {target_date.strftime('%d.%m.%Y')}...")
        
        # 1. Open date settings
        self.run_shell("am start -a android.settings.DATE_SETTINGS")
        time.sleep(3)
        self.run_shell("settings put system accelerometer_rotation 0")
        time.sleep(1)
        self.run_shell("settings put system user_rotation 0")
        time.sleep(2)
        
        # 2. Tap "Set date"
        self.tap(600, 600) 
        time.sleep(1)

        # 3. Date selection menu opens
        self.tap(500, 1225) 
        time.sleep(1.5) # Увеличил задержку для надежности открытия
        
        # Читаем реальную дату с телефона перед сдвигом
        device_date_str = self.run_shell("date +%Y-%m-%d")
        dev_y, dev_m, dev_d = map(int, device_date_str.split('-'))

        # Узнаем количество дней в ТЕКУЩЕМ месяце (чтобы колесо могло сделать оборот)
        days_in_dev_month = calendar.monthrange(dev_y, dev_m)[1]

        # МАТЕМАТИКА ДЛЯ СКРОЛЛА ВПЕРЕД (DOWN)
        # Остаток от деления решает проблему перехода (например, 30 -> 1 = 2 клика)
        d_clicks = (target_date.day - dev_d) % days_in_dev_month
        m_clicks = (target_date.year - dev_y) * 12 + target_date.month - dev_m

        print(f"[DEBUG] Farm jump: day_clicks = {d_clicks}, month_clicks = {m_clicks}")

        # Шаг 1: КРУТИМ ДНИ (Важно делать это первым, чтобы избежать сброса 31->28 числа)
        for _ in range(d_clicks):
            self.tap(246, 1790) # Координаты колеса дней ВНИЗ (вперед)
            time.sleep(0.5)

        # Шаг 2: КРУТИМ МЕСЯЦЫ
        for _ in range(m_clicks):
            # X=507 взял из твоего fix_date для месяцев, Y=1800 для движения вниз
            self.tap(507, 1800) 
            time.sleep(0.5)

        # 5. Tap "Done"
        self.tap(750, 2066) 
        time.sleep(0.8)

        # Return to game
        self.launch_game()

    def fix_date(self, target_date):
        print(f"\n[!!!] STARTING FIX MACRO TO 23:59 [!!!]")
        
        self.run_shell(f"am force-stop {self.PACKAGE}")
        self.run_shell("am start -a android.settings.DATE_SETTINGS")
        time.sleep(3)
        self.run_shell("settings put system accelerometer_rotation 0")
        time.sleep(1)
        self.run_shell("settings put system user_rotation 0")
        time.sleep(2)

        # --- ОТКАТ ДАТЫ ---
        self.tap(600, 600) # "Установить дату"
        time.sleep(1)
        self.tap(500, 1225) # Открыть барабан
        time.sleep(1)

        # Читаем, где мы сейчас (в будущем)
        device_date_str = self.run_shell("date +%Y-%m-%d")
        dev_y, dev_m, dev_d = map(int, device_date_str.split('-'))

        # Для отката назад нам нужно просто посчитать прямую разницу
        # Если мы в феврале (2), а нужно в январь (1) -> 2 - 1 = 1 клик ВВЕРХ
        m_back = dev_m - target_date.month
        if m_back < 0: m_back += 12 # На случай перехода через год
        
        d_back = dev_d - target_date.day
        if d_back < 0: 
            prev_month_days = calendar.monthrange(target_date.year, target_date.month)[1]
            d_back += prev_month_days

        # Крутим ВВЕРХ (точка тапа должна быть выше центра колеса)
        for _ in range(m_back):
            self.tap(507, 1400) # Координата Y выше центра для прокрутки НАЗАД
            time.sleep(0.4)
        for _ in range(d_back):
            self.tap(205, 1400) 
            time.sleep(0.4)

        self.tap(750, 2066) # Готово
        time.sleep(1)

        # --- УСТАНОВКА ВРЕМЕНИ 23:59 ---
        self.tap(270, 830) # "Установить время"
        time.sleep(1)

        # Читаем текущее время (оно может быть любым)
        t_str = self.run_shell("date +%H:%M")
        now_h, now_m = map(int, t_str.split(':'))

        # Сколько кликов нужно до 23:59 (двигаемся вперед до упора)
        h_to_23 = (23 - now_h) % 24
        m_to_59 = (59 - now_m) % 60

        print(f"[DEBUG] Time set: {h_to_23}h clicks, {m_to_59}m clicks")

        for _ in range(h_to_23):
            self.tap(300, 1875) # Вниз (вперед)
            time.sleep(0.4)
        for _ in range(m_to_59):
            self.tap(755, 1880) # Вниз (вперед)
            time.sleep(0.4)

        self.tap(750, 2066) # Готово
        time.sleep(1)

        self.launch_game()

    def launch_game(self):
        self.run_shell(f"monkey -p {self.PACKAGE} -c android.intent.category.LAUNCHER 1")

    def tap(self, x, y):
        self.run_shell(f"input tap {x} {y}")

    def get_time_string(self):
        return self.run_shell("date +%H:%M:%S")
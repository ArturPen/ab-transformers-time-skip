# AB Transformers Automated Time-Skip Glitch 🤖⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fully automated Python script for the **Ultimate Time-Skip Glitch** in Angry Birds Transformers. This tool connects to a rooted emulator via ADB, manipulates the system clock to infinitely farm gems/resources, and safely restores the calendar sync without bricking your game timers.

📍 **Original Method & Exploit Guide:** [Reddit - Ultimate Guide](https://www.reddit.com/user/artur_pen/comments/1srxiu6/ultimate_guide_time_skip_glitch_in_angry_birds/)

---

## ⚙️ How It Works (Code Analysis)

The script relies on `adb shell` and `su` commands to bypass Android's time synchronization. It is fully self-contained and operates in a precise sequence:

* **Target Calculation:** You input the exact amount of gems you want to farm. The script automatically calculates the required number of loops (5 gems per claim).
* **The Farming Loop:**
  * Skips exactly **2 days forward** to break the login streak and trigger the daily reward.
  * Waits 5 seconds for the game to process the date change.
  * Emulates a screen tap on the "Claim" button.
  * Repeats until the target is reached.
* **The "Time Fix" (No 14-day skip required):**
  * Once farming is done, the script force-stops the game completely.
  * It calculates real-world time and sets the emulator's clock to **23:59 of the *previous* day**.
  * It launches the game and waits. 
  * **Your only job** is to watch the map screen until the clock hits exactly `00:00`. The game registers a natural day rollover, fixing the "2000 days until next mission" bug permanently.

---

## 🛠 Prerequisites & Emulator Setup

To change the system date, Android **requires Root access**. The script will not work on an unrooted emulator.

### Required Software
* **Python 3.8+** (No external libraries required, only built-in modules are used).
* **[BlueStacks 5](https://www.bluestacks.com/)** (Recommended emulator).
* **[BSTweaker](https://bstweaker.ru/)** (Required utility to unlock Root access in BlueStacks).

### Rooting & ADB Configuration
* Open **BSTweaker**, connect to your BlueStacks instance, and follow the instructions to unlock and patch Root access.
* In BlueStacks, go to **Settings** -> **Advanced** (or Developer Options).
* Toggle on **Android Debug Bridge (ADB)**.
* Note your ADB port (usually `127.0.0.1:5575` or `127.0.0.1:5555`). 

---

## 🚀 Installation & Usage

### Step 1: Clone the repository
git clone https://github.com/ArturPen/ab-transformers-time-skip.git
cd ab-transformers-time-skip

Step 2: Configure Coordinates (If necessary)
The script is optimized for a 1920x1080 emulator resolution. The "Claim" button coordinates are set to X=720, Y=890 inside main.py. If you use a different resolution, you will need to adjust BTN_X and BTN_Y. Or you can change your resolution in Bluestacks settings.

Step 3: Check ADB Connection
Set your ADB adress from Bluestacks advanced settings in driver.py __init__.

Step 4: Launch script
You have to launch main.py with driver.py and 3 adb files in the same folder.

📝 Features & Logging
Real-time Logging: The script automatically generates a farm_log.txt file and attempts to open it on your PC so you can monitor the farming cycles, calculated loops, and ADB execution status in real-time.
Auto-Recovery: Disables Android's auto_time global setting upon connection so the emulator doesn't fight the script during date manipulation.
Direct Activity Launching: Uses native Android intents to wake the game up directly bypassing suspended tabs issues.

⚠️ Disclaimer
Use at your own risk. This exploit manipulates core game mechanics. While the script includes the Time Fix to prevent timer soft-locks, excessive use may result in leaderboard bans or account flags by Exient/Rovio. Always backup your game progress before using automation tools. Educational purposes only.

## ❤️ Support
If this tool saved you time and gems, feel free to support the project!
### 🪙 Donate via Crypto
* **TON:** `UQB4L-ZzhteBgkQEWqejBkDm4ZKjG0leGJwgfXMy5gfknzQR`
* **USDT (TRC-20):** `TEL1XmhnoE6eeudsPEZf3F82bPZMKrrrSd`
* **GitHub Star:** Leave a ⭐ if you find this project useful!

Developed by ArturPen

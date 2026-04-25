# AB Transformers: Time Skip Auto-Farmer 🤖⚡

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ADB](https://img.shields.io/badge/ADB-Android%20Debug%20Bridge-green.svg)](https://developer.android.com/tools/adb)

A fully automated Python script for the **Ultimate Time-Skip Glitch** in Angry Birds Transformers.
Connects to a rooted BlueStacks emulator via ADB, manipulates the system clock to farm gems and resources, and safely restores the calendar sync so your timers don't break.

📍 **Original exploit method & manual guide:** [Reddit — Ultimate Guide](https://www.reddit.com/r/angrybirdstransform/comments/1ssj9wo/ultimate_guide_time_skip_glitch_in_angry_birds/)

---

## ⚠️ Disclaimer

Use at your own risk. This tool manipulates core game mechanics. While the script includes an automatic Time Fix to prevent timer soft-locks, excessive use may result in leaderboard bans or account flags by Exient/Rovio. Always back up your game data before using automation tools. For educational purposes only.

---

## ❤️ Support

If this tool saved you time and gems, feel free to support the project!

### 🪙 Donate via Crypto

- **TON:** `UQB4L-ZzhteBgkQEWqejBkDm4ZKjG0leGJwgfXMy5gfknzQR`
- **USDT (TRC-20):** `TEL1XmhnoE6eeudsPEZf3F82bPZMKrrrSd`

### ⭐ GitHub Star

Leave a ⭐ if you find this project useful — it helps others find it!

---

## 📋 Table of Contents

- How It Works
- Prerequisites
- Installation & Usage
- Features
- Configuration

---

## ⚙️ How It Works

The script uses `adb shell` and `su` commands to bypass Android's time synchronization on a rooted emulator. After connecting, it disables `auto_time` globally so Android doesn't fight the date changes during the run.

### Mode 1 — Gems Farm (+2 Days Jump)

Skips **2 days forward** on every cycle. This breaks the login streak deliberately, which forces the game to reset to **Day 1** of the weekly calendar — always a 5-gem reward.

- **Input:** total gems you want
- **Calculation:** script divides by 5 and rounds up to get the number of loops
- **Stop command:** available from cycle 1

### Mode 2 — Resources Farm (+1 Day Jump)

Skips **exactly 1 day forward** per cycle. This preserves the daily login streak, so you collect the full 7-day calendar rewards in sequence — Pigs, Coins, and Day-7 Crystals.

- **Input:** number of days (claims) to process — **minimum 15**
- **Important:** 14 days minimum are required for the Time Fix to work correctly ([see guide](https://www.reddit.com/r/angrybirdstransform/comments/1ssj9wo/ultimate_guide_time_skip_glitch_in_angry_birds/))
- **Stop command:** unlocks after cycle 14 completes

### The Time Fix

After farming ends (or when you type `stop`), the script runs an automatic repair sequence:

1. Force-stops the game and clears it from memory
2. Calculates real-world time and sets the emulator clock to **23:59 of the previous day**
3. Relaunches the game via its native Activity path
4. **Your job:** stay on the map screen and wait until your device clock shows `00:00`

At midnight the game registers a natural day rollover, permanently restoring the calendar sync.

---

## 🛠 Prerequisites & Setup

Root access is required to change the system date on Android. The script will not work on an unrooted emulator.

### Required Software

| Software | Purpose |
|----------|---------|
| **Python 3.8+** | Run the script (no external libraries needed — stdlib only) |
| **BlueStacks 5** | Recommended Android emulator |
| **Magisk 27/BSTweaker** | Unlocks Root access in BlueStacks |
| **ADB** | Included in the repo — keep the 3 ADB files in the same folder as the scripts |

### Rooting BlueStacks

1. Visit **[BSTweaker homepage](https://bstweaker.ru/)** to learn how to root BlueStacks5
2. In BlueStacks, go to **Settings → Advanced** (or Developer Options)
3. Enable **Android Debug Bridge (ADB)**
4. Note your ADB port — usually `127.0.0.1:5575` or `127.0.0.1:5555`

---

## 🚀 Installation & Usage

### Step 1 — Clone the repository

```bash
git clone https://github.com/ArturPen/ab-transformers-time-skip.git
cd ab-transformers-time-skip
```

### Step 2 — Set your ADB address

Open `driver.py` and update the address in `__init__` to match your BlueStacks ADB port:

```python
def __init__(self, adb_address="127.0.0.1:5575"):
```

You can find the correct port in **BlueStacks → Settings → Advanced**.

### Step 3 — Adjust button coordinates (if needed)

The script is calibrated for **1920×1080** resolution. The Claim button is set to `X=720, Y=890` in `main.py`. If your resolution differs, update `BTN_X` and `BTN_Y`, or switch BlueStacks to 1920×1080 in its display settings.

### Step 4 — Launch

```bash
python main.py
```
Make sure `main.py`, `driver.py`, and the 3 ADB files (`adb.exe`, `AdbWinApi.dll`, `AdbWinUsbApi.dll`) are all in the same folder.

---

## ✨ Features

### Two farming modes
Gems-focused or resource-focused — each with its own skip strategy and loop calculation.

### Estimated time display
Before the loop starts, the script prints how long the full run will take based on an average cycle time of ~8 seconds.

### Safe Stop command
Type `stop` in the terminal and press **Enter** at any point. The script finishes the current cycle, runs the full Time Fix automatically, and logs the shutdown.

| Mode | When `stop` becomes available |
|------|-------------------------------|
| Mode 1 — Gems Farm | From cycle 1 |
| Mode 2 — Resources Farm | After cycle 14 completes |

Mode 2 enforces the 14-cycle minimum because the Time Fix requires that many days of accumulated skips to restore the calendar correctly. The terminal notifies you the moment `stop` becomes active.

### Real-time log file
The script generates `farm_log.txt` and opens it automatically on startup. Every cycle, time change, tap, and status message is written there so you can monitor the run without watching the terminal. On a stop-command shutdown, the log records:
```
[STOP] Program was stopped via the 'stop' command.
```

### Auto-recovery
Disables `auto_time` immediately on connect so Android doesn't override the script's date changes mid-run.

### Direct Activity launching
Uses native Android intents (`am start -S -W -n`) to wake the game directly, bypassing suspended-tab issues that affect normal app launches.

---

## ⚙️ Configuration

All user-adjustable values are at the top of each file:

**`driver.py`**
```python
adb_address = "127.0.0.1:5575"   # Your BlueStacks ADB port
package_name = "com.rovio.angrybirdstransformers"
```

**`main.py`**
```python
BTN_X, BTN_Y = 720, 890   # Claim button coordinates for 1920×1080
```

---

## 📝 Logging Reference

All messages follow the format `HH:MM:SS [LEVEL] message`. Key entries:

| Entry | Meaning |
|-------|---------|
| `[ACTION] Skipped forward N day(s)` | Time jump executed |
| `[TIME] Device time set to: DD.MM.YYYY HH:MM` | Clock confirmed |
| `[ACTION] Tapped coordinates: X=720, Y=890` | Claim button pressed |
| `[FIX] Reverting time to yesterday 23:59` | Time Fix started |
| `[SUCCESS] Game launched successfully` | Game is running |
| `[STOP] Program was stopped via the 'stop' command.` | Manual stop recorded |

---

*Developed by [ArturPen](https://github.com/ArturPen)*

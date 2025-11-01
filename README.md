# Sneaky Golem

Sneaky Golem is a lightweight Windows prank program that quietly waits a random amount of time, then fades in a small transparent image at a random position on the screen while looping a short sound.  
When the user moves the cursor over the image, the sound stops, the image fades out, and the program returns to its waiting state.

This project is intended purely for harmless, local use and demonstrates timing, transparency, and window control techniques in Python.

---

## Features

- Random delay between appearances (configurable)
- Smooth fade-in animation
- Looped sound while visible
- Immediate stop and hide on hover
- Random position on each appearance
- Hidden from taskbar and Alt+Tab (best effort on Windows)
- Always-on-top overlay window

---

## Requirements

- Windows 10 or 11  
- Python 3.8 or newer

Install dependencies:
```bash
python -m pip install pillow pyinstaller
```

Files required in the same directory:
```
golem_loop.py
golem.png
mystic.wav
```

---

## Running

Run directly from source:
```bash
python golem_loop.py
```

The image will appear after a random delay (default: 1–100 seconds).  
Hovering the mouse over it immediately stops the sound and hides the window.

---

## Building an Executable

To package it into a single `.exe` file (no console window):
```bash
python -m PyInstaller --onefile --noconsole ^
  --add-data "golem.png;." ^
  --add-data "mystic.wav;." ^
  golem_loop.py
```

The finished executable will be created under:
```
dist\golem_loop.exe
```

---

## Configuration

All behavior can be adjusted inside `golem_loop.py`:

| Variable | Description | Default |
|-----------|--------------|----------|
| `MIN_DELAY_S` / `MAX_DELAY_S` | Range for random wait time before appearing | 1 / 100 |
| `TARGET_WIDTH` | Width of the image in pixels (maintains aspect ratio) | 128 |
| `FADE_IN_MS` | Total fade-in duration (milliseconds) | 1500 |
| `FADE_STEPS` | Number of alpha steps during fade-in | 30 |
| `COOLDOWN_AFTER_FOUND_S` | Delay after disappearance before next loop | 1.0 |

---

## Notes

- Works best on Windows desktop environments and borderless windowed applications.
- Exclusive fullscreen applications may prevent the overlay from appearing.
- The process remains visible in Task Manager under its executable name.
- This project is for demonstration and entertainment purposes only. Use responsibly.

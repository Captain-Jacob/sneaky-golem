
A fun little time-killer / desktop curiosity project.

Every few minutes, a mysterious transparent image (“the golem”) briefly appears at a random spot on your screen.  
If your mouse touches it — *poof!* — it disappears with a sound. Then it hides again and waits for the next time.

---

## ✨ Features

- Random delay between appearances (`30–900s` by default)
- Transparent always-on-top image overlay (PNG)
- Plays a sound when your mouse enters the image
- Automatically hides and repeats forever
- Hides from Windows taskbar and Alt + Tab (best-effort)
- Works cross-platform (Windows, macOS, Linux)

---

## 🧩 Requirements

**Python 3.8+**  
and the following libraries:

```bash
pip install pillow simpleaudio
```

If you’re on Linux, you may also need:

```bash
sudo apt install python3-tk
```

---

## 📂 Files

```
golem_loop.py     # Main script
golem.png          # Transparent image that appears
mystic.wav         # Sound played when found
```

---

## ▶️ Usage

Run the script directly:

```bash
python golem_loop.py
```

Then just keep doing your work —  
after a random delay, the “golem” will silently appear somewhere on your screen.

Hover your mouse over it to make it vanish (and optionally play a sound).

---

## 🔇 Testing Without Sound

To test quietly, you can **disable sound** in any of these ways:

1. **Simplest:** Rename or delete the `mystic.wav` file  
   (the script will continue without audio)

2. **Code toggle:**  
   Edit `golem_loop.py` and replace this function:
   ```python
   def play_sound_nonblocking():
       pass  # disable sound
   ```

3. **Or** add a variable `ENABLE_SOUND = False` and skip playback in `_on_found()`.

---

## ⚙️ Configuration

You can tweak these constants near the top of `golem_loop.py`:

```python
MIN_DELAY_S = 30       # Minimum seconds between appearances
MAX_DELAY_S = 900      # Maximum seconds between appearances
MARGIN = 20            # Distance from screen edges
AUTO_HIDE_AFTER_S = None  # Auto-hide after N seconds (None = disabled)
```

---

## 🪄 Tips & Ideas

- Use your own transparent PNGs for fun effects
- Replace the sound with something spooky or funny
- Chain multiple images appearing in sequence
- Try making it fade in/out instead of popping instantly

---

## ⚠️ Notes

- The taskbar/Alt-Tab hiding trick uses Windows API calls and may not work on all systems.
- The program does not modify files or use networking — it’s safe to run.

---

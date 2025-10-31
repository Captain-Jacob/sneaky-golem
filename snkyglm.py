"""
golem_loop.py
Final PoC:
- Random delay (30..900s) then show transparent image at random position (always on top)
- Play sound when mouse enters the image; hide and repeat
- Hide main window from taskbar and Alt+Tab on Windows
- Works cross-platform for showing; Windows-only tricks used to hide taskbar icon
"""

import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import threading
import os
import sys
import simpleaudio
import ctypes

# ---------------- CONFIG ----------------
IMAGE_PATH = "golem.png"      # transparent PNG
SOUND_PATH = "mystic.wav"     # WAV sound
MIN_DELAY_S = 30              # minimum wait Seconds
MAX_DELAY_S = 900             # maximum wait Seconds
MARGIN = 20                   # margin from screen edges
AUTO_HIDE_AFTER_S = None      # optional: auto-hide after N seconds when shown (None = disabled)
COOLDOWN_AFTER_FOUND_S = 1.0  # short cooldown before next loop iteration
# ----------------------------------------

def resource_path(rel):
    """Support for PyInstaller onefile (sys._MEIPASS)"""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

def play_sound_nonblocking():
    try:
        path = resource_path(SOUND_PATH)
        if os.path.exists(path):
            wave = simpleaudio.WaveObject.from_wave_file(path)
            wave.play()  # non-blocking
    except Exception:
        pass

class GolemApp:
    def __init__(self, root):
        self.root = root
        self._stop = False
        self._visible = False

        self._load_assets()
        self._create_window()
        self._apply_windows_taskbar_hide()  # best-effort; Windows only

        # start loop thread
        t = threading.Thread(target=self._loop_thread, daemon=True)
        t.start()

    def _load_assets(self):
        img_path = resource_path(IMAGE_PATH)
        if not os.path.exists(img_path):
            print("Missing image:", img_path)
            sys.exit(1)
        self.pil_img = Image.open(img_path).convert("RGBA")
        self.img_w, self.img_h = self.pil_img.size
        self.tk_img = ImageTk.PhotoImage(self.pil_img)
        # warn if sound missing (not fatal)
        if not os.path.exists(resource_path(SOUND_PATH)):
            print("Warning: sound file missing. No audio will play.")

    def _create_window(self):
        # We use a Toplevel for the visible overlay; root is kept hidden to avoid taskbar icon.
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)  # no border, no titlebar
        try:
            # always on top
            self.win.attributes("-topmost", True)
            # transparency color key on Windows: use a color unlikely used in the image
            # we'll set background to that color and expect the PNG has alpha so it looks correct
            self.win.wm_attributes("-transparentcolor", "#00ff00")
        except tk.TclError:
            # some platforms/older Tk don't support this; it's best-effort
            pass
        self.win.config(bg="#00ff00")  # keyed color

        self.label = tk.Label(self.win, image=self.tk_img, bd=0, bg="#00ff00", highlightthickness=0)
        self.label.pack()

        # Bind enter to handle "found" event (mouse hover)
        self.label.bind("<Enter>", lambda e: self._on_found())
        self.win.bind("<Enter>", lambda e: self._on_found())

        # start withdrawn (hidden)
        self.win.withdraw()

    def _apply_windows_taskbar_hide(self):
        # Best-effort: hide the Python/Tk root from taskbar and Alt+Tab on Windows.
        # This manipulates extended window styles: removes WS_EX_APPWINDOW and adds WS_EX_TOOLWINDOW.
        # If not on Windows or if calls fail, we ignore silently.
        if sys.platform.startswith("win"):
            try:
                # Make root window truly hidden
                self.root.withdraw()
                self.root.update_idletasks()
                # Use the root's window handle
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd:
                    GWL_EXSTYLE = -20
                    WS_EX_APPWINDOW = 0x00040000
                    WS_EX_TOOLWINDOW = 0x00000080
                    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    style = (style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
                    # hide it from screen (we already withdrew)
            except Exception:
                pass
        else:
            # Non-Windows: we already withdraw root so usually no taskbar icon will appear.
            try:
                self.root.withdraw()
            except Exception:
                pass

    def _place_random(self):
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = random.randint(MARGIN, max(MARGIN, sw - self.img_w - MARGIN))
        y = random.randint(MARGIN, max(MARGIN, sh - self.img_h - MARGIN))
        self.win.geometry(f"+{x}+{y}")

    def _show(self):
        if self._visible: 
            return
        self._place_random()
        try:
            # show (on main thread)
            self.win.deiconify()
            # ensure topmost again
            try:
                self.win.lift()
                self.win.attributes("-topmost", True)
            except tk.TclError:
                pass
        except tk.TclError:
            pass
        self._visible = True
        # optional auto-hide timer
        if AUTO_HIDE_AFTER_S:
            self.root.after(int(AUTO_HIDE_AFTER_S*1000), self._hide)

    def _hide(self):
        if not self._visible:
            return
        try:
            self.win.withdraw()
        except tk.TclError:
            pass
        self._visible = False

    def _on_found(self):
        # Called when mouse enters image area
        if not self._visible:
            return
        # play sound async
        threading.Thread(target=play_sound_nonblocking, daemon=True).start()
        # hide immediately
        self._hide()

    def _loop_thread(self):
        # Main loop: wait random time, show, wait for "found", repeat
        while not self._stop:
            delay = random.randint(MIN_DELAY_S, MAX_DELAY_S)
            slept = 0.0
            # Sleep in small steps so we can exit quickly on stop
            while slept < delay and not self._stop:
                time.sleep(0.5)
                slept += 0.5
            if self._stop:
                break
            # Ask main thread to show overlay
            try:
                self.root.after(0, self._show)
            except Exception:
                break
            # Wait until next cycle; we don't block waiting for hover because hover handler hides it
            # Add a short cooldown to avoid immediate re-show
            cooldown = COOLDOWN_AFTER_FOUND_S
            slept2 = 0.0
            while slept2 < cooldown and not self._stop:
                time.sleep(0.2)
                slept2 += 0.2
        # cleanup on exit
        try:
            self.root.after(0, self._hide)
        except Exception:
            pass

    def stop(self):
        self._stop = True
        self._hide()

def main():
    # Create and hide root so it does not appear in taskbar
    root = tk.Tk()
    # Keep root withdrawn / invisible from start
    root.withdraw()
    root.overrideredirect(True)
    try:
        root.attributes("-alpha", 0.0)
    except Exception:
        pass

    app = GolemApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.stop()

if __name__ == "__main__":
    main()
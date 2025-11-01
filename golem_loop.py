"""
golem_loop.py (winsound, fade-in, play-while-visible)
- Random delay (MIN..MAX), then show a smaller transparent image at random place.
- Fades in smoothly. While visible, loops WAV; on hide, stops sound instantly.
- Hidden from taskbar/Alt+Tab as much as Tk allows (Windows tweaks included).
"""

import tkinter as tk
from PIL import Image, ImageTk
import random, time, threading, os, sys, ctypes

# ------------ CONFIG ------------
IMAGE_PATH = "golem.png"         # transparent PNG
SOUND_PATH = "mystic.wav"        # WAV file
MIN_DELAY_S = 1
MAX_DELAY_S = 100
MARGIN = 20
TARGET_WIDTH = 128               # shrink image to this width (keep aspect). Set None to keep original.
FADE_IN_MS = 1500                 # total fade duration in ms (0 = no fade)
FADE_STEPS = 30                  # number of alpha steps for fade-in
COOLDOWN_AFTER_FOUND_S = 1.0
# --------------------------------

IS_WINDOWS = sys.platform.startswith("win")
winsound = None
if IS_WINDOWS:
    try:
        import winsound  # built-in
    except Exception:
        winsound = None

def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

class GolemApp:
    def __init__(self, root):
        self.root = root
        self._stop = False
        self._visible = False
        self._currently_fading = False
        self._load_assets()
        self._create_window()
        self._apply_windows_taskbar_hide()
        threading.Thread(target=self._loop_thread, daemon=True).start()

    # ---------- assets ----------
    def _load_assets(self):
        img_path = resource_path(IMAGE_PATH)
        if not os.path.exists(img_path):
            print("Missing image:", img_path); sys.exit(1)

        pil = Image.open(img_path).convert("RGBA")
        if TARGET_WIDTH:
            w0, h0 = pil.size
            new_h = max(1, int(h0 * (TARGET_WIDTH / float(w0))))
            pil = pil.resize((TARGET_WIDTH, new_h), Image.LANCZOS)
        self.pil_img = pil
        self.img_w, self.img_h = pil.size
        self.tk_img = ImageTk.PhotoImage(pil)

        if not os.path.exists(resource_path(SOUND_PATH)) and winsound:
            print("Note: WAV not found; sound will be silent.")

    # ekran
    def _create_window(self):
        self.win = tk.Toplevel(self.root)
        self.win.overrideredirect(True)
        try:
            self.win.attributes("-topmost", True)
            self.win.wm_attributes("-transparentcolor", "#00ff00")  # chroma key
        except tk.TclError:
            pass
        self.win.config(bg="#00ff00")
        self.label = tk.Label(self.win, image=self.tk_img, bd=0, bg="#00ff00", highlightthickness=0)
        self.label.pack()
        self.label.bind("<Enter>", lambda e: self._on_found())
        self.win.bind("<Enter>",   lambda e: self._on_found())
        self.win.withdraw()

    def _apply_windows_taskbar_hide(self):
        if IS_WINDOWS:
            try:
                self.root.withdraw()
                self.root.update_idletasks()
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if hwnd:
                    GWL_EXSTYLE = -20
                    WS_EX_APPWINDOW = 0x00040000
                    WS_EX_TOOLWINDOW = 0x00000080
                    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                    style = (style & ~WS_EX_APPWINDOW) | WS_EX_TOOLWINDOW
                    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            except Exception:
                pass
        else:
            try: self.root.withdraw()
            except Exception: pass

    # ses
    def _start_sound(self):
        if not (winsound and os.path.exists(resource_path(SOUND_PATH))):
            return
        # loop asynchronously while visible; we’ll purge on hide
        try:
            winsound.PlaySound(resource_path(SOUND_PATH),
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        except Exception:
            pass

    def _stop_sound(self):
        if winsound:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    # gize kapat
    def _place_random(self):
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x = random.randint(MARGIN, max(MARGIN, sw - self.img_w - MARGIN))
        y = random.randint(MARGIN, max(MARGIN, sh - self.img_h - MARGIN))
        self.win.geometry(f"+{x}+{y}")

    def _fade_in(self):
        if FADE_IN_MS <= 0 or FADE_STEPS <= 1:
            return
        self._currently_fading = True
        step_ms = max(1, int(FADE_IN_MS / FADE_STEPS))
        def tick(i=0):
            if not self._visible:  # got hidden mid-fade
                self._currently_fading = False
                return
            alpha = (i + 1) / float(FADE_STEPS)
            try:
                self.win.attributes("-alpha", alpha)
            except tk.TclError:
                self._currently_fading = False
                return
            if i + 1 < FADE_STEPS:
                self.root.after(step_ms, lambda: tick(i + 1))
            else:
                self._currently_fading = False
        # saydamlık
        try:
            self.win.attributes("-alpha", 0.0)
        except tk.TclError:
            self._currently_fading = False
            return
        self.root.after(step_ms, tick)

    def _show(self):
        if self._visible: return
        self._place_random()
        try:
            self.win.deiconify()
            self.win.lift()
            self.win.attributes("-topmost", True)
        except tk.TclError:
            pass
        self._visible = True
        self._start_sound()    
        self._fade_in()       

    def _hide(self):
        if not self._visible: return
        self._stop_sound()      
        try:
            self.win.withdraw()
        except tk.TclError:
            pass
        self._visible = False

    # loop
    def _on_found(self):
        if not self._visible: return
        self._hide()

    def _loop_thread(self):
        while not self._stop:
            delay = random.randint(MIN_DELAY_S, MAX_DELAY_S)
            slept = 0.0
            while slept < delay and not self._stop:
                time.sleep(0.5); slept += 0.5
            if self._stop: break
            try:
                self.root.after(0, self._show)
            except Exception:
                break
            
            t = 0.0
            while t < COOLDOWN_AFTER_FOUND_S and not self._stop:
                time.sleep(0.2); t += 0.2
        try:
            self.root.after(0, self._hide)
        except Exception:
            pass

    def stop(self):
        self._stop = True
        self._hide()

def main():
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    try: root.attributes("-alpha", 0.0)
    except Exception: pass
    app = GolemApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.stop()

if __name__ == "__main__":
    main()

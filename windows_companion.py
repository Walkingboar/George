"""Windows companion for the RP2040 macro pad.

Install: py -m pip install pyserial winsdk
Run:     py windows_companion.py

The app sends Windows Media Session metadata (Spotify and browsers that publish a
media session) to the Pico over USB serial. It is a starter implementation: exact
song/difficulty/star-rating data for osu! is not exposed by the Windows media API.
"""
import asyncio
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None
    list_ports = None

try:
    from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
except ImportError:
    GlobalSystemMediaTransportControlsSessionManager = None

MODES = ("AUTO", "SPOTIFY", "YOUTUBE", "OSU", "CUSTOM")

class Companion:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Pad Companion")
        self.root.geometry("460x380")
        self.port = None
        self.running = True
        self.mode = "AUTO"
        self.username = tk.StringVar(value="Player")
        self.status = tk.StringVar(value="Not connected")
        self.title_text = tk.StringVar(value="Waiting for media…")
        self.artist_text = tk.StringVar(value="")
        self._build_ui()
        self.refresh_ports()
        threading.Thread(target=self.media_loop, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}
        ttk.Label(self.root, text="MACRO PAD COMPANION", font=("Segoe UI", 15, "bold")).pack(**pad)
        ttk.Label(self.root, textvariable=self.status).pack(**pad)
        row = ttk.Frame(self.root); row.pack(fill="x", **pad)
        self.port_combo = ttk.Combobox(row, state="readonly", width=20)
        self.port_combo.pack(side="left", padx=4)
        ttk.Button(row, text="Refresh", command=self.refresh_ports).pack(side="left", padx=4)
        ttk.Button(row, text="Connect", command=self.connect).pack(side="left", padx=4)
        ttk.Label(self.root, text="Mode (select what the screen/buttons should target):").pack(**pad)
        mode_row = ttk.Frame(self.root); mode_row.pack(**pad)
        for m in MODES:
            ttk.Button(mode_row, text=m, command=lambda m=m: self.set_mode(m)).pack(side="left", padx=2)
        ttk.Separator(self.root).pack(fill="x", padx=12, pady=8)
        ttk.Label(self.root, text="Now playing", font=("Segoe UI", 11, "bold")).pack()
        ttk.Label(self.root, textvariable=self.title_text, wraplength=420).pack(**pad)
        ttk.Label(self.root, textvariable=self.artist_text, wraplength=420).pack(**pad)
        userrow = ttk.Frame(self.root); userrow.pack(**pad)
        ttk.Label(userrow, text="osu! username:").pack(side="left")
        ttk.Entry(userrow, textvariable=self.username, width=22).pack(side="left", padx=5)
        ttk.Button(userrow, text="Send username", command=self.send_username).pack(side="left")
        ttk.Label(self.root, text="Custom background: copy a 170×320 or 320×170 BMP named background.bmp to CIRCUITPY.\nScreen dimensions/rotation depend on your exact ST7789 module.", wraplength=430).pack(**pad)

    def refresh_ports(self):
        if list_ports is None:
            self.status.set("Install dependencies: py -m pip install pyserial winsdk")
            return
        ports = [p.device for p in list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and not self.port_combo.get():
            self.port_combo.current(0)

    def connect(self):
        if serial is None:
            messagebox.showerror("Missing package", "Run: py -m pip install pyserial winsdk")
            return
        port_name = self.port_combo.get()
        if not port_name:
            messagebox.showwarning("Select a port", "Choose the Pico's USB CDC data port first.")
            return
        try:
            if self.port:
                self.port.close()
            self.port = serial.Serial(port_name, 115200, timeout=0.1)
            time.sleep(1.0)
            self.status.set("Connected to " + port_name)
            self.send({"mode": self.mode})
        except Exception as exc:
            self.port = None
            messagebox.showerror("Connection failed", str(exc))

    def send(self, payload):
        if not self.port:
            return
        try:
            self.port.write((json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8"))
        except Exception as exc:
            self.root.after(0, lambda: self.status.set("Serial error: " + str(exc)))

    def set_mode(self, mode):
        self.mode = mode
        self.send({"mode": mode})
        self.status.set("Mode: " + mode + (" (not connected)" if not self.port else ""))

    def send_username(self):
        self.send({"media": {"username": self.username.get()}})
        self.status.set("Username sent")

    def media_loop(self):
        if GlobalSystemMediaTransportControlsSessionManager is None:
            self.root.after(0, lambda: self.status.set("Install winsdk for media metadata: py -m pip install winsdk"))
            return
        while self.running:
            try:
                asyncio.run(self.read_media_once())
            except Exception:
                pass
            time.sleep(2.0)

    async def read_media_once(self):
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        sessions = list(manager.get_sessions())
        best = None
        for session in sessions:
            try:
                props = await session.try_get_media_properties_async()
                title = str(props.title or "")
                artist = str(props.artist or "")
                app = str(session.source_app_user_model_id or "")
                if title or artist:
                    best = {"title": title, "artist": artist, "app": app, "status": "Playing/available"}
                    if "spotify" in app.lower():
                        break
            except Exception:
                continue
        if best:
            self.root.after(0, lambda b=best: self._update_media_ui(b))
            self.send({"media": best})

    def _update_media_ui(self, data):
        self.title_text.set(data.get("title", ""))
        self.artist_text.set(data.get("artist", ""))

    def close(self):
        self.running = False
        try:
            if self.port:
                self.port.close()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Companion(root)
    root.mainloop()

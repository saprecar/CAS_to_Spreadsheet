"""
browser_launcher.py
Detects installed browsers on Windows / macOS / Linux and shows a selection
dialog using tkinter (Python built-in — no extra dependencies).
Falls back to the OS default browser if tkinter is unavailable.
"""
import os
import sys
import platform
import subprocess
import webbrowser

APP_URL = "http://127.0.0.1:8000"

# ---------------------------------------------------------------------------
# Browser definitions per OS
# ---------------------------------------------------------------------------

WINDOWS_BROWSERS = [
    {
        "name": "Google Chrome",
        "paths": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
    },
    {
        "name": "Microsoft Edge",
        "paths": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
    },
    {
        "name": "Mozilla Firefox",
        "paths": [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
    },
    {
        "name": "Brave Browser",
        "paths": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
    },
    {
        "name": "Opera",
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\launcher.exe"),
            r"C:\Program Files\Opera\launcher.exe",
        ],
    },
    {
        "name": "Vivaldi",
        "paths": [
            os.path.expandvars(r"%LOCALAPPDATA%\Vivaldi\Application\vivaldi.exe"),
        ],
    },
]

MAC_BROWSERS = [
    {"name": "Google Chrome",  "app": "Google Chrome",  "cmd": ["open", "-a", "Google Chrome",  APP_URL]},
    {"name": "Mozilla Firefox","app": "Firefox",         "cmd": ["open", "-a", "Firefox",         APP_URL]},
    {"name": "Safari",         "app": "Safari",          "cmd": ["open", "-a", "Safari",          APP_URL]},
    {"name": "Microsoft Edge", "app": "Microsoft Edge",  "cmd": ["open", "-a", "Microsoft Edge",  APP_URL]},
    {"name": "Brave Browser",  "app": "Brave Browser",   "cmd": ["open", "-a", "Brave Browser",   APP_URL]},
    {"name": "Opera",          "app": "Opera",           "cmd": ["open", "-a", "Opera",           APP_URL]},
    {"name": "Vivaldi",        "app": "Vivaldi",         "cmd": ["open", "-a", "Vivaldi",         APP_URL]},
]

LINUX_BROWSERS = [
    {"name": "Google Chrome",  "cmd": ["google-chrome",  APP_URL]},
    {"name": "Chromium",       "cmd": ["chromium-browser",APP_URL]},
    {"name": "Mozilla Firefox","cmd": ["firefox",         APP_URL]},
    {"name": "Microsoft Edge", "cmd": ["microsoft-edge",  APP_URL]},
    {"name": "Brave Browser",  "cmd": ["brave-browser",   APP_URL]},
    {"name": "Opera",          "cmd": ["opera",           APP_URL]},
    {"name": "Vivaldi",        "cmd": ["vivaldi",         APP_URL]},
]


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def _detect_windows():
    found = []
    for b in WINDOWS_BROWSERS:
        for path in b["paths"]:
            if os.path.isfile(path):
                found.append({"name": b["name"], "path": path})
                break
    return found


def _detect_mac():
    found = []
    app_dir = "/Applications"
    for b in MAC_BROWSERS:
        app_path = os.path.join(app_dir, f"{b['app']}.app")
        if os.path.isdir(app_path):
            found.append({"name": b["name"], "cmd": b["cmd"]})
    return found


def _detect_linux():
    found = []
    for b in LINUX_BROWSERS:
        exe = b["cmd"][0]
        result = subprocess.run(["which", exe], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            found.append({"name": b["name"], "cmd": b["cmd"]})
    return found


def detect_browsers():
    """Return list of dicts: [{name, path/cmd}, ...]"""
    system = platform.system()
    if system == "Windows":
        return _detect_windows(), "windows"
    elif system == "Darwin":
        return _detect_mac(), "mac"
    else:
        return _detect_linux(), "linux"


# ---------------------------------------------------------------------------
# Launch helpers
# ---------------------------------------------------------------------------

def _launch(browser, system):
    try:
        if system == "windows":
            subprocess.Popen([browser["path"], APP_URL])
        else:
            subprocess.Popen(browser["cmd"])
    except Exception as e:
        print(f"Could not open {browser['name']}: {e}")
        webbrowser.open(APP_URL)


def _open_default():
    webbrowser.open(APP_URL)


# ---------------------------------------------------------------------------
# Tkinter dialog
# ---------------------------------------------------------------------------

def _show_dialog(browsers, system):
    """Show a small browser-picker dialog. Returns True if dialog shown."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        return False

    chosen = {"browser": None}

    root = tk.Tk()
    root.title("Open CAS Parser")
    root.resizable(False, False)

    # Center on screen
    root.update_idletasks()
    w, h = 360, 280
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w)//2}+{(sh - h)//2}")

    # Style
    bg = "#1e1e2e"
    fg = "#cdd6f4"
    btn_bg = "#313244"
    btn_hover = "#45475a"
    accent = "#89b4fa"

    root.configure(bg=bg)

    title_lbl = tk.Label(
        root,
        text="CAS Parser is ready!",
        font=("Segoe UI", 13, "bold"),
        bg=bg, fg=accent
    )
    title_lbl.pack(pady=(18, 2))

    sub_lbl = tk.Label(
        root,
        text="Select a browser to open the app:",
        font=("Segoe UI", 10),
        bg=bg, fg=fg
    )
    sub_lbl.pack(pady=(0, 12))

    frame = tk.Frame(root, bg=bg)
    frame.pack(fill="both", expand=True, padx=20)

    def make_btn(name, action):
        btn = tk.Button(
            frame,
            text=name,
            font=("Segoe UI", 10),
            bg=btn_bg, fg=fg,
            activebackground=btn_hover,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=10, pady=6,
            command=action
        )
        btn.pack(fill="x", pady=3)
        btn.bind("<Enter>", lambda e: btn.config(bg=btn_hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=btn_bg))
        return btn

    for b in browsers:
        b_copy = b  # capture loop var
        make_btn(b_copy["name"], lambda br=b_copy: [chosen.__setitem__("browser", br), root.destroy()])

    sep = tk.Frame(root, bg="#45475a", height=1)
    sep.pack(fill="x", padx=20, pady=8)

    make_btn("Default Browser", lambda: [chosen.__setitem__("browser", "default"), root.destroy()])

    url_lbl = tk.Label(
        root,
        text=f"Or visit: {APP_URL}",
        font=("Segoe UI", 8),
        bg=bg, fg="#6c7086",
        cursor="hand2"
    )
    url_lbl.pack(pady=(0, 12))
    url_lbl.bind("<Button-1>", lambda e: [chosen.__setitem__("browser", "default"), root.destroy()])

    root.mainloop()

    # Act on selection
    sel = chosen["browser"]
    if sel == "default" or sel is None:
        _open_default()
    else:
        _launch(sel, system)

    return True


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def open_browser_picker():
    """
    Detect installed browsers and show a picker dialog.
    Falls back to OS default if tkinter is unavailable or no browsers found.
    """
    import time
    time.sleep(1.5)   # Wait for uvicorn to bind

    browsers, system = detect_browsers()

    if not browsers:
        # No browsers detected — just open OS default
        print(f"\n  No browsers detected. Opening default browser...")
        print(f"  URL: {APP_URL}\n")
        _open_default()
        return

    if len(browsers) == 1:
        # Only one browser installed — open it directly, no dialog needed
        print(f"\n  Opening {browsers[0]['name']}...")
        print(f"  URL: {APP_URL}\n")
        _launch(browsers[0], system)
        return

    # Multiple browsers — show dialog
    shown = _show_dialog(browsers, system)
    if not shown:
        # tkinter not available (headless server) — just open default
        print(f"\n  Server ready at: {APP_URL}")
        print(f"  (tkinter unavailable — open the URL manually)\n")

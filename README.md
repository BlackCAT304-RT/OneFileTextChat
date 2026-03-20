# OneFileTextChat

> A minimalist, serverless peer-to-peer chat — one Python file, zero dependencies beyond the standard library.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange)

---

## What is it?

**OneFileTextChat** is a direct, no-frills text messenger that connects two people over TCP/IP — no servers, no accounts, no cloud. One person creates a chat, the other connects. That's it.

The entire application lives in a single `.py` file. Run it, share your IP and port, start chatting.

---

## Features

- **P2P TCP connection** — direct socket communication, no relay servers
- **UPnP port forwarding** — automatic router port mapping via `miniupnpc` (falls back gracefully)
- **External IP detection** — fetches your public IP automatically when hosting
- **Dark & Light themes** — toggle with one click, preference saved between sessions
- **12 interface languages** — switch instantly from the sidebar:
  English, Русский, Українська, Deutsch, Français, Español, Polski, Português, Italiano, 中文, 日本語, 한국어
- **Chat history** — last 200 messages saved locally in `OFTC_Save.ini`
- **System tray support** — minimize to tray, receive toast notifications when the window is hidden
- **Toast notifications** — slide-in popup when a message arrives in the background
- **PyInstaller-ready** — compiles cleanly into a standalone `.exe`
- **Saves state** — username, theme, language, window geometry, and chat history persist across restarts

---

## Requirements

**Core (no install needed):**
```
Python 3.8+   — tkinter is part of the standard library
```

**Optional (enhanced features):**
```
miniupnpc     — automatic UPnP port forwarding
pystray       — system tray icon
Pillow        — tray icon rendering
```

Install optional dependencies:
```bash
pip install miniupnpc pystray Pillow
```

---

## Usage

```bash
python OneFileMesseger.py
```

**To host a chat:**
1. Click **Create Chat** in the sidebar
2. Choose a port (random one is pre-filled)
3. Share your **external IP** and **port** with your contact
4. Wait for them to connect

**To join a chat:**
1. Click **Connect** in the sidebar
2. Enter your contact's IP address and port
3. Hit Connect

---

## Building a standalone executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=DATA/ico.ico OneFileMesseger.py
```

The compiled `.exe` will be in the `dist/` folder. Place the `DATA/` folder alongside it.

---

## Project structure

```
OneFileMesseger.py   ← the entire application
DATA/
  ico.ico            ← window & tray icon (optional)
OFTC_Save.ini        ← auto-created on first run (settings + history)
```

---

## How it works

Two instances communicate directly over a raw TCP socket. One runs as a **server** (listens for a connection), the other as a **client** (connects to the server's address). Messages are JSON-encoded packets:

```json
{ "type": "msg",   "name": "Alice", "text": "Hello!" }
{ "type": "hello", "name": "Alice" }
```

No encryption is applied — this is a local-network / trusted-connection tool.

---

## License

MIT — do whatever you want with it.

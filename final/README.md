# Broadlink – Control Hub

A modern, dark - themed GUI desktop application for managing, capturing, and transmitting IR (Infrared) and RF (433MHz/315MHz) signals using **Broadlink** devices.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ Features

- 🎨 \\Cyber-Dark UI://                 Built with Tkinter, featuring live visual LED status indicators.
- 📡 \\IR & RF 433/315 MHz Support://   Full two-step RF frequency sweep and packet capturing.
- 🔍 \\Auto-Discovery://                Automatically scans your local network to discover Broadlink IP and MAC parameters.
- 🗄️ \\JSON Database://                 Save and organize signals with tags, dates, and categories.
- 📂 \\Export Options://                Export signals directly into `.txt` hex format.
- 💾 \\Auto-Config Persistence://       Remembers last valid connections effortlessly.

---

## 🚀 Quick Start (Executable)

If you just want to run the program without installing Python:
1. Go to the **[Releases](../../releases)** section on the right.
2. Download the latest `BroadlinkControlHub.exe`.
3. Launch and enjoy!

---

## 🛠️ Running from Source

### Prerequisites
- Python 3.10 or higher
- Installed dependencies:

pip install broadlink

### Run Application
Launch the application directly using Python:

python app.py

### Build Executable (.exe)
To compile the script into a single, standalone Windows .exe file with an embedded icon:

Install PyInstaller:

pip install pyinstaller
Build the app:

pyinstaller --noconsole --onefile --icon=ir.ico --add-data "ir.ico;." app.py
Your compiled executable will be waiting for you in the dist/ directory!

### Usage
Connect: Click Auto-Discovery to automatically locate your RM4 Pro, or type your IP/MAC manually and click Connect.

Learn IR: Enter a name for the command, click Learn IR, and press a button on your IR remote.

Learn RF: Click Learn RF, hold down the button on your RF remote to detect frequency, then press it repeatedly when prompted to grab the data packet.

Transmit: Select any code from the table and double-click or click Transmit Code.

### License
This project is licensed under the MIT License - see the LICENSE file for details.
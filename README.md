[![Release](https://img.shields.io/github/v/release/ArTeXa7/SwitchPulse?color=blue&label=Latest%20Release)](https://github.com/ArTeXa7/SwitchPulse/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)

# SwitchPulse ⚡

<p align="center">
  <img src="assets/icon.ico" width="128" height="128" alt="SwitchPulse Logo">
  <br>
  <b>Multi-Vendor Network Automation & Switch Diagnostics Desktop Utility</b>
  <br>
  <i>Tailored for ISP NOC engineers, network administrators, and field technicians.</i>
</p>

---

## 🚀 Overview

**SwitchPulse** is an open-source, modular desktop application built with Python and CustomTkinter, designed to streamline switch diagnostics, port monitoring, VLAN auditing, and automated provisioning across multi-vendor networks (Cisco IOS, Raisecom ROS, D-Link, etc.).

It replaces cumbersome CLI sessions and manual spreadsheets with an intuitive dashboard, zero-dependency configuration templates, and a built-in mock testing environment.

---

## ✨ Key Features

- **Multi-Vendor Polling Architecture:** Fully decoupled YAML-driven polling definitions. Easily add or modify vendor commands, regex extractors, and port-state normalizers without altering Python code.
- **Real-Time Interface Matrix:** Inspect port link status, descriptions, speed/duplex, and highlight CRC errors for quick physical-layer troubleshooting.
- **VLAN & MAC Audit:** Automatically cross-reference active VLAN definitions against MAC address tables to identify orphaned and unused VLANs.
- **Port Provisioning (Jinja2):** Standardize interface configurations with parametric Jinja2 templates (access ports, dot1q trunks, storm control).
- **Secure Profile Management:** Store switch credentials and management endpoints locally with seamless switching.
- **Built-in Mock Mode:** Full offline simulation mode enabling UI testing and demonstration without physical hardware.

---

## 🛠️ Supported Vendors (Out-of-the-Box)

- **Cisco Systems:** Catalyst IOS (e.g., 2960, 3560, 3750)
- **Raisecom:** ROS-based Metro-Ethernet switches (e.g., ISCOM2600/2900 series)
- **D-Link:** DES/DGS managed access switches

*Custom templates can be added under `./vendors/` using standard YAML syntax.*

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.11 or 3.12 (recommended)
- Windows 10/11

### Quick Start (Local Run)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ArTeXa7/SwitchPulse.git
   cd SwitchPulse
   ```

2. **Create and activate a virtual environment:**

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Launch the application:**

   ```powershell
   python main.py
   ```

---

## 🏗️ Project Architecture

```text
SwitchPulse/
├── assets/                  # Icons and visual UI assets
├── core/
│   ├── auditor.py           # Orphaned VLAN & traffic analytics
│   ├── connector.py         # Netmiko SSH/Telnet wrapper with Mock support
│   ├── parsers.py           # Dynamic YAML-based TextFSM / Regex parser engine
│   ├── profiles.py          # Pydantic data models & credential stores
│   └── template_manager.py  # YAML template loader and validator
├── ui/
│   ├── app.py               # Main Tkinter application orchestrator
│   ├── sidebar.py           # Quick-connect controls and credentials picker
│   ├── settings_overlay.py  # In-App modal for templates, theme, and config
│   └── tabs/
│       ├── ports_tab.py     # Port matrix & CRC error monitor
│       ├── vlans_tab.py     # VLAN audit visualization
│       └── provision_tab.py # Jinja2 configuration pusher
├── vendors/                 # YAML vendor definitions (Cisco, Raisecom, D-Link)
├── main.py                  # Process entry point
└── requirements.txt         # Project dependencies
```

---

## 🔨 Building Standalone Executable

To compile a standalone Windows build with the application icon bundled:

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --icon "assets/icon.ico" --add-data "vendors;vendors" --add-data "assets;assets" main.py
```

The compiled output will be located in `./dist/main/`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

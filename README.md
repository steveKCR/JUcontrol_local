# JUcontrol local

[![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/itsh-neumeier/JUcontrol_local)](https://github.com/itsh-neumeier/JUcontrol_local/releases)

A **local-only** Home Assistant integration for JUDO water treatment devices. Communicates directly with the device on your local network — no cloud dependency.

---

## Features

- **100% Local** — Communicates directly via the device's REST API on your LAN
- **Auto-Detection** — Automatically identifies the connected JUDO device model
- **Full Sensor Support** — Water hardness, salt supply, water volumes, operating hours, and more
- **Device Control** — Start regeneration, toggle leak protection, set vacation mode, adjust settings
- **Configurable Polling** — Choose your update interval: 30 s, 1 min, 2 min, 5 min, or 10 min
- **Multi-Language** — English and German translations included
- **Diagnostics** — Built-in diagnostics support for troubleshooting

---

## Supported Devices

| Device | Type | Key Features |
|---|---|---|
| **i-soft SAFE+** / **i-soft K SAFE+** | Water Softener | Softening, Leak Protection, Salt Monitoring |
| **i-soft PRO** / **i-soft PRO L** | Water Softener | Softening, Leak Protection, Scenes |
| **i-soft** / **i-soft K** | Water Softener | Softening, Leak Alarm |
| **SOFTwell P / S / K / KP / KS** | Water Softener | Basic Softening, Statistics |
| **ZEWA i-SAFE** / **PROM-i-SAFE** / **ZEWA i-SAFE FILT** | Leak Protection | Standalone Leak Protection, Absence Management |
| **i-dos eco** | Dosing Pump | Chemical Dosing, Pump Control |
| **i-fill 60** | Heating Fill System | Heating Circuit Fill, Valve Control |

---

## Installation

### HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Click the three dots in the top-right corner and select **Custom repositories**.
3. Add `https://github.com/itsh-neumeier/JUcontrol_local` as an **Integration**.
4. Search for **JUcontrol local** and click **Download**.
5. Restart Home Assistant.

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/itsh-neumeier/JUcontrol_local/releases).
2. Copy the `custom_components/jucontrol_local` folder to your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **JUcontrol local**.
3. Enter your device details:

| Parameter | Description | Default |
|---|---|---|
| **Host** | IP address of your JUDO device | *(required)* |
| **Username** | API username | `admin` |
| **Password** | API password | `Connectivity` |
| **Polling Interval** | How often to query the device | `1 minute` |

4. The integration will auto-detect your device model and create the appropriate entities.

### Changing the Polling Interval

After setup, you can change the polling interval at any time:

1. Go to **Settings** > **Devices & Services**.
2. Find your JUDO device and click **Configure**.
3. Select a new polling interval and save.

---

## Available Entities

Entities are automatically created based on the detected device type and its capabilities. Not all entities are available for every device model.

### Sensors

| Entity | Description | Device Types |
|---|---|---|
| Water Hardness | Current desired water hardness (°dH) | i-soft variants |
| Salt Supply | Current salt weight (kg) | i-soft variants |
| Salt Range | Estimated salt range (days) | i-soft variants |
| Salt Shortage Warning | Warning threshold (days) | i-soft variants |
| Total Water Volume | Total water consumed (m³) | Most devices |
| Soft Water Volume | Soft water produced (m³) | Softener devices |
| Operating Days | Total operating days | All devices |
| Current Flow Rate | Current water flow (L/h) | i-dos eco |
| Container Remaining | Dosing agent remaining (L) | i-dos eco |
| Max Fill Pressure | Maximum fill pressure (bar) | i-fill 60 |
| Cartridge Type | Installed cartridge type | i-fill 60 |

### Buttons

| Entity | Description | Device Types |
|---|---|---|
| Start Regeneration | Triggers a manual regeneration cycle | i-soft variants |
| Reset Notification | Resets active notifications | ZEWA i-SAFE |
| Start Micro-Leak Test | Runs a micro-leak detection test | ZEWA i-SAFE |
| Start Learning Mode | Starts the learning mode | ZEWA i-SAFE |

### Switches

| Entity | Description | Device Types |
|---|---|---|
| Leak Protection | Closes/opens the leak protection valve | i-soft SAFE+, ZEWA |
| Sleep Mode | Enables/disables sleep mode | ZEWA i-SAFE |

### Selects

| Entity | Options | Device Types |
|---|---|---|
| Vacation Mode | Off, U1, U2, U3 | i-soft variants, ZEWA |
| Hardness Unit | °dH, °eH, °fH, gpg, ppm, mmol, mval | i-soft variants |
| Pump Operation Mode | Off, Auto, Manual, Single | i-dos eco |
| Fill Valve Mode | Auto, Manual Open, Manual Close | i-fill 60 |
| Micro-Leak Mode | Disabled, Notify Only, Notify and Close | ZEWA i-SAFE |

### Numbers

| Entity | Range | Device Types |
|---|---|---|
| Desired Water Hardness | 1–30 °dH | i-soft variants |
| Salt Supply (set) | 0–50,000 g | i-soft variants |
| Salt Shortage Warning (set) | 1–90 days | i-soft variants |
| Max Extraction Duration | 0–255 min | i-soft variants |
| Max Extraction Volume | 0–65,535 L | i-soft variants |
| Max Flow Rate | 0–65,535 L/h | i-soft variants |
| Sleep Mode Duration | 1–10 h | ZEWA i-SAFE |

### Binary Sensors

| Entity | Description | Device Types |
|---|---|---|
| Learning Mode Active | Whether learning mode is currently active | ZEWA i-SAFE |

---

## Network Requirements

- The JUDO device must be on the **same local network** as your Home Assistant instance.
- Communication uses **HTTP** (port 80) with **Basic Authentication**.
- No internet connection is required — all communication is local.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **Cannot connect** | Verify the IP address is correct and the device is powered on. Ensure Home Assistant can reach the device (same VLAN/subnet). |
| **Invalid authentication** | Check username and password. Default credentials are `admin` / `Connectivity`. |
| **Unknown device** | The device type is not yet supported. Please open an issue on GitHub with your device model. |
| **Entities not updating** | Check the polling interval in the integration options. Verify network connectivity to the device. |
| **Entities show "unavailable"** | The device may be temporarily unreachable. Check your network and device status. |

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/).
4. Push to your branch and open a Pull Request.

If you have a JUDO device model that is not yet supported, please open an issue with the device type code (readable via the integration's diagnostics).

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This integration is **not affiliated with, endorsed by, or connected to JUDO Wasseraufbereitung GmbH**. JUDO, i-soft, SOFTwell, ZEWA, i-dos, and i-fill are trademarks of JUDO Wasseraufbereitung GmbH. Use this integration at your own risk.

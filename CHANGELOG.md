# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-03-14

### Added

- Home Assistant 2026.3+ integration branding assets under `custom_components/jucontrol_local/brand/`
- Local brand files: `icon.png`, `icon@2x.png`, `logo.png`, `logo@2x.png`

## [1.1.1] - 2026-03-07

### Fixed

- Water volume sensors (total water, soft water) now correctly display in m³ instead of HA converting back to liters
- Salt supply number entity changed from grams to kilograms (0–50 kg, step 0.1 kg)

## [1.1.0] - 2026-03-07

### Changed

- Renamed integration from "JUDO JUcontrol Local" to "JUcontrol local"
- Total water volume and soft water volume now displayed in m³ instead of liters
- Vacation mode changed from simple on/off switch to dropdown select with modes: Off, U1, U2, U3

### Added

- Integration icon
- Vacation mode select entity for softener and ZEWA devices with multiple modes (Off, U1, U2, U3)

### Removed

- Vacation mode switch (replaced by vacation mode select)

## [1.0.0] - 2025-03-07

### Added

- Initial release of JUcontrol local integration
- Support for all major JUDO device families:
  - **i-soft SAFE+** / **i-soft K SAFE+** (water softener with leak protection)
  - **i-soft PRO** / **i-soft PRO L** (water softener with leak protection and scenes)
  - **i-soft** / **i-soft K** (water softener with leak alarm)
  - **SOFTwell P / S / K / KP / KS** (basic water softener)
  - **ZEWA i-SAFE** / **PROM-i-SAFE** / **ZEWA i-SAFE FILT** (leak protection)
  - **i-dos eco** (dosing pump)
  - **i-fill 60** (heating fill system)
- Auto-detection of device type during setup
- Configurable polling interval (30s, 1min, 2min, 5min, 10min)
- **Sensors**: water hardness, salt supply (weight & range), total/soft water volume, operating hours, extraction limits, dosing status, fill pressure, and more
- **Buttons**: start regeneration, reset notification, start micro-leak test, start learning mode
- **Switches**: leak protection, sleep mode
- **Numbers**: desired water hardness, salt supply, salt shortage warning, max extraction duration/volume/flow rate, sleep duration
- **Selects**: hardness unit, vacation mode, pump operation mode, fill valve mode, micro-leak mode
- **Binary Sensors**: learning mode active
- Options flow for changing polling interval after setup
- English and German translations
- Diagnostics support
- MIT License

[1.2.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.2.0
[1.1.1]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.1.1
[1.1.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.1.0
[1.0.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.0.0

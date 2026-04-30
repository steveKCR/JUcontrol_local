# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.6.2] - 2026-04-30

### Fixed

- **Auto-disable legacy entities on upgrade**: Existing installations now automatically disable the entities that became `entity_registry_enabled_default=False` in v1.6.0/v1.6.1 (vacation mode, scenes, set-numbers, advanced sensors, regeneration/salt buttons). Migration runs once per config entry; a flag is stored in `entry.data` to prevent re-running. Users can still manually re-enable any entity in Settings → Devices → JUcontrol → Entities

## [1.6.1] - 2026-04-30

### Fixed

- **Flow rate accuracy**: `_prev_total_water` and timestamp are now only committed after a fully successful coordinator update cycle — prevents a false delta if a later API call fails in the same cycle
- **Water hardness dropdown**: guard against device returning value 0 (not a valid option) — select shows unknown instead of crashing
- **`salt_range` sensor**: added `native_unit_of_measurement=UnitOfTime.DAYS` for correct dashboard and history display
- **All ZEWA buttons** (`reset_notification`, `start_micro_leak_test`, `start_learning_mode`) now disabled by default, consistent with softener buttons
- **Removed unused** `DEFAULT_PORT` constant from `const.py`

## [1.6.0] - 2026-04-30

### Added

- **Water hardness dropdown select** (`set_water_hardness_select`): replaces the slider for setting desired water hardness — full dropdown with 1–30 °dH; reads back current value from device; restores last selection after HA restart
- **Total water volume in liters** sensor (`total_water_liters`): raw liter counter alongside the existing m³ sensor
- **Softened water in liters** sensor (`soft_water_liters`): raw liter counter alongside the existing m³ sensor

### Changed

- **`current_flow_rate`** sensor is now enabled by default (was disabled)
- Renamed total/soft water sensor labels to clarify unit in name (m³ vs liters)
- **Disabled by default** (can be re-enabled in entity registry): `set_water_hardness` number, `set_salt_supply` number, `salt_refill_25kg` button, `start_regeneration` button, vacation mode selects, scene selects

## [1.5.0] - 2026-04-30

### Added

- **"Salz nachgefüllt (25 kg)" button** (`salt_refill_25kg`): One-tap button that sets salt supply to 25 kg — no manual input needed
- **Select state persistence** (`RestoreEntity`): Vacation mode and water scene selects now restore their last known value after HA restart instead of showing "Unknown"; initial default is "off" / "Normalbetrieb" for new installations

### Changed

- **Valve initial state**: Leak protection valve now starts as "open" (assumed) instead of unknown, eliminating the confusing lightning-bolt icon
- **Water hardness number**: Switched to slider mode for easier adjustment
- **Diagnostic / advanced entities disabled by default** (can be re-enabled individually in HA): `hardness_unit` select, `set_salt_shortage_warning`, `set_max_extraction_duration`, `set_max_extraction_volume`, `set_max_flow_rate` numbers, `salt_shortage_warning`, `max_extraction_duration`, `max_extraction_volume`, `max_flow_rate`, `operating_days`, `commissioning_date`, `service_address` sensors

## [1.4.0] - 2026-04-30

### Added

- **Water scene select for i-soft SAFE+ / i-soft K SAFE+ / i-soft** (`isoft_scene`): 5 preset water scenes (Normalbetrieb, Duschen, Gartenbewässerung, Heizungsbefüllung, Waschen) via cmd `0x36`; new `WATER_SCENES` capability added to `_SOFTENER_LEAK` and `_SOFTENER_ALARM` device sets
- **Example Lovelace dashboard** (`dashboards/jucontrol_isoft_safe_plus.yaml`): app-style dashboard with Betriebsstatus, Wasserszenen, Bedienung, Einstellungen/Grenzwerte, Verbrauchsdiagramm and Info views

## [1.3.0] - 2026-04-30

### Fixed

- `DOSING_CONTROL` capability no longer incorrectly triggers the `number` platform (which had no matching entities, causing an empty platform load for i-dos devices)
- Duplicate inline micro-leak option map in `select.py` replaced with the shared `MICRO_LEAK_SETTINGS` constant from `const.py`
- Missing translation entries for `valve.zewa_leak_protection` added to both `de.json` and `strings.json`

### Added

- **API robustness**: `send_command()` now automatically retries once after 2 s on HTTP 429 (device busy), as documented in the JUDO connectivity manual
- **i-soft PRO – Water scene select**: New `pro_scene` select entity (11 scenes: Alltag, Körperpflege, Garten, …) using cmd `0x36`; requires `SCENES` capability
- **i-dos eco – Dosing concentration select**: New `idos_concentration_select` select entity (min / norm / max) using cmd `0x52`; requires `DOSING_CONTROL` capability
- **i-fill – Alarm relay select**: New `ifill_alarm_relay` select entity (auto / off / on) using cmd `0x54`; requires `FILL_ALARM_RELAY` capability
- **i-dos eco – Total water consumption sensor**: New `idos_water_consumption` sensor (L, total increasing) from i-dos status data
- **i-fill – Six additional diagnostic sensors**: `ifill_hysteresis_fill_pressure`, `ifill_max_fill_cycles`, `ifill_max_fill_time`, `ifill_max_fill_volume`, `ifill_cartridge_capacity`, `ifill_heating_content` – all parsed from the existing `0x42` response
- **New constants**: `PRO_SCENES` (scene index → name map) and `IFILL_ALARM_RELAY_MODES` added to `const.py`
- **Commissioning date and service address sensors**: Two new diagnostic sensors (`commissioning_date`, `service_address`) are now visible as entities for all device types; data was already fetched but previously only available in the HA diagnostics download
- **Current flow rate sensor** (`current_flow_rate`, disabled by default): Derived sensor for all devices with `TOTAL_WATER` capability (i-soft SAFE+, i-soft K SAFE+, i-soft PRO, i-soft, ZEWA, i-dos, i-fill). Calculated from the delta of the already-polled total water volume between consecutive update cycles — no extra API call needed. Unit: L/h, updated every polling interval
- **New blueprint**: `jucontrol_leak_protection_alert.yaml` – fires when the leak protection valve closes unexpectedly, creates a persistent notification and supports optional custom actions; compatible with both i-soft SAFE+ and ZEWA i-SAFE

## [1.2.2] - 2026-03-22

### Changed

- Day-based entities no longer show the Home Assistant shorthand unit `d`; existing installations migrate these entities to unitless display values
- Salt day-based entities now include `(Tage)` / `(days)` in their translated names for clearer display

## [1.2.1] - 2026-03-21

### Fixed

- Existing installations now migrate `total_water` and `soft_water` sensors to display in `m³` instead of liters

### Added

- Reusable Home Assistant blueprint for daily salt supply reminders based on `Salt range` and `Salt shortage warning`

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

[1.2.2]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.2.2
[1.2.1]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.2.1
[1.2.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.2.0
[1.1.1]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.1.1
[1.1.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.1.0
[1.0.0]: https://github.com/itsh-neumeier/JUcontrol_local/releases/tag/v1.0.0

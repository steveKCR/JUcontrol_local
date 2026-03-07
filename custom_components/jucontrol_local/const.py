"""Constants for the JUcontrol local integration."""

from __future__ import annotations

DOMAIN = "jucontrol_local"
MANUFACTURER = "JUDO Wasseraufbereitung GmbH"

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 60
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "Connectivity"
DEFAULT_PORT = 80

SCAN_INTERVAL_OPTIONS = {
    30: "30 seconds",
    60: "1 minute",
    120: "2 minutes",
    300: "5 minutes",
    600: "10 minutes",
}

# Hardness unit mapping
HARDNESS_UNITS: dict[int, str] = {
    0: "°dH",
    1: "°eH",
    2: "°fH",
    3: "gpg",
    4: "ppm",
    5: "mmol",
    6: "mval",
}

# Pump operation modes (i-dos eco)
PUMP_MODES: dict[int, str] = {
    0: "off",
    1: "auto",
    2: "manual",
    3: "single",
}

# Dosing concentration levels (i-dos eco)
DOSING_CONCENTRATION: dict[int, str] = {
    1: "min",
    2: "norm",
    3: "max",
}

# Fill valve modes (i-fill)
FILL_VALVE_MODES: dict[int, str] = {
    0: "auto",
    1: "manual_open",
    2: "manual_close",
}

# Cartridge types (i-fill)
CARTRIDGE_TYPES: dict[int, str] = {
    0: "PURE 7500",
    1: "PURE 25000",
    2: "SOFT 12000",
    3: "SOFT 60000",
    4: "PURE free",
    5: "SOFT free",
    10: "JP17",
    11: "JP26",
    12: "JP46",
    13: "JP100",
}

# Vacation mode types
# i-soft SAFE+: bitmask with bit 0=active, bit 1=U1, bit 2=U2, bit 3=U3
# ZEWA: simple 0=off, 1=U1, 2=U2, 3=U3
VACATION_MODES_SOFTENER: dict[str, int] = {
    "off": 0x00,
    "U1": 0x03,   # bit 0 (active) + bit 1 (U1)
    "U2": 0x05,   # bit 0 (active) + bit 2 (U2)
    "U3": 0x09,   # bit 0 (active) + bit 3 (U3)
}

VACATION_MODES_ZEWA: dict[int, str] = {
    0: "off",
    1: "U1",
    2: "U2",
    3: "U3",
}

# Micro-leak test settings
MICRO_LEAK_SETTINGS: dict[int, str] = {
    0: "disabled",
    1: "notify_only",
    2: "notify_and_close",
}

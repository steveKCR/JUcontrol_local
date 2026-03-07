"""Device type registry for JUDO water treatment devices."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class DeviceFamily(StrEnum):
    """JUDO device families."""

    ISOFT_SAFE = "isoft_safe"
    ISOFT_PRO = "isoft_pro"
    ISOFT = "isoft"
    SOFTWELL = "softwell"
    ZEWA = "zewa"
    IDOS = "idos"
    IFILL = "ifill"


class Capability(StrEnum):
    """Device capabilities."""

    # Sensor capabilities
    WATER_HARDNESS = "water_hardness"
    SALT_SUPPLY = "salt_supply"
    TOTAL_WATER = "total_water"
    SOFT_WATER = "soft_water"
    OPERATING_HOURS = "operating_hours"
    SERVICE_ADDRESS = "service_address"

    # Control capabilities
    REGENERATION = "regeneration"
    SET_HARDNESS = "set_hardness"
    SET_SALT = "set_salt"
    HARDNESS_UNIT = "hardness_unit"
    EXTRACTION_LIMITS = "extraction_limits"

    # Leak protection
    LEAK_PROTECTION = "leak_protection"
    LEAK_ALARM = "leak_alarm"
    VACATION_MODE = "vacation_mode"

    # ZEWA specific
    ZEWA_LEAK_PROTECTION = "zewa_leak_protection"
    ZEWA_VACATION = "zewa_vacation"
    ZEWA_SLEEP = "zewa_sleep"
    ZEWA_MICRO_LEAK = "zewa_micro_leak"
    ZEWA_LEARNING = "zewa_learning"
    ZEWA_NOTIFICATION = "zewa_notification"
    ZEWA_ABSENCE = "zewa_absence"

    # i-soft PRO specific
    SCENES = "scenes"

    # i-dos eco specific
    DOSING_STATUS = "dosing_status"
    DOSING_CONTROL = "dosing_control"
    PUMP_CONTROL = "pump_control"

    # i-fill specific
    FILL_LIMITS = "fill_limits"
    FILL_VALVE = "fill_valve"
    FILL_ALARM_RELAY = "fill_alarm_relay"


@dataclass
class DeviceTypeInfo:
    """Information about a JUDO device type."""

    family: DeviceFamily
    model: str
    has_leak_protection: bool = False
    capabilities: set[Capability] = field(default_factory=set)


# Common capability sets
_SOFTENER_BASE: set[Capability] = {
    Capability.WATER_HARDNESS,
    Capability.SALT_SUPPLY,
    Capability.SOFT_WATER,
    Capability.OPERATING_HOURS,
    Capability.SERVICE_ADDRESS,
    Capability.REGENERATION,
    Capability.SET_HARDNESS,
    Capability.SET_SALT,
    Capability.HARDNESS_UNIT,
    Capability.EXTRACTION_LIMITS,
    Capability.TOTAL_WATER,
    Capability.VACATION_MODE,
}

_SOFTENER_LEAK = _SOFTENER_BASE | {Capability.LEAK_PROTECTION}
_SOFTENER_ALARM = _SOFTENER_BASE | {Capability.LEAK_ALARM}
_SOFTENER_PRO = _SOFTENER_LEAK | {Capability.SCENES}

_SOFTWELL_CAPS: set[Capability] = {
    Capability.SOFT_WATER,
    Capability.OPERATING_HOURS,
}

_ZEWA_CAPS: set[Capability] = {
    Capability.TOTAL_WATER,
    Capability.OPERATING_HOURS,
    Capability.ZEWA_LEAK_PROTECTION,
    Capability.ZEWA_VACATION,
    Capability.ZEWA_SLEEP,
    Capability.ZEWA_MICRO_LEAK,
    Capability.ZEWA_LEARNING,
    Capability.ZEWA_NOTIFICATION,
    Capability.ZEWA_ABSENCE,
}

_IDOS_CAPS: set[Capability] = {
    Capability.TOTAL_WATER,
    Capability.OPERATING_HOURS,
    Capability.DOSING_STATUS,
    Capability.DOSING_CONTROL,
    Capability.PUMP_CONTROL,
}

_IFILL_CAPS: set[Capability] = {
    Capability.TOTAL_WATER,
    Capability.OPERATING_HOURS,
    Capability.FILL_LIMITS,
    Capability.FILL_VALVE,
    Capability.FILL_ALARM_RELAY,
    Capability.ZEWA_LEAK_PROTECTION,
}


# Device type code to info mapping
DEVICE_TYPE_MAP: dict[int, DeviceTypeInfo] = {
    # i-soft SAFE+ (with leak protection)
    0x33: DeviceTypeInfo(DeviceFamily.ISOFT_SAFE, "i-soft SAFE+", True, _SOFTENER_LEAK),
    0x57: DeviceTypeInfo(DeviceFamily.ISOFT_SAFE, "i-soft SAFE+", True, _SOFTENER_LEAK),
    # i-soft K SAFE+ (with leak protection)
    0x42: DeviceTypeInfo(DeviceFamily.ISOFT_SAFE, "i-soft K SAFE+", True, _SOFTENER_LEAK),
    0x67: DeviceTypeInfo(DeviceFamily.ISOFT_SAFE, "i-soft K SAFE+", True, _SOFTENER_LEAK),
    # i-soft PRO (with leak protection + scenes)
    0x58: DeviceTypeInfo(DeviceFamily.ISOFT_PRO, "i-soft PRO", True, _SOFTENER_PRO),
    0x4B: DeviceTypeInfo(DeviceFamily.ISOFT_PRO, "i-soft PRO", True, _SOFTENER_PRO),
    0x4C: DeviceTypeInfo(DeviceFamily.ISOFT_PRO, "i-soft PRO L", True, _SOFTENER_PRO),
    # i-soft (with leak alarm)
    0x32: DeviceTypeInfo(DeviceFamily.ISOFT, "i-soft", False, _SOFTENER_ALARM),
    0x53: DeviceTypeInfo(DeviceFamily.ISOFT, "i-soft", False, _SOFTENER_ALARM),
    # i-soft K (with leak alarm)
    0x43: DeviceTypeInfo(DeviceFamily.ISOFT, "i-soft K", False, _SOFTENER_ALARM),
    0x54: DeviceTypeInfo(DeviceFamily.ISOFT, "i-soft K", False, _SOFTENER_ALARM),
    # SOFTwell variants (no leak protection, basic)
    0x34: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell P", False, _SOFTWELL_CAPS),
    0x59: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell P", False, _SOFTWELL_CAPS),
    0x35: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell S", False, _SOFTWELL_CAPS),
    0x63: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell S", False, _SOFTWELL_CAPS),
    0x36: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell K", False, _SOFTWELL_CAPS),
    0x5A: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell K", False, _SOFTWELL_CAPS),
    0x47: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell KP", False, _SOFTWELL_CAPS),
    0x62: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell KP", False, _SOFTWELL_CAPS),
    0x48: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell KS", False, _SOFTWELL_CAPS),
    0x64: DeviceTypeInfo(DeviceFamily.SOFTWELL, "SOFTwell KS", False, _SOFTWELL_CAPS),
    # ZEWA i-SAFE / PROM-i-SAFE / ZEWA i-SAFE FILT
    0x44: DeviceTypeInfo(DeviceFamily.ZEWA, "ZEWA i-SAFE", True, _ZEWA_CAPS),
    # i-dos eco (dosing pump)
    0x41: DeviceTypeInfo(DeviceFamily.IDOS, "i-dos eco", False, _IDOS_CAPS),
    # i-fill 60 (heating fill)
    0x3C: DeviceTypeInfo(DeviceFamily.IFILL, "i-fill 60", False, _IFILL_CAPS),
}


def get_device_info(type_code: int) -> DeviceTypeInfo | None:
    """Look up device information by type code."""
    return DEVICE_TYPE_MAP.get(type_code)


def has_capability(type_code: int, capability: Capability) -> bool:
    """Check if a device type has a specific capability."""
    info = DEVICE_TYPE_MAP.get(type_code)
    if info is None:
        return False
    return capability in info.capabilities


def get_platforms_for_device(type_code: int) -> list[str]:
    """Get the HA platforms needed for a device type."""
    info = DEVICE_TYPE_MAP.get(type_code)
    if info is None:
        return []

    platforms = ["sensor"]
    caps = info.capabilities

    # Check if buttons are needed
    if caps & {
        Capability.REGENERATION,
        Capability.ZEWA_NOTIFICATION,
        Capability.ZEWA_MICRO_LEAK,
        Capability.ZEWA_LEARNING,
    }:
        platforms.append("button")

    # Check if switches are needed
    if caps & {
        Capability.LEAK_PROTECTION,
        Capability.ZEWA_LEAK_PROTECTION,
        Capability.ZEWA_SLEEP,
    }:
        platforms.append("switch")

    # Check if numbers are needed
    if caps & {
        Capability.SET_HARDNESS,
        Capability.SET_SALT,
        Capability.EXTRACTION_LIMITS,
        Capability.ZEWA_SLEEP,
        Capability.DOSING_CONTROL,
    }:
        platforms.append("number")

    # Check if selects are needed (includes vacation mode dropdown)
    if caps & {
        Capability.HARDNESS_UNIT,
        Capability.PUMP_CONTROL,
        Capability.FILL_VALVE,
        Capability.VACATION_MODE,
        Capability.ZEWA_VACATION,
    }:
        platforms.append("select")

    # Check if binary sensors are needed
    if caps & {
        Capability.ZEWA_LEARNING,
    }:
        platforms.append("binary_sensor")

    return platforms

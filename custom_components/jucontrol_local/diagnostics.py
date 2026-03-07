"""Diagnostics support for JUcontrol local."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import JudoDataCoordinator


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Redact sensitive information
    config_data = dict(entry.data)
    config_data[CONF_PASSWORD] = "**REDACTED**"
    config_data[CONF_USERNAME] = "**REDACTED**"
    config_data[CONF_HOST] = "**REDACTED**"

    return {
        "config": config_data,
        "device_info": {
            "type_code": f"0x{coordinator.device_type_code:02X}",
            "family": coordinator.device_family,
            "model": (
                coordinator.device_info.model if coordinator.device_info else "Unknown"
            ),
            "serial_number": coordinator.device_number,
            "sw_version": coordinator.sw_version,
            "commissioning_date": coordinator.commissioning_date,
            "service_address": coordinator.service_address,
        },
        "coordinator_data": coordinator.data,
    }

"""The JUcontrol local integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import entity_registry as er

from .api_client import JudoApiClient
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import get_platforms_for_device

_LOGGER = logging.getLogger(__name__)

type JudoConfigEntry = ConfigEntry

_WATER_VOLUME_SENSOR_UNITS = {
    "total_water": UnitOfVolume.CUBIC_METERS,
    "soft_water": UnitOfVolume.CUBIC_METERS,
}


async def async_setup_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Set up JUcontrol local from a config entry."""
    session = async_get_clientsession(hass)
    client = JudoApiClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )

    device_type = entry.data.get("device_type", 0)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    # Check for options flow override
    if CONF_SCAN_INTERVAL in entry.options:
        scan_interval = entry.options[CONF_SCAN_INTERVAL]

    coordinator = JudoDataCoordinator(hass, client, device_type, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await _async_migrate_water_volume_units(hass, entry)

    platforms = get_platforms_for_device(device_type)
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Unload a config entry."""
    device_type = entry.data.get("device_type", 0)
    platforms = get_platforms_for_device(device_type)

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, platforms):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: JudoConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _async_migrate_water_volume_units(
    hass: HomeAssistant, entry: JudoConfigEntry
) -> None:
    """Force water total sensors to display in cubic meters for existing installs."""
    if (device_number := entry.data.get("device_number")) is None:
        return

    entity_registry = er.async_get(hass)

    for sensor_key, unit in _WATER_VOLUME_SENSOR_UNITS.items():
        unique_id = f"judo_{device_number}_{sensor_key}"
        entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, unique_id)
        if entity_id is None:
            continue

        registry_entry = entity_registry.async_get(entity_id)
        if registry_entry is None or registry_entry.unit_of_measurement == unit:
            continue

        entity_registry.async_update_entity(
            entity_id,
            unit_of_measurement=unit,
        )

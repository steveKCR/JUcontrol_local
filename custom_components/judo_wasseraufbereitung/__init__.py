"""Die JUDO Wasseraufbereitung Integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import JudoApiClient
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import JudoCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SELECT, Platform.SWITCH]

type JudoConfigEntry = ConfigEntry


async def async_setup_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Config Entry einrichten."""
    session = async_get_clientsession(hass)
    client = JudoApiClient(
        host=entry.data[CONF_HOST],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        session=session,
    )

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL
    ) or entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinator = JudoCoordinator(hass, client, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    _async_remove_legacy_valve_entity(hass, coordinator.serial_number)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: JudoConfigEntry) -> bool:
    """Config Entry entladen."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


def _async_remove_legacy_valve_entity(hass: HomeAssistant, serial: int) -> None:
    """Alte Ventil-Entität (Leckageschutz) nach Umstellung auf Switch entfernen."""
    registry = er.async_get(hass)
    legacy_uid = f"judo_{serial}_leak_protection"
    if entity_id := registry.async_get_entity_id("valve", DOMAIN, legacy_uid):
        registry.async_remove(entity_id)


async def _async_update_listener(
    hass: HomeAssistant, entry: JudoConfigEntry
) -> None:
    """Bei Optionsänderungen reloaden."""
    await hass.config_entries.async_reload(entry.entry_id)

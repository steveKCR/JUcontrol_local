"""Switch-Plattform – Wasser an/aus (Leckageschutz-Ventil)."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .coordinator import JudoCoordinator
from .entity import JudoEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: JudoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WaterSupplySwitch(coordinator)])


class WaterSupplySwitch(JudoEntity, SwitchEntity, RestoreEntity):
    """Ein = Wasser fließt (Leckageschutz geöffnet), Aus = abgesperrt."""

    _attr_translation_key = "water_supply"
    _attr_icon = "mdi:water"

    def __init__(self, coordinator: JudoCoordinator) -> None:
        super().__init__(coordinator, "water_supply")
        # Kein API-Lesebefehl: nach Neustart letzten Zustand wiederherstellen,
        # sonst Annahme „Wasser an“ wie früher beim Ventil (offen).
        self._attr_is_on = True

    async def async_added_to_hass(self) -> None:
        """Letzten Schalterzustand nach HA-Neustart übernehmen."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            if last_state.state == STATE_ON:
                self._attr_is_on = True
            elif last_state.state == STATE_OFF:
                self._attr_is_on = False

    async def async_turn_on(self, **kwargs: object) -> None:
        await self.coordinator.client.open_leak_protection()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: object) -> None:
        await self.coordinator.client.close_leak_protection()
        self._attr_is_on = False
        self.async_write_ha_state()

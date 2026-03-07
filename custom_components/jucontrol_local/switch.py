"""Switch platform for JUcontrol local."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoSwitchEntityDescription(SwitchEntityDescription):
    """Describes a JUDO switch entity."""

    required_capability: Capability
    turn_on_fn: Callable[[JudoDataCoordinator], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[JudoDataCoordinator], Coroutine[Any, Any, None]]
    is_on_fn: Callable[[dict[str, Any]], bool | None] | None = None


SWITCH_DESCRIPTIONS: tuple[JudoSwitchEntityDescription, ...] = (
    # Softener leak protection (closed = protected = ON)
    JudoSwitchEntityDescription(
        key="leak_protection",
        translation_key="leak_protection",
        icon="mdi:shield-lock",
        required_capability=Capability.LEAK_PROTECTION,
        turn_on_fn=lambda coord: coord.client.close_leak_protection(),
        turn_off_fn=lambda coord: coord.client.open_leak_protection(),
        is_on_fn=None,  # No read-back available via API
    ),
    # ZEWA leak protection
    JudoSwitchEntityDescription(
        key="zewa_leak_protection",
        translation_key="leak_protection",
        icon="mdi:shield-lock",
        required_capability=Capability.ZEWA_LEAK_PROTECTION,
        turn_on_fn=lambda coord: coord.client.zewa_close_leak_protection(),
        turn_off_fn=lambda coord: coord.client.zewa_open_leak_protection(),
        is_on_fn=None,
    ),
    # ZEWA sleep mode
    JudoSwitchEntityDescription(
        key="zewa_sleep",
        translation_key="sleep_mode",
        icon="mdi:sleep",
        required_capability=Capability.ZEWA_SLEEP,
        turn_on_fn=lambda coord: coord.client.zewa_start_sleep_mode(),
        turn_off_fn=lambda coord: coord.client.zewa_stop_sleep_mode(),
        is_on_fn=None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO switch entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoSwitch] = []
    for description in SWITCH_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoSwitch(coordinator, description))

    async_add_entities(entities)


class JudoSwitch(JudoEntity, SwitchEntity):
    """Representation of a JUDO switch."""

    entity_description: JudoSwitchEntityDescription
    _attr_assumed_state = True  # No read-back for most commands

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._is_on: bool = False

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.entity_description.is_on_fn is not None and self.coordinator.data:
            result = self.entity_description.is_on_fn(self.coordinator.data)
            if result is not None:
                self._is_on = result
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(self.coordinator)
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(self.coordinator)
        self._is_on = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

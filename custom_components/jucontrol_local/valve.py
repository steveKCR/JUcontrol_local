"""Valve platform for JUcontrol local."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.valve import (
    ValveDeviceClass,
    ValveEntity,
    ValveEntityDescription,
    ValveEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoValveEntityDescription(ValveEntityDescription):
    """Describes a JUDO valve entity."""

    required_capability: Capability
    open_fn: Callable[[JudoDataCoordinator], Coroutine[Any, Any, None]]
    close_fn: Callable[[JudoDataCoordinator], Coroutine[Any, Any, None]]


VALVE_DESCRIPTIONS: tuple[JudoValveEntityDescription, ...] = (
    # Softener leak protection valve
    JudoValveEntityDescription(
        key="leak_protection",
        translation_key="leak_protection",
        device_class=ValveDeviceClass.WATER,
        required_capability=Capability.LEAK_PROTECTION,
        open_fn=lambda coord: coord.client.open_leak_protection(),
        close_fn=lambda coord: coord.client.close_leak_protection(),
    ),
    # ZEWA leak protection valve
    JudoValveEntityDescription(
        key="zewa_leak_protection",
        translation_key="leak_protection",
        device_class=ValveDeviceClass.WATER,
        required_capability=Capability.ZEWA_LEAK_PROTECTION,
        open_fn=lambda coord: coord.client.zewa_open_leak_protection(),
        close_fn=lambda coord: coord.client.zewa_close_leak_protection(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO valve entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoValve] = []
    for description in VALVE_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoValve(coordinator, description))

    async_add_entities(entities)


class JudoValve(JudoEntity, ValveEntity):
    """Representation of a JUDO valve."""

    entity_description: JudoValveEntityDescription
    _attr_supported_features = (
        ValveEntityFeature.OPEN | ValveEntityFeature.CLOSE
    )
    _attr_reports_position = False

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoValveEntityDescription,
    ) -> None:
        """Initialize the valve."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_is_closed: bool | None = None

    async def async_open_valve(self, **kwargs: Any) -> None:
        """Open the valve."""
        await self.entity_description.open_fn(self.coordinator)
        self._attr_is_closed = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    async def async_close_valve(self, **kwargs: Any) -> None:
        """Close the valve."""
        await self.entity_description.close_fn(self.coordinator)
        self._attr_is_closed = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

"""Binary sensor platform for JUcontrol local."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a JUDO binary sensor entity."""

    required_capability: Capability
    is_on_fn: Any = None


BINARY_SENSOR_DESCRIPTIONS: tuple[JudoBinarySensorEntityDescription, ...] = (
    JudoBinarySensorEntityDescription(
        key="learning_mode_active",
        translation_key="learning_mode_active",
        icon="mdi:school",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_LEARNING,
        is_on_fn=lambda data: data.get("learning_mode", {}).get("active", False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO binary sensor entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoBinarySensor] = []
    for description in BINARY_SENSOR_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoBinarySensor(coordinator, description))

    async_add_entities(entities)


class JudoBinarySensor(JudoEntity, BinarySensorEntity):
    """Representation of a JUDO binary sensor."""

    entity_description: JudoBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None or self.entity_description.is_on_fn is None:
            return None
        return self.entity_description.is_on_fn(self.coordinator.data)

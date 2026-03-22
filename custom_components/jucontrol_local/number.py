"""Number platform for JUcontrol local."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoNumberEntityDescription(NumberEntityDescription):
    """Describes a JUDO number entity."""

    required_capability: Capability
    set_fn: Callable[[JudoDataCoordinator, float], Coroutine[Any, Any, None]]
    value_fn: Callable[[dict[str, Any]], float | None] | None = None


NUMBER_DESCRIPTIONS: tuple[JudoNumberEntityDescription, ...] = (
    JudoNumberEntityDescription(
        key="set_water_hardness",
        translation_key="set_water_hardness",
        icon="mdi:water-opacity",
        native_min_value=1,
        native_max_value=30,
        native_step=1,
        native_unit_of_measurement="°dH",
        mode=NumberMode.BOX,
        required_capability=Capability.SET_HARDNESS,
        set_fn=lambda coord, val: coord.client.set_water_hardness(int(val)),
        value_fn=lambda data: data.get("water_hardness"),
    ),
    JudoNumberEntityDescription(
        key="set_salt_supply",
        translation_key="set_salt_supply",
        icon="mdi:shaker-outline",
        native_min_value=0,
        native_max_value=50,
        native_step=0.1,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        mode=NumberMode.BOX,
        required_capability=Capability.SET_SALT,
        set_fn=lambda coord, val: coord.client.set_salt_supply(int(val * 1000)),
        value_fn=lambda data: round(data.get("salt_weight", 0) / 1000, 1),
    ),
    JudoNumberEntityDescription(
        key="set_salt_shortage_warning",
        translation_key="set_salt_shortage_warning",
        icon="mdi:alert-circle-outline",
        native_min_value=1,
        native_max_value=90,
        native_step=1,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.SET_SALT,
        set_fn=lambda coord, val: coord.client.set_salt_shortage_warning(int(val)),
        value_fn=lambda data: data.get("salt_shortage_warning"),
    ),
    JudoNumberEntityDescription(
        key="set_max_extraction_duration",
        translation_key="set_max_extraction_duration",
        icon="mdi:timer-outline",
        native_min_value=0,
        native_max_value=255,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.EXTRACTION_LIMITS,
        set_fn=lambda coord, val: coord.client.set_max_extraction_duration(int(val)),
        value_fn=lambda data: data.get("max_extraction_duration"),
    ),
    JudoNumberEntityDescription(
        key="set_max_extraction_volume",
        translation_key="set_max_extraction_volume",
        icon="mdi:water-outline",
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.EXTRACTION_LIMITS,
        set_fn=lambda coord, val: coord.client.set_max_extraction_volume(int(val)),
        value_fn=lambda data: data.get("max_extraction_volume"),
    ),
    JudoNumberEntityDescription(
        key="set_max_flow_rate",
        translation_key="set_max_flow_rate",
        icon="mdi:speedometer",
        native_min_value=0,
        native_max_value=65535,
        native_step=1,
        native_unit_of_measurement="L/h",
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.EXTRACTION_LIMITS,
        set_fn=lambda coord, val: coord.client.set_max_flow_rate(int(val)),
        value_fn=lambda data: data.get("max_flow_rate"),
    ),
    JudoNumberEntityDescription(
        key="set_sleep_duration",
        translation_key="set_sleep_duration",
        icon="mdi:sleep",
        native_min_value=1,
        native_max_value=10,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.HOURS,
        mode=NumberMode.SLIDER,
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.ZEWA_SLEEP,
        set_fn=lambda coord, val: coord.client.zewa_set_sleep_duration(int(val)),
        value_fn=lambda data: data.get("sleep_duration"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO number entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoNumber] = []
    for description in NUMBER_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoNumber(coordinator, description))

    async_add_entities(entities)


class JudoNumber(JudoEntity, NumberEntity):
    """Representation of a JUDO number entity."""

    entity_description: JudoNumberEntityDescription

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoNumberEntityDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None or self.entity_description.value_fn is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.entity_description.set_fn(self.coordinator, value)
        await self.coordinator.async_request_refresh()

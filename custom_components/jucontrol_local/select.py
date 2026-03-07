"""Select platform for JUcontrol local."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    FILL_VALVE_MODES,
    HARDNESS_UNITS,
    PUMP_MODES,
    VACATION_MODES_SOFTENER,
    VACATION_MODES_ZEWA,
)
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoSelectEntityDescription(SelectEntityDescription):
    """Describes a JUDO select entity."""

    required_capability: Capability
    options_map: dict[int, str] | dict[str, int]
    options_list: list[str] | None = None
    current_fn: Any = None
    select_fn: Any = None


SELECT_DESCRIPTIONS: tuple[JudoSelectEntityDescription, ...] = (
    JudoSelectEntityDescription(
        key="hardness_unit",
        translation_key="set_hardness_unit",
        icon="mdi:format-text",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.HARDNESS_UNIT,
        options_map=HARDNESS_UNITS,
        current_fn=lambda data: HARDNESS_UNITS.get(data.get("hardness_unit", 0)),
        select_fn=lambda coord, val: coord.client.set_hardness_unit(
            next(k for k, v in HARDNESS_UNITS.items() if v == val)
        ),
    ),
    JudoSelectEntityDescription(
        key="pump_mode",
        translation_key="pump_mode",
        icon="mdi:pump",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.PUMP_CONTROL,
        options_map=PUMP_MODES,
        current_fn=lambda data: PUMP_MODES.get(
            data.get("idos_status", {}).get("operation_mode", 0)
        ),
        select_fn=lambda coord, val: coord.client.idos_set_pump_mode(
            next(k for k, v in PUMP_MODES.items() if v == val)
        ),
    ),
    JudoSelectEntityDescription(
        key="fill_valve_mode",
        translation_key="fill_valve_mode",
        icon="mdi:valve",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.FILL_VALVE,
        options_map=FILL_VALVE_MODES,
        current_fn=None,  # No read-back
        select_fn=lambda coord, val: coord.client.ifill_set_valve_mode(
            next(k for k, v in FILL_VALVE_MODES.items() if v == val)
        ),
    ),
    # Softener vacation mode (i-soft SAFE+, i-soft PRO, i-soft)
    JudoSelectEntityDescription(
        key="vacation_mode",
        translation_key="vacation_mode",
        icon="mdi:palm-tree",
        required_capability=Capability.VACATION_MODE,
        options_map=VACATION_MODES_SOFTENER,
        options_list=list(VACATION_MODES_SOFTENER.keys()),
        current_fn=None,  # No read-back available
        select_fn=lambda coord, val: coord.client.set_vacation_mode_softener(
            VACATION_MODES_SOFTENER[val]
        ),
    ),
    # ZEWA vacation mode
    JudoSelectEntityDescription(
        key="zewa_vacation_mode",
        translation_key="vacation_mode",
        icon="mdi:palm-tree",
        required_capability=Capability.ZEWA_VACATION,
        options_map=VACATION_MODES_ZEWA,
        current_fn=None,
        select_fn=lambda coord, val: coord.client.zewa_set_vacation_type(
            next(k for k, v in VACATION_MODES_ZEWA.items() if v == val)
        ),
    ),
    JudoSelectEntityDescription(
        key="micro_leak_mode",
        translation_key="micro_leak_mode",
        icon="mdi:water-alert-outline",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.ZEWA_MICRO_LEAK,
        options_map={0: "disabled", 1: "notify_only", 2: "notify_and_close"},
        current_fn=lambda data: {0: "disabled", 1: "notify_only", 2: "notify_and_close"}.get(
            data.get("micro_leak_setting", 0)
        ),
        select_fn=lambda coord, val: coord.client.zewa_set_micro_leak(
            next(
                k
                for k, v in {0: "disabled", 1: "notify_only", 2: "notify_and_close"}.items()
                if v == val
            )
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO select entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoSelect] = []
    for description in SELECT_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoSelect(coordinator, description))

    async_add_entities(entities)


class JudoSelect(JudoEntity, SelectEntity):
    """Representation of a JUDO select entity."""

    entity_description: JudoSelectEntityDescription

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoSelectEntityDescription,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        if description.options_list is not None:
            self._attr_options = description.options_list
        else:
            self._attr_options = list(description.options_map.values())
        self._selected: str | None = None

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.entity_description.current_fn is not None and self.coordinator.data:
            result = self.entity_description.current_fn(self.coordinator.data)
            if result is not None:
                self._selected = result
                return result
        return self._selected

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.select_fn(self.coordinator, option)
        self._selected = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

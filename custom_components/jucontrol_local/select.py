"""Select platform for JUcontrol local."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    DOSING_CONCENTRATION,
    FILL_VALVE_MODES,
    HARDNESS_UNITS,
    IFILL_ALARM_RELAY_MODES,
    ISOFT_SCENES,
    MICRO_LEAK_SETTINGS,
    PRO_SCENES,
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
    default_option: str | None = None  # restored after HA restart if no read-back


SELECT_DESCRIPTIONS: tuple[JudoSelectEntityDescription, ...] = (
    JudoSelectEntityDescription(
        key="hardness_unit",
        translation_key="set_hardness_unit",
        icon="mdi:format-text",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
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
        default_option="off",
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
        options_map=MICRO_LEAK_SETTINGS,
        current_fn=lambda data: MICRO_LEAK_SETTINGS.get(
            data.get("micro_leak_setting", 0)
        ),
        select_fn=lambda coord, val: coord.client.zewa_set_micro_leak(
            next(k for k, v in MICRO_LEAK_SETTINGS.items() if v == val)
        ),
    ),
    # i-soft SAFE+ / i-soft K SAFE+ / i-soft water scenes (5 scenes)
    JudoSelectEntityDescription(
        key="isoft_scene",
        translation_key="isoft_scene",
        icon="mdi:water-sync",
        required_capability=Capability.WATER_SCENES,
        options_map=ISOFT_SCENES,
        current_fn=None,
        default_option="normal_operation",
        select_fn=lambda coord, val: coord.client.pro_activate_scene(
            next(k for k, v in ISOFT_SCENES.items() if v == val)
        ),
    ),
    # i-soft PRO water scenes
    JudoSelectEntityDescription(
        key="pro_scene",
        translation_key="pro_scene",
        icon="mdi:water-sync",
        required_capability=Capability.SCENES,
        options_map=PRO_SCENES,
        current_fn=None,
        default_option="everyday",
        select_fn=lambda coord, val: coord.client.pro_activate_scene(
            next(k for k, v in PRO_SCENES.items() if v == val)
        ),
    ),
    # i-dos eco dosing concentration
    JudoSelectEntityDescription(
        key="idos_concentration_select",
        translation_key="idos_concentration_select",
        icon="mdi:flask-outline",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.DOSING_CONTROL,
        options_map=DOSING_CONCENTRATION,
        current_fn=lambda data: DOSING_CONCENTRATION.get(
            data.get("idos_status", {}).get("concentration", 0)
        ),
        select_fn=lambda coord, val: coord.client.idos_set_concentration(
            next(k for k, v in DOSING_CONCENTRATION.items() if v == val)
        ),
    ),
    # i-fill alarm relay
    JudoSelectEntityDescription(
        key="ifill_alarm_relay",
        translation_key="ifill_alarm_relay",
        icon="mdi:alarm-light-outline",
        entity_category=EntityCategory.CONFIG,
        required_capability=Capability.FILL_ALARM_RELAY,
        options_map=IFILL_ALARM_RELAY_MODES,
        current_fn=None,
        select_fn=lambda coord, val: coord.client.ifill_set_alarm_relay(
            next(k for k, v in IFILL_ALARM_RELAY_MODES.items() if v == val)
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


class JudoSelect(JudoEntity, SelectEntity, RestoreEntity):
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
        self._selected: str | None = description.default_option

    async def async_added_to_hass(self) -> None:
        """Restore last known state after HA restart."""
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            if last_state.state in self._attr_options:
                self._selected = last_state.state

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.entity_description.current_fn is not None and self.coordinator.data:
            result = self.entity_description.current_fn(self.coordinator.data)
            if result is not None:
                self._selected = result
        return self._selected

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.entity_description.select_fn(self.coordinator, option)
        self._selected = option
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

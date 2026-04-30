"""Button platform for JUcontrol local."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoButtonEntityDescription(ButtonEntityDescription):
    """Describes a JUDO button entity."""

    required_capability: Capability
    press_fn: Callable[[JudoDataCoordinator], Coroutine[Any, Any, None]]


BUTTON_DESCRIPTIONS: tuple[JudoButtonEntityDescription, ...] = (
    JudoButtonEntityDescription(
        key="salt_refill_25kg",
        translation_key="salt_refill_25kg",
        icon="mdi:shaker-outline",
        required_capability=Capability.SET_SALT,
        press_fn=lambda coord: coord.client.set_salt_supply(25000),
    ),
    JudoButtonEntityDescription(
        key="start_regeneration",
        translation_key="start_regeneration",
        icon="mdi:refresh",
        required_capability=Capability.REGENERATION,
        press_fn=lambda coord: coord.client.start_regeneration(),
    ),
    JudoButtonEntityDescription(
        key="reset_notification",
        translation_key="reset_notification",
        icon="mdi:bell-off-outline",
        required_capability=Capability.ZEWA_NOTIFICATION,
        press_fn=lambda coord: coord.client.zewa_reset_notification(),
    ),
    JudoButtonEntityDescription(
        key="start_micro_leak_test",
        translation_key="start_micro_leak_test",
        icon="mdi:water-alert",
        required_capability=Capability.ZEWA_MICRO_LEAK,
        press_fn=lambda coord: coord.client.zewa_start_micro_leak_test(),
    ),
    JudoButtonEntityDescription(
        key="start_learning_mode",
        translation_key="start_learning_mode",
        icon="mdi:school",
        required_capability=Capability.ZEWA_LEARNING,
        press_fn=lambda coord: coord.client.zewa_start_learning_mode(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO button entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoButton] = []
    for description in BUTTON_DESCRIPTIONS:
        if coordinator.has_capability(description.required_capability):
            entities.append(JudoButton(coordinator, description))

    async_add_entities(entities)


class JudoButton(JudoEntity, ButtonEntity):
    """Representation of a JUDO button."""

    entity_description: JudoButtonEntityDescription

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator)
        await self.coordinator.async_request_refresh()

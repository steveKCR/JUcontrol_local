"""Base entity for JUcontrol local."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import JudoDataCoordinator


class JudoEntity(CoordinatorEntity[JudoDataCoordinator]):
    """Base class for JUDO entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        entity_key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        device_number = coordinator.device_number
        model = (
            coordinator.device_info.model if coordinator.device_info else "Unknown"
        )

        self._attr_unique_id = f"judo_{device_number}_{entity_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device_number))},
            name=f"JUDO {model}",
            manufacturer=MANUFACTURER,
            model=model,
            sw_version=coordinator.sw_version,
            serial_number=str(device_number),
        )

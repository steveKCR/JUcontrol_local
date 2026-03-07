"""Sensor platform for JUcontrol local."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass, UnitOfTime, UnitOfVolume, UnitOfVolumeFlowRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    HARDNESS_UNITS,
    DOSING_CONCENTRATION,
    CARTRIDGE_TYPES,
)
from .coordinator import JudoDataCoordinator
from .device_types import Capability
from .entity import JudoEntity


@dataclass(frozen=True, kw_only=True)
class JudoSensorEntityDescription(SensorEntityDescription):
    """Describes a JUDO sensor entity."""

    required_capability: Capability | None = None
    value_fn: Any = None


SENSOR_DESCRIPTIONS: tuple[JudoSensorEntityDescription, ...] = (
    # --- Water softener sensors ---
    JudoSensorEntityDescription(
        key="water_hardness",
        translation_key="water_hardness",
        icon="mdi:water-opacity",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="°dH",
        required_capability=Capability.WATER_HARDNESS,
        value_fn=lambda data: data.get("water_hardness"),
    ),
    JudoSensorEntityDescription(
        key="salt_weight",
        translation_key="salt_weight",
        icon="mdi:shaker-outline",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        device_class=SensorDeviceClass.WEIGHT,
        required_capability=Capability.SALT_SUPPLY,
        value_fn=lambda data: round(data.get("salt_weight", 0) / 1000, 2),
    ),
    JudoSensorEntityDescription(
        key="salt_range",
        translation_key="salt_range",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.DAYS,
        required_capability=Capability.SALT_SUPPLY,
        value_fn=lambda data: data.get("salt_range"),
    ),
    JudoSensorEntityDescription(
        key="salt_shortage_warning",
        translation_key="salt_shortage_warning",
        icon="mdi:alert-circle-outline",
        native_unit_of_measurement=UnitOfTime.DAYS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.SALT_SUPPLY,
        value_fn=lambda data: data.get("salt_shortage_warning"),
    ),
    JudoSensorEntityDescription(
        key="total_water",
        translation_key="total_water",
        icon="mdi:water",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.WATER,
        suggested_display_precision=3,
        suggested_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        required_capability=Capability.TOTAL_WATER,
        value_fn=lambda data: round(data.get("total_water", 0) / 1000, 3),
    ),
    JudoSensorEntityDescription(
        key="soft_water",
        translation_key="soft_water",
        icon="mdi:water-check",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        device_class=SensorDeviceClass.WATER,
        suggested_display_precision=3,
        suggested_unit_of_measurement=UnitOfVolume.CUBIC_METERS,
        required_capability=Capability.SOFT_WATER,
        value_fn=lambda data: round(data.get("soft_water", 0) / 1000, 3),
    ),
    JudoSensorEntityDescription(
        key="hardness_unit",
        translation_key="hardness_unit",
        icon="mdi:format-text",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.HARDNESS_UNIT,
        value_fn=lambda data: HARDNESS_UNITS.get(data.get("hardness_unit", 0), "°dH"),
    ),
    # --- Operating hours (all devices) ---
    JudoSensorEntityDescription(
        key="operating_days",
        translation_key="operating_days",
        icon="mdi:clock-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.DAYS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.OPERATING_HOURS,
        value_fn=lambda data: data.get("operating_hours", {}).get("days", 0),
    ),
    # --- Extraction limits (diagnostic) ---
    JudoSensorEntityDescription(
        key="max_extraction_duration",
        translation_key="max_extraction_duration",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.EXTRACTION_LIMITS,
        value_fn=lambda data: data.get("max_extraction_duration"),
    ),
    JudoSensorEntityDescription(
        key="max_extraction_volume",
        translation_key="max_extraction_volume",
        icon="mdi:water-outline",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.EXTRACTION_LIMITS,
        value_fn=lambda data: data.get("max_extraction_volume"),
    ),
    JudoSensorEntityDescription(
        key="max_flow_rate",
        translation_key="max_flow_rate",
        icon="mdi:speedometer",
        native_unit_of_measurement="L/h",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.EXTRACTION_LIMITS,
        value_fn=lambda data: data.get("max_flow_rate"),
    ),
    # --- ZEWA sensors ---
    JudoSensorEntityDescription(
        key="sleep_duration",
        translation_key="sleep_duration",
        icon="mdi:sleep",
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_SLEEP,
        value_fn=lambda data: data.get("sleep_duration"),
    ),
    JudoSensorEntityDescription(
        key="micro_leak_setting",
        translation_key="micro_leak_setting",
        icon="mdi:water-alert-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_MICRO_LEAK,
        value_fn=lambda data: {0: "disabled", 1: "notify_only", 2: "notify_and_close"}.get(
            data.get("micro_leak_setting", 0), "unknown"
        ),
    ),
    JudoSensorEntityDescription(
        key="learning_remaining_water",
        translation_key="learning_remaining_water",
        icon="mdi:school-outline",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_LEARNING,
        value_fn=lambda data: data.get("learning_mode", {}).get("remaining_liters", 0),
    ),
    JudoSensorEntityDescription(
        key="absence_limit_flow_rate",
        translation_key="absence_limit_flow_rate",
        icon="mdi:speedometer-slow",
        native_unit_of_measurement="L/h",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_ABSENCE,
        value_fn=lambda data: data.get("absence_limits", {}).get("flow_rate", 0),
    ),
    JudoSensorEntityDescription(
        key="absence_limit_volume",
        translation_key="absence_limit_volume",
        icon="mdi:water-outline",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_ABSENCE,
        value_fn=lambda data: data.get("absence_limits", {}).get("volume", 0),
    ),
    JudoSensorEntityDescription(
        key="absence_limit_duration",
        translation_key="absence_limit_duration",
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.ZEWA_ABSENCE,
        value_fn=lambda data: data.get("absence_limits", {}).get("duration", 0),
    ),
    # --- i-dos eco sensors ---
    JudoSensorEntityDescription(
        key="idos_current_flow",
        translation_key="idos_current_flow",
        icon="mdi:water-pump",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="L/h",
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_status", {}).get("current_flow", 0),
    ),
    JudoSensorEntityDescription(
        key="idos_dosing_amount",
        translation_key="idos_dosing_amount",
        icon="mdi:beaker-outline",
        state_class=SensorStateClass.MEASUREMENT,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_status", {}).get("dosing_amount", 0),
    ),
    JudoSensorEntityDescription(
        key="idos_container_remaining",
        translation_key="idos_container_remaining",
        icon="mdi:bottle-tonic-outline",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_status", {}).get("container_remaining", 0),
    ),
    JudoSensorEntityDescription(
        key="idos_concentration",
        translation_key="idos_concentration",
        icon="mdi:flask-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: DOSING_CONCENTRATION.get(
            data.get("idos_status", {}).get("concentration", 0), "unknown"
        ),
    ),
    JudoSensorEntityDescription(
        key="idos_error_code",
        translation_key="idos_error_code",
        icon="mdi:alert-circle",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_status", {}).get("error_code", 0),
    ),
    JudoSensorEntityDescription(
        key="idos_warnings",
        translation_key="idos_warnings",
        icon="mdi:alert-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_status", {}).get("warnings", 0),
    ),
    JudoSensorEntityDescription(
        key="idos_type",
        translation_key="idos_type",
        icon="mdi:information-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.DOSING_STATUS,
        value_fn=lambda data: data.get("idos_config", {}).get("type", "unknown"),
    ),
    # --- i-fill sensors ---
    JudoSensorEntityDescription(
        key="ifill_max_fill_pressure",
        translation_key="ifill_max_fill_pressure",
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="bar",
        device_class=SensorDeviceClass.PRESSURE,
        required_capability=Capability.FILL_LIMITS,
        value_fn=lambda data: data.get("ifill_limits", {}).get("max_fill_pressure", 0),
    ),
    JudoSensorEntityDescription(
        key="ifill_cartridge_type",
        translation_key="ifill_cartridge_type",
        icon="mdi:filter",
        entity_category=EntityCategory.DIAGNOSTIC,
        required_capability=Capability.FILL_LIMITS,
        value_fn=lambda data: CARTRIDGE_TYPES.get(
            data.get("ifill_limits", {}).get("cartridge_type", 0), "unknown"
        ),
    ),
    JudoSensorEntityDescription(
        key="ifill_raw_water_hardness",
        translation_key="ifill_raw_water_hardness",
        icon="mdi:water-opacity",
        native_unit_of_measurement="°dH",
        required_capability=Capability.FILL_LIMITS,
        value_fn=lambda data: data.get("ifill_limits", {}).get("raw_water_hardness", 0),
    ),
    JudoSensorEntityDescription(
        key="ifill_max_conductivity",
        translation_key="ifill_max_conductivity",
        icon="mdi:flash-outline",
        required_capability=Capability.FILL_LIMITS,
        value_fn=lambda data: data.get("ifill_limits", {}).get("max_conductivity", 0),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JUDO sensor entities."""
    coordinator: JudoDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[JudoSensor] = []
    for description in SENSOR_DESCRIPTIONS:
        if (
            description.required_capability is None
            or coordinator.has_capability(description.required_capability)
        ):
            entities.append(JudoSensor(coordinator, description))

    async_add_entities(entities)


class JudoSensor(JudoEntity, SensorEntity):
    """Representation of a JUDO sensor."""

    entity_description: JudoSensorEntityDescription

    def __init__(
        self,
        coordinator: JudoDataCoordinator,
        description: JudoSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

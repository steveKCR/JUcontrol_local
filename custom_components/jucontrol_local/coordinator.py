"""Data update coordinator for JUDO devices."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import JudoApiClient, JudoConnectionError, JudoAuthError
from .const import DOMAIN
from .device_types import (
    Capability,
    DeviceFamily,
    DeviceTypeInfo,
    get_device_info,
)

_LOGGER = logging.getLogger(__name__)


class JudoDataCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data polling from JUDO device."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: JudoApiClient,
        device_type_code: int,
        scan_interval: int,
    ) -> None:
        """Initialize the coordinator."""
        self.client = client
        self.device_type_code = device_type_code
        self.device_info: DeviceTypeInfo | None = get_device_info(device_type_code)

        device_name = self.device_info.model if self.device_info else "Unknown JUDO"

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_name}",
            update_interval=timedelta(seconds=scan_interval),
        )

        # Static device data (fetched once)
        self.device_number: int = 0
        self.sw_version: str = "unknown"
        self.commissioning_date: str | None = None
        self.service_address: str = ""
        self._initial_fetch_done = False

        # For derived current flow rate (delta of total_water)
        self._prev_total_water: int | None = None
        self._prev_total_water_time: datetime | None = None

    @property
    def device_family(self) -> DeviceFamily | None:
        """Return the device family."""
        return self.device_info.family if self.device_info else None

    def has_capability(self, capability: Capability) -> bool:
        """Check if the device has a capability."""
        if self.device_info is None:
            return False
        return capability in self.device_info.capabilities

    async def _fetch_static_data(self) -> None:
        """Fetch data that doesn't change (serial, version, etc.)."""
        try:
            self.device_number = await self.client.get_device_number()
            self.sw_version = await self.client.get_sw_version()

            is_unix = self.device_family in (
                DeviceFamily.ZEWA,
                DeviceFamily.IDOS,
                DeviceFamily.IFILL,
            )
            self.commissioning_date = await self.client.get_commissioning_date(
                is_unix=is_unix
            )

            if self.has_capability(Capability.SERVICE_ADDRESS):
                self.service_address = await self.client.get_service_address()
        except (JudoConnectionError, JudoAuthError):
            _LOGGER.warning("Failed to fetch static device data")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch current data from the device."""
        if not self._initial_fetch_done:
            await self._fetch_static_data()
            self._initial_fetch_done = True

        data: dict[str, Any] = {
            "commissioning_date": self.commissioning_date,
            "service_address": self.service_address,
        }

        try:
            # Operating hours (all devices)
            if self.has_capability(Capability.OPERATING_HOURS):
                data["operating_hours"] = await self.client.get_operating_hours()

            # Water softener sensors
            if self.has_capability(Capability.WATER_HARDNESS):
                data["water_hardness"] = await self.client.get_water_hardness()

            if self.has_capability(Capability.SALT_SUPPLY):
                weight, days = await self.client.get_salt_supply()
                data["salt_weight"] = weight
                data["salt_range"] = days
                data["salt_shortage_warning"] = (
                    await self.client.get_salt_shortage_warning()
                )

            if self.has_capability(Capability.TOTAL_WATER):
                current_water = await self.client.get_total_water()
                data["total_water"] = current_water
                now = datetime.now(timezone.utc)
                if (
                    self._prev_total_water is not None
                    and self._prev_total_water_time is not None
                ):
                    delta_liters = current_water - self._prev_total_water
                    delta_seconds = (now - self._prev_total_water_time).total_seconds()
                    if delta_seconds > 0 and delta_liters >= 0:
                        data["current_flow_rate"] = round(
                            delta_liters / delta_seconds * 3600, 1
                        )
                    else:
                        data["current_flow_rate"] = 0.0
                else:
                    data["current_flow_rate"] = None
                self._prev_total_water = current_water
                self._prev_total_water_time = now

            if self.has_capability(Capability.SOFT_WATER):
                data["soft_water"] = await self.client.get_soft_water()

            if self.has_capability(Capability.HARDNESS_UNIT):
                data["hardness_unit"] = await self.client.get_hardness_unit()

            # Extraction limits
            if self.has_capability(Capability.EXTRACTION_LIMITS):
                data["max_extraction_duration"] = (
                    await self.client.get_max_extraction_duration()
                )
                data["max_extraction_volume"] = (
                    await self.client.get_max_extraction_volume()
                )
                data["max_flow_rate"] = await self.client.get_max_flow_rate()

            # ZEWA specific
            if self.has_capability(Capability.ZEWA_SLEEP):
                data["sleep_duration"] = await self.client.zewa_get_sleep_duration()

            if self.has_capability(Capability.ZEWA_MICRO_LEAK):
                data["micro_leak_setting"] = (
                    await self.client.zewa_get_micro_leak_setting()
                )

            if self.has_capability(Capability.ZEWA_LEARNING):
                data["learning_mode"] = (
                    await self.client.zewa_get_learning_mode_status()
                )

            if self.has_capability(Capability.ZEWA_ABSENCE):
                data["absence_limits"] = await self.client.zewa_get_absence_limits()

            # i-dos eco
            if self.has_capability(Capability.DOSING_STATUS):
                data["idos_status"] = await self.client.idos_get_status()
                data["idos_config"] = await self.client.idos_get_dosing_config()

            # i-fill
            if self.has_capability(Capability.FILL_LIMITS):
                data["ifill_limits"] = await self.client.ifill_get_limits()

        except JudoAuthError as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except JudoConnectionError as err:
            raise UpdateFailed(f"Connection failed: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

        return data

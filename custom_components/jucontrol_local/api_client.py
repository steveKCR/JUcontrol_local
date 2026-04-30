"""API client for JUDO water treatment devices."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

_HEX_PATTERN = re.compile(r"^[0-9a-fA-F]*$")
_CONNECT_TIMEOUT = 10
_READ_TIMEOUT = 15


def _validate_hex(value: str) -> str:
    """Validate that a string contains only hex characters."""
    if not _HEX_PATTERN.match(value):
        raise ValueError(f"Invalid hex string: {value!r}")
    return value


def parse_int_lsb(hex_str: str, num_bytes: int) -> int:
    """Parse a little-endian hex string to integer."""
    data = bytes.fromhex(hex_str[: num_bytes * 2])
    return int.from_bytes(data, byteorder="little")


def parse_int_msb(hex_str: str, num_bytes: int) -> int:
    """Parse a big-endian hex string to integer."""
    data = bytes.fromhex(hex_str[: num_bytes * 2])
    return int.from_bytes(data, byteorder="big")


def int_to_hex_lsb(value: int, num_bytes: int) -> str:
    """Convert integer to little-endian hex string."""
    return value.to_bytes(num_bytes, byteorder="little").hex().upper()


def int_to_hex_msb(value: int, num_bytes: int) -> str:
    """Convert integer to big-endian hex string."""
    return value.to_bytes(num_bytes, byteorder="big").hex().upper()


def parse_version(hex_str: str) -> str:
    """Parse 3-byte SW version hex to readable string.

    Format: byte0=minor_char, byte1=major_minor, byte2=major
    Example: 6b1502 -> 2.21k
    """
    b = bytes.fromhex(hex_str[:6])
    major = b[2]
    minor = b[1]
    patch_char = chr(b[0]) if 0x20 <= b[0] <= 0x7E else ""
    return f"{major}.{minor}{patch_char}"


def parse_operating_hours(hex_str: str) -> dict[str, int]:
    """Parse 4-byte operating hours.

    Format: 1 byte minutes, 1 byte hours, 2 bytes days (LSB)
    """
    b = bytes.fromhex(hex_str[:8])
    return {
        "minutes": b[0],
        "hours": b[1],
        "days": int.from_bytes(b[2:4], byteorder="little"),
    }


def parse_commissioning_date_softener(hex_str: str) -> str | None:
    """Parse 4-byte commissioning date for softener devices.

    Format varies by device. Try common patterns.
    """
    if len(hex_str) < 8:
        return None
    b = bytes.fromhex(hex_str[:8])
    # Try: day, month, year(2 bytes LSB)
    day = b[0]
    month = b[1]
    year = int.from_bytes(b[2:4], byteorder="little")
    if 1 <= day <= 31 and 1 <= month <= 12 and 2000 <= year <= 2100:
        return f"{year:04d}-{month:02d}-{day:02d}"
    return None


def parse_commissioning_date_unix(hex_str: str) -> str | None:
    """Parse 4-byte commissioning date as UNIX timestamp (ZEWA/i-dos/i-fill)."""
    if len(hex_str) < 8:
        return None
    import datetime

    timestamp = parse_int_lsb(hex_str, 4)
    if timestamp < 946684800 or timestamp > 4102444800:  # 2000-2100
        return None
    try:
        dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except (OSError, ValueError):
        return None


def parse_salt_supply(hex_str: str) -> tuple[int, int]:
    """Parse 4-byte salt supply response.

    Returns: (weight_grams, range_days)
    """
    weight = parse_int_lsb(hex_str[:4], 2)
    days = parse_int_lsb(hex_str[4:8], 2)
    return weight, days


def parse_idos_status(hex_str: str) -> dict[str, Any]:
    """Parse 29-byte i-dos eco status data."""
    if len(hex_str) < 58:
        return {}
    b = bytes.fromhex(hex_str[:58])
    return {
        "circuit_type": b[0],
        "operation_mode": b[1],
        "concentration": b[3],
        "error_code": int.from_bytes(b[5:7], byteorder="big"),
        "warnings": int.from_bytes(b[7:9], byteorder="big"),
        "dosing_amount": int.from_bytes(b[15:17], byteorder="big"),
        "current_flow": int.from_bytes(b[17:19], byteorder="big"),
        "container_remaining": int.from_bytes(b[19:21], byteorder="big"),
        "water_consumption": int.from_bytes(b[21:25], byteorder="little"),
    }


def parse_ifill_limits(hex_str: str) -> dict[str, Any]:
    """Parse 22-byte i-fill limit data."""
    if len(hex_str) < 44:
        return {}
    b = bytes.fromhex(hex_str[:44])
    return {
        "language": b[0],
        "unit": b[1],
        "raw_water_correction": b[2],
        "cartridge_type": b[3],
        "max_fill_cycles": b[5],
        "max_fill_pressure": b[6] / 10.0,
        "hysteresis_fill_pressure": b[7] / 10.0,
        "raw_water_hardness": int.from_bytes(b[8:10], byteorder="big"),
        "max_fill_time": int.from_bytes(b[10:12], byteorder="big"),
        "max_fill_volume": int.from_bytes(b[12:14], byteorder="big"),
        "heating_content": int.from_bytes(b[14:16], byteorder="big"),
        "max_conductivity": int.from_bytes(b[16:18], byteorder="big"),
        "cartridge_capacity": int.from_bytes(b[18:22], byteorder="big"),
    }


class JudoApiClient:
    """Client for communicating with JUDO devices via REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._host = host
        self._auth = aiohttp.BasicAuth(username, password)
        self._session = session
        self._base_url = f"http://{host}"
        self._timeout = aiohttp.ClientTimeout(
            connect=_CONNECT_TIMEOUT, total=_READ_TIMEOUT
        )

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    async def send_command(self, command_hex: str, data_hex: str = "") -> str:
        """Send a command to the device and return the response data.

        Args:
            command_hex: Command as hex string (e.g. "FF")
            data_hex: Optional data payload as hex string (e.g. "00")

        Returns:
            Response data as hex string.

        Raises:
            JudoConnectionError: On connection failure.
            JudoAuthError: On authentication failure.
            JudoCommandError: On command execution failure.
        """
        _validate_hex(command_hex)
        if data_hex:
            _validate_hex(data_hex)

        url = f"{self._base_url}/api/rest/{command_hex}{data_hex}"
        _LOGGER.debug("Sending command: GET %s", url)

        try:
            return await self._do_request(url)
        except _RetryableError:
            _LOGGER.debug("Device busy (429), retrying after 2s: %s", url)
            await asyncio.sleep(2)
            try:
                return await self._do_request(url)
            except _RetryableError as err:
                raise JudoConnectionError(
                    f"Device at {self._host} is busy, retry failed"
                ) from err

    async def _do_request(self, url: str) -> str:
        """Execute a single HTTP GET request to the device."""
        try:
            async with self._session.get(
                url, auth=self._auth, timeout=self._timeout
            ) as response:
                if response.status == 401:
                    raise JudoAuthError("Authentication failed")
                if response.status == 429:
                    raise _RetryableError()
                if response.status != 200:
                    raise JudoCommandError(
                        f"Command failed with status {response.status}"
                    )

                result = await response.json(content_type=None)
                _LOGGER.debug("Response: %s", result)

                if isinstance(result, dict) and "data" in result:
                    return str(result["data"])
                return ""

        except aiohttp.ClientError as err:
            raise JudoConnectionError(
                f"Connection to {self._host} failed: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise JudoConnectionError(
                f"Connection to {self._host} timed out"
            ) from err

    # --- Info commands (all devices) ---

    async def get_device_type(self) -> int:
        """Read device type (cmd 0xFF)."""
        data = await self.send_command("FF", "00")
        return int(data, 16) if data else 0

    async def get_device_number(self) -> int:
        """Read device serial number (cmd 0x06)."""
        data = await self.send_command("06", "00")
        return parse_int_lsb(data, 4) if data else 0

    async def get_sw_version(self) -> str:
        """Read software version (cmd 0x01)."""
        data = await self.send_command("01", "00")
        return parse_version(data) if data and len(data) >= 6 else "unknown"

    async def get_commissioning_date(self, is_unix: bool = False) -> str | None:
        """Read commissioning date (cmd 0x0E)."""
        data = await self.send_command("0E", "00")
        if not data or len(data) < 8:
            return None
        if is_unix:
            return parse_commissioning_date_unix(data)
        return parse_commissioning_date_softener(data)

    async def get_operating_hours(self) -> dict[str, int]:
        """Read operating hours (cmd 0x25)."""
        data = await self.send_command("25", "00")
        if not data or len(data) < 8:
            return {"minutes": 0, "hours": 0, "days": 0}
        return parse_operating_hours(data)

    async def get_service_address(self) -> str:
        """Read service address (cmd 0x58)."""
        data = await self.send_command("58", "00")
        if not data:
            return ""
        try:
            return bytes.fromhex(data).decode("ascii").strip()
        except (ValueError, UnicodeDecodeError):
            return data

    # --- Water softener commands ---

    async def get_water_hardness(self) -> int:
        """Read desired water hardness in device units (cmd 0x51)."""
        data = await self.send_command("51", "00")
        return parse_int_lsb(data, 2) if data and len(data) >= 4 else 0

    async def set_water_hardness(self, value: int) -> None:
        """Set desired water hardness in °dH (cmd 0x30)."""
        if not 1 <= value <= 30:
            raise ValueError(f"Hardness must be 1-30, got {value}")
        hex_val = f"{value:02X}"
        await self.send_command("30", f"00{hex_val}")

    async def get_salt_supply(self) -> tuple[int, int]:
        """Read salt supply (cmd 0x56). Returns (weight_g, range_days)."""
        data = await self.send_command("56", "00")
        if not data or len(data) < 8:
            return (0, 0)
        return parse_salt_supply(data)

    async def set_salt_supply(self, grams: int) -> None:
        """Set salt supply weight in grams (cmd 0x56)."""
        if not 0 <= grams <= 65535:
            raise ValueError(f"Salt supply must be 0-65535g, got {grams}")
        hex_val = int_to_hex_lsb(grams, 2)
        await self.send_command("56", f"00{hex_val}")

    async def get_salt_shortage_warning(self) -> int:
        """Read salt shortage warning in days (cmd 0x57)."""
        data = await self.send_command("57", "00")
        return int(data, 16) if data else 0

    async def set_salt_shortage_warning(self, days: int) -> None:
        """Set salt shortage warning in days (cmd 0x57)."""
        if not 1 <= days <= 90:
            raise ValueError(f"Warning days must be 1-90, got {days}")
        await self.send_command("57", f"00{days:02X}")

    async def get_hardness_unit(self) -> int:
        """Read hardness unit (cmd 0x23). Returns index 0-6."""
        data = await self.send_command("23", "00")
        return int(data, 16) if data else 0

    async def set_hardness_unit(self, unit: int) -> None:
        """Set hardness unit (cmd 0x24). 0=°dH, 1=°eH, 2=°fH, etc."""
        if not 0 <= unit <= 6:
            raise ValueError(f"Unit must be 0-6, got {unit}")
        await self.send_command("24", f"00{unit:02X}")

    async def start_regeneration(self) -> None:
        """Start regeneration (cmd 0x35)."""
        await self.send_command("35", "0000")

    # --- Water volume commands ---

    async def get_total_water(self) -> int:
        """Read total water volume in liters (cmd 0x28)."""
        data = await self.send_command("28", "00")
        return parse_int_lsb(data, 4) if data and len(data) >= 8 else 0

    async def get_soft_water(self) -> int:
        """Read soft water volume in liters (cmd 0x29)."""
        data = await self.send_command("29", "00")
        return parse_int_lsb(data, 4) if data and len(data) >= 8 else 0

    # --- Leak protection commands (softener variants) ---

    async def close_leak_protection(self) -> None:
        """Close leak protection valve (cmd 0x3C)."""
        await self.send_command("3C", "00")

    async def open_leak_protection(self) -> None:
        """Open leak protection valve (cmd 0x3D)."""
        await self.send_command("3D", "00")

    # --- Limit settings (softener) ---

    async def get_max_extraction_duration(self) -> int:
        """Read max extraction duration in minutes (cmd 0x3E)."""
        data = await self.send_command("3E", "00")
        return int(data, 16) if data else 0

    async def set_max_extraction_duration(self, minutes: int) -> None:
        """Set max extraction duration (cmd 0x3E). 0=disabled, 1-255 min."""
        if not 0 <= minutes <= 255:
            raise ValueError(f"Duration must be 0-255, got {minutes}")
        await self.send_command("3E", f"00{minutes:02X}")

    async def get_max_extraction_volume(self) -> int:
        """Read max extraction volume in liters (cmd 0x3F)."""
        data = await self.send_command("3F", "00")
        return parse_int_lsb(data, 2) if data and len(data) >= 4 else 0

    async def set_max_extraction_volume(self, liters: int) -> None:
        """Set max extraction volume in liters (cmd 0x3F). 0=disabled."""
        if not 0 <= liters <= 65535:
            raise ValueError(f"Volume must be 0-65535, got {liters}")
        hex_val = int_to_hex_lsb(liters, 2)
        await self.send_command("3F", f"00{hex_val}")

    async def get_max_flow_rate(self) -> int:
        """Read max flow rate in l/h (cmd 0x40)."""
        data = await self.send_command("40", "00")
        return parse_int_lsb(data, 2) if data and len(data) >= 4 else 0

    async def set_max_flow_rate(self, liters_per_hour: int) -> None:
        """Set max flow rate in l/h (cmd 0x40). 0=disabled."""
        if not 0 <= liters_per_hour <= 65535:
            raise ValueError(f"Flow rate must be 0-65535, got {liters_per_hour}")
        hex_val = int_to_hex_lsb(liters_per_hour, 2)
        await self.send_command("40", f"00{hex_val}")

    # --- Vacation mode (softener) ---

    async def set_vacation_mode_softener(self, flags: int) -> None:
        """Set vacation mode for softener devices (cmd 0x41).

        flags bitmask (i-soft SAFE+):
          0x00: off
          0x03: U1 (bit 0 active + bit 1 U1)
          0x05: U2 (bit 0 active + bit 2 U2)
          0x09: U3 (bit 0 active + bit 3 U3)
        """
        await self.send_command("41", f"00{flags:02X}")

    # --- ZEWA i-SAFE commands ---

    async def zewa_close_leak_protection(self) -> None:
        """Close ZEWA leak protection (cmd 0x51)."""
        await self.send_command("51", "00")

    async def zewa_open_leak_protection(self) -> None:
        """Open ZEWA leak protection (cmd 0x52)."""
        await self.send_command("52", "00")

    async def zewa_start_sleep_mode(self) -> None:
        """Start ZEWA sleep mode (cmd 0x54)."""
        await self.send_command("54", "00")

    async def zewa_stop_sleep_mode(self) -> None:
        """Stop ZEWA sleep mode (cmd 0x55)."""
        await self.send_command("55", "00")

    async def zewa_set_vacation_type(self, mode: int) -> None:
        """Set ZEWA vacation mode type (cmd 0x56). 0=off, 1=U1, 2=U2, 3=U3."""
        if not 0 <= mode <= 3:
            raise ValueError(f"Vacation mode must be 0-3, got {mode}")
        await self.send_command("56", f"00{mode:02X}")
        # Start or stop vacation based on mode
        if mode > 0:
            await self.send_command("57", "00")  # Start vacation
        else:
            await self.send_command("58", "00")  # Stop vacation

    async def zewa_reset_notification(self) -> None:
        """Reset ZEWA notification (cmd 0x63)."""
        await self.send_command("63", "00")

    async def zewa_start_micro_leak_test(self) -> None:
        """Start micro-leak test (cmd 0x5C)."""
        await self.send_command("5C", "00")

    async def zewa_start_learning_mode(self) -> None:
        """Start learning mode (cmd 0x5D)."""
        await self.send_command("5D", "00")

    async def zewa_get_sleep_duration(self) -> int:
        """Read sleep mode duration in hours (cmd 0x66)."""
        data = await self.send_command("66", "00")
        return int(data, 16) if data else 0

    async def zewa_set_sleep_duration(self, hours: int) -> None:
        """Set sleep mode duration (cmd 0x53). 1-10 hours."""
        if not 1 <= hours <= 10:
            raise ValueError(f"Duration must be 1-10h, got {hours}")
        await self.send_command("53", f"00{hours:02X}")

    async def zewa_get_micro_leak_setting(self) -> int:
        """Read micro-leak setting (cmd 0x65). 0=off, 1=notify, 2=notify+close."""
        data = await self.send_command("65", "00")
        return int(data, 16) if data else 0

    async def zewa_set_micro_leak(self, mode: int) -> None:
        """Set micro-leak mode (cmd 0x5B). 0=off, 1=notify, 2=notify+close."""
        if not 0 <= mode <= 2:
            raise ValueError(f"Mode must be 0-2, got {mode}")
        await self.send_command("5B", f"00{mode:02X}")

    async def zewa_get_learning_mode_status(self) -> dict[str, Any]:
        """Read learning mode status (cmd 0x64)."""
        data = await self.send_command("64", "00")
        if not data or len(data) < 6:
            return {"active": False, "remaining_liters": 0}
        b = bytes.fromhex(data[:6])
        return {
            "active": b[0] == 1,
            "remaining_liters": int.from_bytes(b[1:3], byteorder="big"),
        }

    async def zewa_get_absence_limits(self) -> dict[str, int]:
        """Read absence limits (cmd 0x5E)."""
        data = await self.send_command("5E", "00")
        if not data or len(data) < 12:
            return {"flow_rate": 0, "volume": 0, "duration": 0}
        return {
            "flow_rate": parse_int_lsb(data[0:4], 2),
            "volume": parse_int_lsb(data[4:8], 2),
            "duration": parse_int_lsb(data[8:12], 2),
        }

    # --- i-dos eco commands ---

    async def idos_get_status(self) -> dict[str, Any]:
        """Read i-dos eco status data (cmd 0x43)."""
        data = await self.send_command("43", "00")
        return parse_idos_status(data) if data else {}

    async def idos_set_concentration(self, level: int) -> None:
        """Set dosing concentration (cmd 0x52). 1=min, 2=norm, 3=max."""
        if not 1 <= level <= 3:
            raise ValueError(f"Concentration must be 1-3, got {level}")
        await self.send_command("52", f"0000{level:02X}")

    async def idos_set_pump_mode(self, mode: int, rpm: int = 0) -> None:
        """Set pump operation mode (cmd 0x53).

        mode: 0=off, 1=auto, 2=manual, 3=single
        rpm: pump speed for manual mode
        """
        if not 0 <= mode <= 3:
            raise ValueError(f"Mode must be 0-3, got {mode}")
        rpm_hex = int_to_hex_msb(rpm, 2)
        await self.send_command("53", f"00{mode:02X}{rpm_hex}")

    async def idos_get_dosing_config(self) -> dict[str, Any]:
        """Read dosing configuration (cmd 0x63)."""
        data = await self.send_command("63", "00")
        if not data or len(data) < 4:
            return {}
        b = bytes.fromhex(data[:4])
        type_names = {1: "JUL-W", 2: "JUL-C", 3: "JUL-H", 4: "JUL-S", 5: "JUL-SW"}
        size_names = {1: "3L", 2: "6L", 3: "25L", 4: "60L"}
        return {
            "type": type_names.get(b[0], f"unknown({b[0]})"),
            "size": size_names.get(b[1], f"unknown({b[1]})"),
        }

    # --- i-fill commands ---

    async def ifill_get_limits(self) -> dict[str, Any]:
        """Read i-fill limit data (cmd 0x42)."""
        data = await self.send_command("42", "00")
        return parse_ifill_limits(data) if data else {}

    async def ifill_set_valve_mode(self, mode: int) -> None:
        """Set fill valve mode (cmd 0x53). 0=auto, 1=open, 2=close."""
        if not 0 <= mode <= 2:
            raise ValueError(f"Mode must be 0-2, got {mode}")
        await self.send_command("53", f"00{mode:02X}")

    async def ifill_set_alarm_relay(self, mode: int) -> None:
        """Set alarm relay (cmd 0x54). 0=auto, 128=off, 129=on."""
        if mode not in (0, 128, 129):
            raise ValueError(f"Mode must be 0/128/129, got {mode}")
        await self.send_command("54", f"00{mode:02X}")

    # --- i-soft PRO scene commands ---

    async def pro_activate_scene(self, scene: int, duration_hex: str = "FFFF") -> None:
        """Activate a scene immediately (cmd 0x36).

        scene: 0-10 (0=Alltag, 1=Körperpflege, 2=Garten, 3=Urlaub, etc.)
        duration_hex: HH:MM as hex, FFFF=infinite
        """
        if not 0 <= scene <= 10:
            raise ValueError(f"Scene must be 0-10, got {scene}")
        _validate_hex(duration_hex)
        scene_hex = f"{scene:02X}"
        await self.send_command("36", f"00{scene_hex}{duration_hex}")

    async def pro_reset_scene(self, scene: int) -> None:
        """Reset a scene to defaults (cmd 0x38)."""
        if not 1 <= scene <= 10:
            raise ValueError(f"Scene must be 1-10, got {scene}")
        await self.send_command("38", f"00{scene:02X}")


class JudoConnectionError(Exception):
    """Error connecting to JUDO device."""


class JudoAuthError(Exception):
    """Authentication error with JUDO device."""


class JudoCommandError(Exception):
    """Command execution error on JUDO device."""


class _RetryableError(Exception):
    """Internal: device is busy, caller should retry after delay."""

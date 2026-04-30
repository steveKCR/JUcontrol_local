"""Config flow for JUcontrol local integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api_client import JudoApiClient, JudoAuthError, JudoConnectionError
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    SCAN_INTERVAL_OPTIONS,
)
from .device_types import get_device_info

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): str,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.In(
            SCAN_INTERVAL_OPTIONS
        ),
    }
)


class JudoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JUcontrol local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input[CONF_USERNAME]
            password = user_input[CONF_PASSWORD]

            session = async_get_clientsession(self.hass)
            client = JudoApiClient(host, username, password, session)

            try:
                device_type = await client.get_device_type()
                device_number = await client.get_device_number()
            except JudoAuthError:
                errors["base"] = "invalid_auth"
            except JudoConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                device_info = get_device_info(device_type)
                if device_info is None:
                    errors["base"] = "unknown_device"
                else:
                    unique_id = f"judo_{device_number}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"JUDO {device_info.model}",
                        data={
                            CONF_HOST: host,
                            CONF_USERNAME: username,
                            CONF_PASSWORD: password,
                            CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                            "device_type": device_type,
                            "device_number": device_number,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> JudoOptionsFlow:
        """Get the options flow for this handler."""
        return JudoOptionsFlow(config_entry)


class JudoOptionsFlow(OptionsFlow):
    """Handle options flow for JUcontrol local."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL
        ) or self._config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=current_interval
                    ): vol.In(SCAN_INTERVAL_OPTIONS),
                }
            ),
        )

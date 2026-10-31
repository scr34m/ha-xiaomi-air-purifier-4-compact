"""Config flow for Xiaomi Smart Air Purifier 4 Compact integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import format_mac

from .api import PurifierError, XiaomiAirPurifier
from .const import (
    CONF_IP,
    CONF_MAC,
    CONF_MODEL,
    CONF_NAME,
    CONF_TOKEN,
    DEFAULT_NAME,
    DOMAIN,
    SUPPORTED_MODELS,
)

_LOGGER = logging.getLogger(__name__)


class XiaomiAirPurifierConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Smart Air Purifier 4 Compact."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            ip = user_input[CONF_IP].strip()
            token = user_input[CONF_TOKEN].strip().lower()
            name = user_input.get(CONF_NAME, DEFAULT_NAME).strip()

            if len(token) != 32 or any(c not in "0123456789abcdef" for c in token):
                errors[CONF_TOKEN] = "invalid_token"
            else:
                try:
                    client = XiaomiAirPurifier(ip, token)
                    info = await self.hass.async_add_executor_job(client.info)
                except PurifierError as err:
                    _LOGGER.error("Cannot connect to Xiaomi Air Purifier at %s: %s", ip, err)
                    errors["base"] = "cannot_connect"
                except Exception as err:
                    _LOGGER.exception("Unexpected exception during config flow: %s", err)
                    errors["base"] = "unknown"
                else:
                    if info.model not in SUPPORTED_MODELS:
                        _LOGGER.error("Unsupported model at %s: %s", ip, info.model)
                        errors["base"] = "unsupported_model"
                    else:
                        # The MAC address survives IP changes; the IP is a fallback.
                        if info.mac:
                            unique_id = format_mac(info.mac)
                        else:
                            unique_id = f"xiaomi_air_purifier_{ip.replace('.', '_')}"
                        await self.async_set_unique_id(unique_id)
                        self._abort_if_unique_id_configured(updates={CONF_IP: ip, CONF_TOKEN: token})

                        return self.async_create_entry(
                            title=name,
                            data={
                                CONF_IP: ip,
                                CONF_TOKEN: token,
                                CONF_NAME: name,
                                CONF_MAC: info.mac,
                                CONF_MODEL: info.model,
                            },
                        )

        schema = vol.Schema(
            {
                vol.Required(CONF_IP, default=(user_input or {}).get(CONF_IP, "")): cv.string,
                vol.Required(CONF_TOKEN): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

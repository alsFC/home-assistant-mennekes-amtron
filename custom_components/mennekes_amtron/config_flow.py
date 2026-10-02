"""Config flow for Mennekes AMTRON Professional."""
from __future__ import annotations
import logging
import voluptuous as vol
from modbus_connection import ModbusError, ModbusTcpParams
from homeassistant import config_entries
from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from .const import (
    CONF_RFID_COMPANY, CONF_RFID_GUEST, DEFAULT_PORT, DEFAULT_UNIT_ID, DOMAIN,
)
from .device import MennekesAmtronDevice

_LOGGER = logging.getLogger(__name__)

async def _validate(hass: HomeAssistant, data: dict) -> None:
    params = ModbusTcpParams(host=data[CONF_HOST], port=data[CONF_PORT])
    async with async_get_temporary_unit(hass, params, DEFAULT_UNIT_ID) as unit:
        await MennekesAmtronDevice(unit).async_validate()

class MennekesAmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            host, port = user_input[CONF_HOST], user_input[CONF_PORT]
            await self.async_set_unique_id(f"{host}:{port}:{DEFAULT_UNIT_ID}")
            self._abort_if_unique_id_configured()
            try:
                await _validate(self.hass, user_input)
            except (ModbusError, TimeoutError, ValueError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("AMTRON validation failed with unexpected error")
                errors["base"] = "unknown"
            else:
                data = dict(user_input)
                data["unit_id"] = DEFAULT_UNIT_ID
                return self.async_create_entry(title="Mennekes AMTRON Professional", data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(int, vol.Range(min=1, max=65535)),
            }),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return MennekesAmtronOptionsFlow(config_entry)

class MennekesAmtronOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                for key in (CONF_RFID_COMPANY, CONF_RFID_GUEST):
                    value = user_input.get(key, "").strip()
                    if value:
                        raw = value.encode("ascii")
                        if len(raw) > 20:
                            raise ValueError
                    user_input[key] = value
            except (UnicodeEncodeError, ValueError):
                errors["base"] = "invalid_rfid"
            else:
                return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_RFID_COMPANY,
                    default=self._entry.options.get(CONF_RFID_COMPANY, ""),
                ): str,
                vol.Optional(
                    CONF_RFID_GUEST,
                    default=self._entry.options.get(CONF_RFID_GUEST, ""),
                ): str,
            }),
            errors=errors,
        )

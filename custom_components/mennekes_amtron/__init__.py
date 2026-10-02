"""Mennekes AMTRON Professional integration."""
from __future__ import annotations

import logging

from modbus_connection import ModbusTcpParams
from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .const import CONF_UNIT_ID, DOMAIN, PLATFORMS
from .coordinator import AmtronCoordinator
from .device import MennekesAmtronDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up AMTRON from a config entry."""
    _LOGGER.warning(
        "AMTRON runtime setup: host=%s port=%s unit=%s",
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_UNIT_ID],
    )
    unit = async_get_unit(
        hass,
        entry,
        ModbusTcpParams(host=entry.data[CONF_HOST], port=entry.data[CONF_PORT]),
        entry.data[CONF_UNIT_ID],
    )
    device = MennekesAmtronDevice(unit)
    coordinator = AmtronCoordinator(hass, entry, device)

    _LOGGER.warning("AMTRON runtime setup: starting first refresh")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.warning(
        "AMTRON runtime setup: first refresh succeeded; vehicle_state=%s total_power=%s",
        coordinator.data.vehicle_state,
        coordinator.data.total_power,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload AMTRON config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when integration options change."""
    await hass.config_entries.async_reload(entry.entry_id)

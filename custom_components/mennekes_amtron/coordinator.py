"""Polling coordinator for Mennekes AMTRON Professional."""
from __future__ import annotations
from datetime import datetime, timedelta
import logging
from modbus_connection import ModbusError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from .const import (
    CURRENT_LIMITS_INTERVAL, DEFAULT_FAST_INTERVAL, FIRMWARE_INTERVAL,
    GENERAL_STATUS_INTERVAL, HEMS_INTERVAL, METER_INTERVAL, SESSION_INTERVAL,
    STATUS_INTERVAL, VEHICLE_INTERVAL,
)
from .device import MennekesAmtronDevice

_LOGGER = logging.getLogger(__name__)

class AmtronCoordinator(DataUpdateCoordinator):
    """Serialize all AMTRON polling through one coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device: MennekesAmtronDevice) -> None:
        self.device = device
        self._last_vehicle: datetime | None = None
        self._last_meter: datetime | None = None
        self._last_session: datetime | None = None
        self._last_status: datetime | None = None
        self._last_hems: datetime | None = None
        self._last_general_status: datetime | None = None
        self._last_current_limits: datetime | None = None
        self._last_firmware: datetime | None = None
        interval = int(entry.options.get("fast_interval", DEFAULT_FAST_INTERVAL))
        super().__init__(hass, _LOGGER, name="Mennekes AMTRON Professional",
                         update_interval=timedelta(seconds=interval))

    @staticmethod
    def _due(last, interval, now) -> bool:
        return last is None or now - last >= interval

    async def async_refresh_after_command(self) -> None:
        """Refresh only command-related state without running a full poll cycle."""
        now = dt_util.utcnow()
        try:
            await self.device.async_read_status()
            self._last_status = now
            await self.device.async_read_vehicle_state()
            self._last_vehicle = now
        except (ModbusError, TimeoutError, ConnectionError) as err:
            raise UpdateFailed(f"AMTRON post-command refresh failed: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected AMTRON post-command refresh error")
            raise UpdateFailed(f"Unexpected AMTRON post-command refresh error: {err}") from err
        self.async_set_updated_data(self.device.data)

    async def _async_update_data(self):
        now = dt_util.utcnow()
        try:
            # Critical automation value: one request every 10 s.
            await self.device.async_read_power()

            # Vehicle state changes much less frequently.
            if self._due(self._last_vehicle, VEHICLE_INTERVAL, now):
                await self.device.async_read_vehicle_state()
                self._last_vehicle = now

            if self._due(self._last_status, STATUS_INTERVAL, now):
                await self.device.async_read_status()
                self._last_status = now

            if self._due(self._last_meter, METER_INTERVAL, now):
                await self.device.async_read_meter()
                self._last_meter = now

            if self._due(self._last_hems, HEMS_INTERVAL, now):
                await self.device.async_read_hems()
                self._last_hems = now

            if self._due(self._last_general_status, GENERAL_STATUS_INTERVAL, now):
                await self.device.async_read_general_status()
                self._last_general_status = now

            if self._due(self._last_current_limits, CURRENT_LIMITS_INTERVAL, now):
                await self.device.async_read_current_limits()
                self._last_current_limits = now

            if self._due(self._last_firmware, FIRMWARE_INTERVAL, now):
                await self.device.async_read_firmware()
                self._last_firmware = now

            if self.device.data.vehicle_state in (2, 3) and self._due(
                self._last_session, SESSION_INTERVAL, now
            ):
                await self.device.async_read_session()
                self._last_session = now

            return self.device.data
        except (ModbusError, TimeoutError, ConnectionError) as err:
            raise UpdateFailed(f"AMTRON Modbus communication failed: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected AMTRON polling error")
            raise UpdateFailed(f"Unexpected AMTRON polling error: {err}") from err

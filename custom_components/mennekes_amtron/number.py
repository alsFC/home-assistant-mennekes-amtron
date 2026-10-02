"""HEMS current limit control for Mennekes AMTRON Professional."""
from __future__ import annotations
import asyncio
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import AmtronCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AmtronHemsCurrentLimit(coordinator, entry)])

class AmtronHemsCurrentLimit(CoordinatorEntity[AmtronCoordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "hems_current_limit"
    _attr_native_min_value = 0
    _attr_native_max_value = 32
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_hems_current_limit"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, manufacturer="MENNEKES",
            name="AMTRON Professional",
            configuration_url=f"http://{entry.data['host']}",
        )

    @property
    def native_value(self):
        return self.coordinator.data.hems_current_limit_a

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.device.async_set_hems_current_limit(int(value))
        await asyncio.sleep(0.5)
        await self.coordinator.device.async_read_hems()
        self.coordinator.async_set_updated_data(self.coordinator.device.data)

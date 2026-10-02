"""Sensors for Mennekes AMTRON Professional."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AmtronCoordinator

VEHICLE_STATES = {1: "disconnected", 2: "connected", 3: "charging"}
OCPP_STATES = {0: "available", 1: "occupied", 2: "reserved", 3: "unavailable", 4: "faulted", 5: "preparing", 6: "charging", 7: "suspended_evse", 8: "suspended_ev", 9: "finishing"}

@dataclass(frozen=True, kw_only=True)
class AmtronSensorDescription(SensorEntityDescription):
    value_fn: Callable = lambda data: None

SENSORS = (
    AmtronSensorDescription(key="firmware", entity_category=EntityCategory.DIAGNOSTIC, translation_key="firmware", value_fn=lambda d: d.firmware),
    AmtronSensorDescription(key="cp_availability", entity_category=EntityCategory.DIAGNOSTIC, translation_key="cp_availability", device_class=SensorDeviceClass.ENUM, options=["unavailable", "available"], value_fn=lambda d: {0: "unavailable", 1: "available"}.get(d.cp_availability)),
    AmtronSensorDescription(key="safe_current", entity_category=EntityCategory.DIAGNOSTIC, translation_key="safe_current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, value_fn=lambda d: d.safe_current_a),
    AmtronSensorDescription(key="operator_current_limit", entity_category=EntityCategory.DIAGNOSTIC, translation_key="operator_current_limit", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, value_fn=lambda d: d.operator_current_limit_a),
    AmtronSensorDescription(key="plug_lock_status", translation_key="plug_lock_status", device_class=SensorDeviceClass.ENUM, options=["unlocked", "locked"], value_fn=lambda d: {0: "unlocked", 1: "locked"}.get(d.plug_lock_status)),
    AmtronSensorDescription(key="meter_total_power", translation_key="meter_total_power", device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfPower.WATT, value_fn=lambda d: d.total_power),
    AmtronSensorDescription(key="vehicle_state", translation_key="vehicle_state", device_class=SensorDeviceClass.ENUM, options=list(VEHICLE_STATES.values()), value_fn=lambda d: VEHICLE_STATES.get(d.vehicle_state, f"unknown_{d.vehicle_state}")),
    AmtronSensorDescription(key="ocpp_cp_status", translation_key="ocpp_cp_status", device_class=SensorDeviceClass.ENUM, options=list(OCPP_STATES.values()), value_fn=lambda d: OCPP_STATES.get(d.ocpp_status, f"unknown_{d.ocpp_status}")),
    AmtronSensorDescription(key="meter_current_l1", translation_key="meter_current_l1", device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, value_fn=lambda d: d.current_l1_ma),
    AmtronSensorDescription(key="meter_current_l2", translation_key="meter_current_l2", device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, value_fn=lambda d: d.current_l2_ma),
    AmtronSensorDescription(key="meter_current_l3", translation_key="meter_current_l3", device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE, value_fn=lambda d: d.current_l3_ma),
    AmtronSensorDescription(key="meter_total_energy", translation_key="meter_total_energy", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL, native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, value_fn=lambda d: d.total_energy_wh),
    AmtronSensorDescription(key="meter_voltage_l1", translation_key="meter_voltage_l1", device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, value_fn=lambda d: d.voltage_l1_v),
    AmtronSensorDescription(key="meter_voltage_l2", translation_key="meter_voltage_l2", device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, value_fn=lambda d: d.voltage_l2_v),
    AmtronSensorDescription(key="meter_voltage_l3", translation_key="meter_voltage_l3", device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT, native_unit_of_measurement=UnitOfElectricPotential.VOLT, value_fn=lambda d: d.voltage_l3_v),
    AmtronSensorDescription(key="ev_max_current", translation_key="ev_max_current", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, value_fn=lambda d: d.ev_max_current_a),
    AmtronSensorDescription(key="ev_charged_energy", translation_key="ev_charged_energy", device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, native_unit_of_measurement=UnitOfEnergy.WATT_HOUR, value_fn=lambda d: d.session_energy_wh),
    AmtronSensorDescription(key="ev_charge_duration", translation_key="ev_charge_duration", device_class=SensorDeviceClass.DURATION, native_unit_of_measurement=UnitOfTime.SECONDS, value_fn=lambda d: d.charge_duration_s),
    AmtronSensorDescription(key="active_id_tag", translation_key="active_id_tag", value_fn=lambda d: d.active_rfid),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: AmtronCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(AmtronSensor(coordinator, entry, description) for description in SENSORS)

class AmtronSensor(CoordinatorEntity[AmtronCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: AmtronCoordinator, entry: ConfigEntry, description: AmtronSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, manufacturer="MENNEKES", name="AMTRON Professional", configuration_url=f"http://{entry.data['host']}")

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data)

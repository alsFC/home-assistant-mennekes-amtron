"""Actions for Mennekes AMTRON Professional."""
from __future__ import annotations
import asyncio
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_RFID_COMPANY, CONF_RFID_GUEST, DOMAIN
from .coordinator import AmtronCoordinator

LABEL_COMPANY = "Firmenwagen"
LABEL_GUEST = "Fremd"
CONF_RFID_SELECTED = "rfid_selected"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AmtronSendRfidButton(coordinator, entry)])

class AmtronSendRfidButton(CoordinatorEntity[AmtronCoordinator], ButtonEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "send_rfid_authorization"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_send_rfid_authorization"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            manufacturer="MENNEKES",
            name="AMTRON Professional",
            configuration_url=f"http://{entry.data['host']}",
        )

    async def async_press(self) -> None:
        selected = self._entry.options.get(CONF_RFID_SELECTED, LABEL_COMPANY)
        key = CONF_RFID_COMPANY if selected == LABEL_COMPANY else CONF_RFID_GUEST
        tag = self._entry.options.get(key, "").strip()
        if not tag:
            raise ValueError(f"No RFID ID configured for {selected}")
        await self.coordinator.device.async_authorize_rfid(tag)
        # The AMTRON processes the presented IDTag asynchronously.
        await asyncio.sleep(1.0)
        await self.coordinator.async_refresh_after_command()

"""RFID authorization select for Mennekes AMTRON Professional."""
from __future__ import annotations
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_RFID_COMPANY, CONF_RFID_GUEST, DOMAIN
from .coordinator import AmtronCoordinator

LABEL_COMPANY = "Firmenwagen"
LABEL_GUEST = "Fremd"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AmtronRfidSelect(coordinator, entry)])

class AmtronRfidSelect(CoordinatorEntity[AmtronCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "rfid_authorization"
    _attr_options = [LABEL_COMPANY, LABEL_GUEST]

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_rfid_authorization"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, manufacturer="MENNEKES",
            name="AMTRON Professional",
            configuration_url=f"http://{entry.data['host']}",
        )

    def _tag_for(self, option: str) -> str:
        key = CONF_RFID_COMPANY if option == LABEL_COMPANY else CONF_RFID_GUEST
        tag = self._entry.options.get(key, "").strip()
        if not tag:
            raise ValueError(f"No RFID ID configured for {option}")
        return tag

    @property
    def current_option(self):
        return self._entry.options.get("rfid_selected", LABEL_COMPANY)

    async def async_select_option(self, option: str) -> None:
        if option not in self.options:
            raise ValueError(f"Unknown RFID option: {option}")
        new_options = dict(self._entry.options)
        new_options["rfid_selected"] = option
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.async_write_ha_state()

"""Switch platform for Panda Breath."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_WORK_ON
from .coordinator import PandaBreathCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PandaBreathCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PandaBreathSwitch(coordinator, entry)])


class PandaBreathSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to turn Panda Breath on or off."""

    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_icon = "mdi:power"

    def __init__(self, coordinator: PandaBreathCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Panda Breath",
            "manufacturer": "BIQU",
            "model": "Panda Breath",
            "sw_version": coordinator.data.get("fw_version", "unknown"),
        }

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(KEY_WORK_ON, False))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.send_settings({KEY_WORK_ON: True})

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.send_settings({KEY_WORK_ON: False})

"""Select platform for Panda Breath."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_WORK_MODE,
    WORK_MODE_MAP,
    WORK_MODE_REVERSE_MAP,
)
from .coordinator import PandaBreathCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PandaBreathCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([PandaBreathModeSelect(coordinator, entry)])


class PandaBreathModeSelect(CoordinatorEntity, SelectEntity):
    """Select entity to choose Panda Breath work mode."""

    _attr_has_entity_name = True
    _attr_name = "Work Mode"
    _attr_icon = "mdi:cog"
    _attr_options = list(WORK_MODE_MAP.values())

    def __init__(self, coordinator: PandaBreathCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_work_mode"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Panda Breath",
            "manufacturer": "BIQU",
            "model": "Panda Breath",
        }

    @property
    def current_option(self) -> str | None:
        mode_num = self.coordinator.data.get(KEY_WORK_MODE, 1)
        return WORK_MODE_MAP.get(mode_num, "Auto")

    async def async_select_option(self, option: str) -> None:
        mode_num = WORK_MODE_REVERSE_MAP.get(option, 1)
        await self.coordinator.send_settings({KEY_WORK_MODE: mode_num})

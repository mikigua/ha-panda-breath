"""Sensor platform for Panda Breath."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_WAREHOUSE_TEMPER, KEY_FW_VERSION
from .coordinator import PandaBreathCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PandaBreathCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        PandaBreathTemperatureSensor(coordinator, entry),
        PandaBreathFirmwareSensor(coordinator, entry),
    ])


class PandaBreathTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current chamber temperature."""

    _attr_has_entity_name = True
    _attr_name = "Chamber Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: PandaBreathCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_chamber_temperature"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Panda Breath",
            "manufacturer": "BIQU",
            "model": "Panda Breath",
            "sw_version": coordinator.data.get(KEY_FW_VERSION, "unknown"),
        }

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get(KEY_WAREHOUSE_TEMPER)
        if val is not None and val < 15:
            return None  # Device reports <15 as invalid
        return val


class PandaBreathFirmwareSensor(CoordinatorEntity, SensorEntity):
    """Sensor for firmware version."""

    _attr_has_entity_name = True
    _attr_name = "Firmware Version"
    _attr_icon = "mdi:chip"
    _attr_entity_registry_enabled_default = False  # Hidden by default

    def __init__(self, coordinator: PandaBreathCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_firmware_version"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Panda Breath",
            "manufacturer": "BIQU",
            "model": "Panda Breath",
        }

    @property
    def native_value(self) -> str | None:
        return self.coordinator.data.get(KEY_FW_VERSION)

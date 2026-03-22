"""Number platform for Panda Breath."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_SET_TEMP, KEY_FILTER_TEMP, KEY_HOTBED_TEMP
from .coordinator import PandaBreathCoordinator


@dataclass
class PandaBreathNumberDescription(NumberEntityDescription):
    settings_key: str = ""


NUMBER_DESCRIPTIONS: list[PandaBreathNumberDescription] = [
    PandaBreathNumberDescription(
        key="set_temp",
        name="Target Chamber Temperature",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=25,
        native_max_value=60,
        native_step=1,
        settings_key=KEY_SET_TEMP,
    ),
    PandaBreathNumberDescription(
        key="filtertemp",
        name="Filter Fan Activation Threshold",
        icon="mdi:fan",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=0,
        native_max_value=120,
        native_step=1,
        settings_key=KEY_FILTER_TEMP,
    ),
    PandaBreathNumberDescription(
        key="hotbedtemp",
        name="Heater Activation Threshold",
        icon="mdi:fire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_min_value=40,
        native_max_value=120,
        native_step=1,
        settings_key=KEY_HOTBED_TEMP,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PandaBreathCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PandaBreathNumber(coordinator, entry, desc)
        for desc in NUMBER_DESCRIPTIONS
    )


class PandaBreathNumber(CoordinatorEntity, NumberEntity):
    """Number entity for Panda Breath temperature settings."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PandaBreathCoordinator,
        entry: ConfigEntry,
        description: PandaBreathNumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._settings_key = description.settings_key
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Panda Breath",
            "manufacturer": "BIQU",
            "model": "Panda Breath",
        }

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self._settings_key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.send_settings({self._settings_key: int(value)})

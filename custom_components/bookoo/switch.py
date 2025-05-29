"""Switch platform for Bookoo integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BookooCoordinator
from .entity import BookooEntity


@dataclass
class BookooSwitchEntityDescription(SwitchEntityDescription):
    """Class describing Bookoo switch entities."""

    is_on_fn: callable = None
    set_fn: callable = None


SWITCH_TYPES: tuple[BookooSwitchEntityDescription, ...] = (
    BookooSwitchEntityDescription(
        key="flow_smoothing",
        name="Flow Smoothing",
        icon="mdi:chart-line",
        is_on_fn=lambda scale: scale.device_state.flow_rate_smoothing if scale.device_state else False,
        set_fn=lambda scale, value: scale.set_flow_smoothing(value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bookoo switch entities."""
    coordinator: BookooCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        BookooSwitch(coordinator, description) for description in SWITCH_TYPES
    ]

    async_add_entities(entities, True)


class BookooSwitch(BookooEntity, SwitchEntity):
    """Representation of a Bookoo switch entity."""

    entity_description: BookooSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if not self._scale.device_state:
            return None
        return self.entity_description.is_on_fn(self._scale)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        await self.entity_description.set_fn(self._scale, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        await self.entity_description.set_fn(self._scale, False)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self, *args, **kwargs) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

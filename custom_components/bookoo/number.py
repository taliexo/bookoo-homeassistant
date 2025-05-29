"""Number platform for Bookoo integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BookooCoordinator
from .entity import BookooEntity


@dataclass
class BookooNumberEntityDescription(NumberEntityDescription):
    """Class describing Bookoo number entities."""

    min_value: float = 0
    max_value: float = 100
    step: float = 1
    mode: str = NumberMode.AUTO
    set_fn: callable = None
    value_fn: callable = None


NUMBER_TYPES: tuple[BookooNumberEntityDescription, ...] = (
    BookooNumberEntityDescription(
        key="beep_level",
        name="Beep Level",
        icon="mdi:volume-high",
        min_value=0,
        max_value=5,
        step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda scale: scale.device_state.buzzer_gear if scale.device_state else 0,
        set_fn=lambda scale, value: scale.set_beep_level(int(value)),
    ),
    BookooNumberEntityDescription(
        key="auto_off",
        name="Auto-off",
        icon="mdi:timer-outline",
        min_value=1,
        max_value=30,
        step=1,
        mode=NumberMode.BOX,
        value_fn=lambda scale: scale.device_state.standby_time if scale.device_state else 5,
        set_fn=lambda scale, value: scale.set_auto_off(int(value)),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bookoo number entities."""
    coordinator: BookooCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        BookooNumber(coordinator, description) for description in NUMBER_TYPES
    ]

    async_add_entities(entities, True)


class BookooNumber(BookooEntity, NumberEntity):
    """Representation of a Bookoo number entity."""

    entity_description: BookooNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if not self._scale.device_state:
            return None
        return self.entity_description.value_fn(self._scale)

    @property
    def mode(self) -> NumberMode:
        """Return the mode of the entity."""
        return self.entity_description.mode

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return self.entity_description.min_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return self.entity_description.max_value

    @property
    def native_step(self) -> float | None:
        """Return the increment/decrement step."""
        return self.entity_description.step

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.entity_description.set_fn(self._scale, value)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self, *args, **kwargs) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()

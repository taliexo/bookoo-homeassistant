"""Sensor platform for Bookoo."""

from collections.abc import Callable  # noqa: I001
from dataclasses import dataclass, field
from typing import Callable

from aiobookoo.bookooscale import BookooDeviceState, BookooScale
from aiobookoo.const import UnitMass as BookooUnitOfMass
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorExtraStoredData,
    SensorStateClass,
)
from homeassistant.const import (
    MASS_GRAMS,
    PERCENTAGE,
    TIME_SECONDS,
    TIME_MINUTES,
    UnitOfMass,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BookooConfigEntry
from .entity import BookooEntity

# Coordinator is used to centralize the data updates
PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class BookooSensorEntityDescription(SensorEntityDescription):
    """Description for Bookoo sensor entities."""

    value_fn: Callable[[BookooScale], int | float | str | None] = field(default=lambda _: None)
    attributes: dict[str, Callable[[BookooScale], dict]] = field(default_factory=dict)
    native_unit_of_measurement: str | None = None
    device_class: str | None = None
    state_class: str | None = None


@dataclass(frozen=True)
class BookooDynamicUnitSensorEntityDescription(BookooSensorEntityDescription):
    """Description for Bookoo sensor entities with dynamic units."""

    unit_fn: Callable[[BookooDeviceState], str] | None = None


SENSOR_TYPES: tuple[BookooSensorEntityDescription, ...] = (
    BookooSensorEntityDescription(
        key="weight",
        name="Weight",
        icon="mdi:scale",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=MASS_GRAMS,
        value_fn=lambda scale: scale.weight,
        attributes={
            "unit": lambda scale: scale.device_state.unit if scale.device_state else None,
        },
    ),
    BookooSensorEntityDescription(
        key="flow_rate",
        name="Flow Rate",
        icon="mdi:water-percent",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=f"{MASS_GRAMS}/{UnitOfTime.SECONDS}",
        value_fn=lambda scale: scale.flow_rate,
    ),
    BookooSensorEntityDescription(
        key="battery",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False,
        value_fn=lambda scale: scale.device_state.battery_level if scale.device_state else None,
    ),
    BookooSensorEntityDescription(
        key="timer",
        name="Timer",
        icon="mdi:timer-outline",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda scale: scale.timer,
    ),
    # New sensors
    BookooSensorEntityDescription(
        key="standby_time",
        name="Standby Time",
        icon="mdi:timer-sand",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda scale: scale.device_state.standby_time if scale.device_state else None,
    ),
    BookooSensorEntityDescription(
        key="buzzer_gear",
        name="Beep Level",
        icon="mdi:volume-high",
        value_fn=lambda scale: scale.device_state.buzzer_gear if scale.device_state else None,
        attributes={
            "min_level": 0,
            "max_level": 5,
        },
    ),
    BookooSensorEntityDescription(
        key="flow_smoothing_status",
        name="Flow Smoothing Status",
        icon="mdi:chart-line",
        value_fn=lambda scale: "ON" if scale.device_state and scale.device_state.flow_rate_smoothing else "OFF" if scale.device_state else None,
    ),
    BookooSensorEntityDescription(
        key="unit",
        name="Unit",
        icon="mdi:scale-balance",
        value_fn=lambda scale: scale.device_state.unit if scale.device_state else None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""

    coordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        BookooSensor(coordinator, entity_description) for entity_description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class BookooSensor(BookooEntity, SensorEntity):
    """Representation of a Bookoo sensor."""
    def native_value(self) -> int | float | None:
        """Return the state of the entity."""
        return self.entity_description.value_fn(self._scale)


class BookooRestoreSensor(BookooEntity, RestoreSensor):
    """Representation of an Bookoo sensor with restore capabilities."""

    entity_description: BookooSensorEntityDescription
    _restored_data: SensorExtraStoredData | None = None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()

        self._restored_data = await self.async_get_last_sensor_data()
        if self._restored_data is not None:
            self._attr_native_value = self._restored_data.native_value
            self._attr_native_unit_of_measurement = (
                self._restored_data.native_unit_of_measurement
            )

        if self._scale.device_state is not None:
            self._attr_native_value = self.entity_description.value_fn(self._scale)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self._scale.device_state is not None:
            self._attr_native_value = self.entity_description.value_fn(self._scale)
        self._async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available or self._restored_data is not None

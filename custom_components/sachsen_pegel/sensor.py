from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfVolumeFlowRate
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import PegelConfigEntry
from .const import DOMAIN
from .coordinator import PegelCoordinator


@dataclass(frozen=True, kw_only=True)
class PegelSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def _timestamp(data: dict[str, Any]) -> datetime | None:
    raw = data.get("timestamp")
    return dt_util.parse_datetime(raw) if raw else None


_ALARM_LEVEL_PATTERN = re.compile(r"Alarmstufe\s*(\d)$")

# "Kein Hochwassermeldepegel" bedeutet, dass der Pegel nicht für amtliche
# Hochwassermeldungen genutzt wird; dafür gibt es keine Alarmstufe, daher None.
_NO_ALERT_TEXTS = {"Niedrigwasser", "Kein Hochwasser"}


def _alarm_level(data: dict[str, Any]) -> int | None:
    text = data.get("flood_alert_level")
    if not isinstance(text, str):
        return None
    text = text.strip()
    if text in _NO_ALERT_TEXTS:
        return 0
    match = _ALARM_LEVEL_PATTERN.match(text)
    return int(match.group(1)) if match else None


def _alarm_thresholds_attributes(data: dict[str, Any]) -> dict[str, Any]:
    thresholds = data.get("alarm_thresholds")
    if not isinstance(thresholds, list):
        return {}
    attributes = {}
    for threshold in thresholds:
        level = threshold.get("level")
        water_level_cm = threshold.get("water_level_cm")
        if isinstance(level, int) and isinstance(water_level_cm, int):
            attributes[f"alarm_threshold_{level}_cm"] = water_level_cm
    return attributes


SENSORS: tuple[PegelSensorDescription, ...] = (
    PegelSensorDescription(
        key="water_level",
        translation_key="water_level",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("water_level_cm"),
    ),
    PegelSensorDescription(
        key="flow",
        translation_key="flow",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: d.get("flow_m3s"),
    ),
    PegelSensorDescription(
        key="flood_alert_level",
        translation_key="flood_alert_level",
        value_fn=lambda d: d.get("flood_alert_level"),
    ),
    PegelSensorDescription(
        key="alarm_level",
        translation_key="alarm_level",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_alarm_level,
        attributes_fn=_alarm_thresholds_attributes,
    ),
    PegelSensorDescription(
        key="last_measurement",
        translation_key="last_measurement",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_timestamp,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PegelConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(PegelSensor(coordinator, desc) for desc in SENSORS)


class PegelSensor(CoordinatorEntity[PegelCoordinator], SensorEntity):
    _attr_has_entity_name = True
    entity_description: PegelSensorDescription

    def __init__(
        self, coordinator: PegelCoordinator, description: PegelSensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.station_id)},
            name=coordinator.data.get("station_title") or coordinator.station_id,
            manufacturer="Freistaat Sachsen (HWIMS)",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator.data)

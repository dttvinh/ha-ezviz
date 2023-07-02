"""Support for EZVIZ sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import EzvizDataUpdateCoordinator
from .entity import EzvizEntity

PARALLEL_UPDATES = 1

SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    "battery_level": SensorEntityDescription(
        key="battery_level",
        name="Battery",
        translation_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    "last_alarm_time": SensorEntityDescription(
        key="last_alarm_time",
        name="Last alarm time",
        translation_key="last_alarm_time",
    ),
    "Seconds_Last_Trigger": SensorEntityDescription(
        key="Seconds_Last_Trigger",
        name="Seconds since last alarm",
        translation_key="seconds_last_trigger",
        entity_registry_enabled_default=False,
    ),
    "last_alarm_pic": SensorEntityDescription(
        key="last_alarm_pic",
        name="Last alarm picture url",
        translation_key="last_alarm_pic",
    ),
    "supported_channels": SensorEntityDescription(
        key="supported_channels",
        name="Supported channels",
        translation_key="supported_channels",
    ),
    "local_ip": SensorEntityDescription(
        key="local_ip",
        name="Local IP",
        translation_key="local_ip",
    ),
    "wan_ip": SensorEntityDescription(
        key="wan_ip",
        name="WAN IP",
        translation_key="wan_ip",
    ),
    "PIR_Status": SensorEntityDescription(
        key="PIR_Status",
        name="PIR Status",
        translation_key="pir_status",
    ),
    "last_alarm_type_code": SensorEntityDescription(
        key="last_alarm_type_code",
        name="Last alarm type code",
        translation_key="last_alarm_type_code",
    ),
    "last_alarm_type_name": SensorEntityDescription(
        key="last_alarm_type_name",
        name="Last alarm type name",
        translation_key="last_alarm_type_name",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up EZVIZ sensors based on a config entry."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    async_add_entities(
        [
            EzvizSensor(coordinator, camera, sensor)
            for camera in coordinator.data
            for sensor, value in coordinator.data[camera].items()
            if sensor in SENSOR_TYPES
            if value is not None
        ]
    )


class EzvizSensor(EzvizEntity, SensorEntity):
    """Representation of a EZVIZ sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: EzvizDataUpdateCoordinator, serial: str, sensor: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial)
        self._sensor_name = sensor
        self._attr_unique_id = f"{serial}_{self._camera_name}.{sensor}"
        self.entity_description = SENSOR_TYPES[sensor]

    @property
    def native_value(self) -> int | str:
        """Return the state of the sensor."""
        return self.data[self._sensor_name]

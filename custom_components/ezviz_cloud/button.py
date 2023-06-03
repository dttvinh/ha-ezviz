"""Support for EZVIZ button controls."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pyezviz import EzvizClient
from pyezviz.constants import SupportExt
from pyezviz.exceptions import HTTPError, PyEzvizError

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_COORDINATOR, DOMAIN
from .coordinator import EzvizDataUpdateCoordinator
from .entity import EzvizEntity

PARALLEL_UPDATES = 1


@dataclass
class EzvizButtonEntityDescriptionMixin:
    """Mixin values for EZVIZ button entities."""

    method: Callable[[EzvizClient, str, str], Any]
    supported_ext: str


@dataclass
class EzvizButtonEntityDescription(
    ButtonEntityDescription, EzvizButtonEntityDescriptionMixin
):
    """Describe a EZVIZ Button."""


BUTTON_ENTITIES = (
    EzvizButtonEntityDescription(
        key="ptz_up",
        name="PTZ up",
        icon="mdi:pan",
        method=lambda pyezviz_client, serial, run: pyezviz_client.ptz_control(
            "UP", serial, run
        ),
        supported_ext=str(SupportExt.SupportPtz.value),
    ),
    EzvizButtonEntityDescription(
        key="ptz_down",
        name="PTZ down",
        icon="mdi:pan",
        method=lambda pyezviz_client, serial, run: pyezviz_client.ptz_control(
            "DOWN", serial, run
        ),
        supported_ext=str(SupportExt.SupportPtz.value),
    ),
    EzvizButtonEntityDescription(
        key="ptz_left",
        name="PTZ left",
        icon="mdi:pan",
        method=lambda pyezviz_client, serial, run: pyezviz_client.ptz_control(
            "LEFT", serial, run
        ),
        supported_ext=str(SupportExt.SupportPtz.value),
    ),
    EzvizButtonEntityDescription(
        key="ptz_right",
        name="PTZ right",
        icon="mdi:pan",
        method=lambda pyezviz_client, serial, run: pyezviz_client.ptz_control(
            "RIGHT", serial, run
        ),
        supported_ext=str(SupportExt.SupportPtz.value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up EZVIZ button based on a config entry."""
    coordinator: EzvizDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    # Add button entities if supportExt value indicates PTZ capbility.
    # Could be missing or "0" for unsupported.
    # If present with value of "1" then add button entity.

    async_add_entities(
        EzvizButtonEntity(coordinator, camera, entity_description)
        for camera in coordinator.data
        for capibility, value in coordinator.data[camera]["supportExt"].items()
        for entity_description in BUTTON_ENTITIES
        if capibility == entity_description.supported_ext
        if value == "1"
    )


class EzvizButtonEntity(EzvizEntity, ButtonEntity):
    """Representation of a EZVIZ button entity."""

    entity_description: EzvizButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: EzvizDataUpdateCoordinator,
        serial: str,
        description: EzvizButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_{description.name}"
        self.entity_description = description

    def press(self) -> None:
        """Execute the button action."""
        try:
            self.entity_description.method(
                self.coordinator.ezviz_client, self._serial, "START"
            )
            self.entity_description.method(
                self.coordinator.ezviz_client, self._serial, "STOP"
            )
        except (HTTPError, PyEzvizError) as err:
            raise HomeAssistantError(
                f"Cannot perform PTZ action on {self.name}"
            ) from err

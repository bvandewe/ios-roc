import datetime
import logging
from dataclasses import dataclass

from neuroglia.eventing.cloud_events.decorators import cloudevent
from neuroglia.integration.models import IntegrationEvent

from integration.models.collected_outputs_per_device_dto import (
    DeviceOutputsCollectionResponseDto,
)
from integration.models.command_line_dto import CommandLineDto
from integration.models.device_dto import DeviceDto

log = logging.getLogger(__name__)


@cloudevent("cli-collection.failed.v1")
@dataclass
class CliCollectionFailedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the collection request."""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""

    error: str
    """The error message."""


@cloudevent("cli-collection.requested.v1")
@dataclass
class CliCollectionRequestedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the collection request."""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""

    command_lines: list[CommandLineDto]
    """The command_line to be collected."""

    device: DeviceDto
    """The device to collect the command_line from."""


@cloudevent("cli-collection.completed.v1")
@dataclass
class CliCollectionCompletedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the collection request."""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""

    result: DeviceOutputsCollectionResponseDto
    """The collected output."""

import datetime
import logging
from dataclasses import dataclass
from typing import Optional

from neuroglia.eventing.cloud_events.decorators import cloudevent
from neuroglia.integration.models import IntegrationEvent

log = logging.getLogger(__name__)


@cloudevent("dependencies-health-check.requested.v1")
@dataclass
class HealthCheckRequestedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the Event"""

    health_check_id: str
    """The unique id of HealthCheck request"""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""


@cloudevent("dependencies-health-check.completed.v1")
@dataclass
class HealthCheckCompletedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the Event"""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""

    all: bool
    """Whether ALL dependencies are available."""

    identity_provider: bool
    """Whether the IDP is available."""

    events_gateway: bool
    """Whether the event gateway is available."""


@cloudevent("dependencies-health-check.failed.v1")
@dataclass
class HealthCheckFailedIntegrationEventV1(IntegrationEvent[str]):
    aggregate_id: str
    """The unique id of the Event"""

    created_at: datetime.datetime
    """The timestamp when the event was emitted."""

    detail: Optional[str] = None
    """Details of the Exception that triggered the Initialization failure."""

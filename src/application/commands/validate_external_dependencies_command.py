import datetime
import logging
import uuid
from typing import Any

import httpx
from neuroglia.core import OperationResult
from neuroglia.eventing.cloud_events.infrastructure import CloudEventBus
from neuroglia.eventing.cloud_events.infrastructure.cloud_event_publisher import (
    CloudEventPublishingOptions,
)
from neuroglia.mapping import Mapper
from neuroglia.mediation import Command, CommandHandler, Mediator

from api.services.oauth import get_public_key
from application import ApplicationException
from application.commands.command_handler_base import CommandHandlerBase
from application.events.integration import (
    HealthCheckCompletedIntegrationEventV1,
    HealthCheckFailedIntegrationEventV1,
    HealthCheckRequestedIntegrationEventV1,
)
from application.settings import IosRocSettings
from integration import IntegrationException
from integration.models import ExternalDependenciesHealthCheckResultDto

log = logging.getLogger(__name__)


class ValidateExternalDependenciesCommand(Command):
    pass


class ValidateExternalDependenciesCommandHandler(CommandHandlerBase, CommandHandler[ValidateExternalDependenciesCommand, OperationResult[Any]]):
    """Represents the service used to handle ValidateExternalDependenciesCommand"""

    def __init__(self, mediator: Mediator, mapper: Mapper, cloud_event_bus: CloudEventBus, cloud_event_publishing_options: CloudEventPublishingOptions, app_settings: IosRocSettings):
        super().__init__(mediator, mapper, cloud_event_bus, cloud_event_publishing_options, app_settings)

    async def handle_async(self, command: ValidateExternalDependenciesCommand) -> OperationResult[ExternalDependenciesHealthCheckResultDto]:
        """Validates whether the external dependencies are reachable and responsive."""
        try:
            id = str(uuid.uuid4()).replace("-", "")
            try:
                await self.publish_cloud_event_async(HealthCheckRequestedIntegrationEventV1(aggregate_id=id, created_at=datetime.datetime.now(), health_check_id=id))
            except IntegrationException as e:
                log.warning(f"The Event Gateway is down: {e}")

            identity_provider = None
            identity_provider = await get_public_key(self.app_settings.jwt_authority)

            # To test the event gateway, we really need to make an HTTP call to it,
            # just using await self.publish_cloud_event_async will always return True
            # if the event is valid (as the CloudEventPublisher will try to "silently" send
            # the event {retry} times and "just" log ERROR if any)!
            events_gateway = None
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self.app_settings.cloud_event_sink)
                    if response.is_success or response.is_error:
                        events_gateway = True
            except httpx.ConnectError as e:
                log.error(f"Error connecting to events gateway: {e}")

            dependencies_health = {
                "identity_provider": identity_provider is not None,
                "events_gateway": events_gateway is not None,
            }
            dependencies_health["all"] = all(dependencies_health.values())
            try:
                await self.publish_cloud_event_async(HealthCheckCompletedIntegrationEventV1(aggregate_id=id, created_at=datetime.datetime.now(), **dependencies_health))
            except IntegrationException as e:
                log.warning(f"The Event Gateway is down: {e}")

            return self.ok(ExternalDependenciesHealthCheckResultDto(**dependencies_health))

        except (ApplicationException, IntegrationException) as e:
            try:
                await self.publish_cloud_event_async(HealthCheckFailedIntegrationEventV1(aggregate_id=id, created_at=datetime.datetime.now(), detail=str(e)))
            except IntegrationException as e2:
                log.warning(f"The Event Gateway is down: {e2}")
            log.error(f"Failed to handle ValidateExternalDependenciesCommand: {e}")
            return self.bad_request(f"Failed to handle ValidateExternalDependenciesCommand: {e}")

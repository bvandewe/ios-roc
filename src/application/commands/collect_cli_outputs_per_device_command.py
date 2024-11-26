import datetime
import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from neuroglia.core import OperationResult
from neuroglia.eventing.cloud_events.infrastructure import CloudEventBus
from neuroglia.eventing.cloud_events.infrastructure.cloud_event_publisher import (
    CloudEventPublishingOptions,
)
from neuroglia.mapping.mapper import Mapper
from neuroglia.mediation import Command, CommandHandler, Mediator

from application import ApplicationException
from application.commands.command_handler_base import CommandHandlerBase
from application.events.integration import (
    CliCollectionCompletedIntegrationEventV1,
    CliCollectionRequestedIntegrationEventV1,
)
from application.events.integration.output_collection_events import (
    CliCollectionFailedIntegrationEventV1,
)
from application.settings import IosRocSettings
from domain.exceptions import DomainException
from domain.models import CommandLine, Device
from integration import IntegrationException
from integration.models import (
    CiscoIosCliAuthenticationPropertiesDto,
    CommandLineDto,
    CommandOutputDto,
    DeviceDto,
    DeviceInterfaceDto,
    DeviceOutputsCollectionResponseDto,
    InterfaceAuthenticationDto,
)
from integration.services.cisco_command_line_collector_base import (
    CiscoCommandLineCollectorBase,
    CiscoCommandLineCollectorException,
)

log = logging.getLogger(__name__)


@dataclass
class CollectCliOutputsPerDeviceCommand(Command):
    pod_id: str
    """The unique identifier of the Pod that the Device belongs to."""

    device: Device
    """The Device to collect the CommandLines from."""

    commands: list[CommandLine]
    """The CommandLines to collect from the Device."""

    use_console: Optional[bool] = True
    """Uses the console interface if True, otherwise uses the first interface in the Device's list of interfaces."""


class CollectCliOutputsPerDeviceCommandHandler(CommandHandlerBase, CommandHandler[CollectCliOutputsPerDeviceCommand, OperationResult[DeviceOutputsCollectionResponseDto]]):
    """Represents the service used to handle CollectCliOutputsPerDeviceCommand"""

    collector: CiscoCommandLineCollectorBase
    """The service used to collect CommandLines from a Device."""

    def __init__(self, mediator: Mediator, mapper: Mapper, cloud_event_bus: CloudEventBus, cloud_event_publishing_options: CloudEventPublishingOptions, app_settings: IosRocSettings, collector: CiscoCommandLineCollectorBase):
        super().__init__(mediator, mapper, cloud_event_bus, cloud_event_publishing_options, app_settings)
        self.collector = collector

    async def handle_async(self, command: CollectCliOutputsPerDeviceCommand) -> OperationResult[DeviceOutputsCollectionResponseDto]:
        """Collect a sequence of CLIs from a single Device."""
        try:
            reqid = str(uuid.uuid4()).replace("-", "")
            log.info(f"Handling CollectCliOutputsPerDeviceCommand(reqid: {reqid}, CLIs: '{[cli.line for cli in command.commands]}' from {command.device.label})")

            # device_dto = self.mapper.map(command.device, DeviceDto)  # mapper fails with fancy types that include Optional fields...
            device_dto = DeviceDto(
                label=command.device.label,
                hostname=command.device.hostname,
                interfaces=[
                    DeviceInterfaceDto(
                        name=interface.name,
                        protocol=interface.protocol,
                        ip=interface.ip,
                        port=interface.port,
                        authentication=InterfaceAuthenticationDto(
                            scheme=interface.authentication.scheme,
                            properties=CiscoIosCliAuthenticationPropertiesDto(
                                username=interface.authentication.properties.username,
                                password=interface.authentication.properties.password,
                                secret=interface.authentication.properties.secret,
                            ),
                        ),
                    )
                    for interface in command.device.interfaces
                ],
            )

            await self.publish_cloud_event_async(
                CliCollectionRequestedIntegrationEventV1(
                    aggregate_id=command.device.id,
                    created_at=datetime.datetime.now(),
                    command_lines=[CommandLineDto(line=cli.line, timeout=cli.timeout) for cli in command.commands],
                    device=device_dto,
                )
            )

            # Find the console interface on the device
            if command.use_console:
                if console_interface := command.device.get_interface_by_name("console"):
                    interface = console_interface
            else:
                log.warning(f"Console interface not found on device {command.device.label}")
                interface = command.device.interfaces[0]

            # Collect the outputs
            commands_output = await self.collector.collect_async(command.commands, command.device, interface.name)

            # Publish the results
            if len(commands_output):
                results_dto = []
                for command_output in commands_output:
                    succeeded = command_output.error is None
                    result_dto = CommandOutputDto(command=command_output.command.line, succeeded=succeeded, error=command_output.error, duration=command_output.duration, output=command_output.output)
                    results_dto.append(result_dto)

                response = DeviceOutputsCollectionResponseDto(results=results_dto)

                await self.publish_cloud_event_async(
                    CliCollectionCompletedIntegrationEventV1(aggregate_id=reqid, created_at=datetime.datetime.now(), result=response),
                )
                return self.ok(response)

            return self.bad_request("No outputs were collected.")

        except (ApplicationException, DomainException, IntegrationException, CiscoCommandLineCollectorException) as e:
            err = f"Failed to handle CollectCliOutputsPerDeviceCommand: reqid: {reqid}, {e}"
            log.error(err)
            await self.publish_cloud_event_async(CliCollectionFailedIntegrationEventV1(aggregate_id=reqid, created_at=datetime.datetime.now(), error=err))
            return self.bad_request(err)

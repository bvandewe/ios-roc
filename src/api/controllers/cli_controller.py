import logging
from ipaddress import IPv4Address
from typing import Any

from classy_fastapi.decorators import post
from fastapi import Depends
from neuroglia.dependency_injection import ServiceProviderBase
from neuroglia.mapping.mapper import Mapper
from neuroglia.mediation.mediator import Mediator
from neuroglia.mvc.controller_base import ControllerBase

from api.controllers.oauth2_scheme import validate_token
from application.commands import CollectCliOutputsPerDeviceCommand
from domain.models import (
    CiscoIosCliAuthenticationProperties,
    CommandLine,
    Device,
    DeviceInterface,
    InterfaceAuthentication,
)
from integration.enums import InterfaceAuthenticationScheme
from integration.models import (
    CollectCliOutputsPerDeviceCommandDto,
    DeviceOutputsCollectionResponseDto,
)

log = logging.getLogger(__name__)


class CliController(ControllerBase):
    def __init__(self, service_provider: ServiceProviderBase, mapper: Mapper, mediator: Mediator):
        ControllerBase.__init__(self, service_provider, mapper, mediator)

    @post("/collect", response_model=DeviceOutputsCollectionResponseDto, status_code=201, responses=ControllerBase.error_responses)
    async def from_device(self, command_dto: CollectCliOutputsPerDeviceCommandDto, token: str = Depends(validate_token)) -> Any:
        """Collect a sequence of CommandLines from a Device.

        - The first interface is used if `use_console` is either `False` or `None`.
        - Each CommandLine is executed sequentially, the output is collected if the command succeeds within its defined timeout.
        - Failed CommandLine are reported individually in the response.

        """
        clis = [CommandLine(line=cli.line, timeout=cli.timeout or 5) for cli in command_dto.commands]
        device = Device(
            label=command_dto.device.label or "",
            hostname=command_dto.device.hostname or command_dto.device.label,
            interfaces=[
                DeviceInterface(
                    name=interface.name or "console",
                    protocol=interface.protocol or "telnet",
                    ip=IPv4Address(interface.ip),
                    port=interface.port or 23,
                    authentication=InterfaceAuthentication(
                        scheme=InterfaceAuthenticationScheme(interface.authentication.scheme),
                        properties=CiscoIosCliAuthenticationProperties(
                            username=interface.authentication.properties.username,
                            password=interface.authentication.properties.password,
                            secret=interface.authentication.properties.secret,
                        ),
                    ),
                )
                for interface in command_dto.device.interfaces
            ],
        )
        return self.process(await self.mediator.execute_async(CollectCliOutputsPerDeviceCommand(pod_id=command_dto.pod_id, commands=clis, device=device)))

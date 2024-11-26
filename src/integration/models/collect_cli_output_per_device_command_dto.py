from typing import Optional

from pydantic import BaseModel

from integration.models.command_line_dto import CommandLineDto
from integration.models.device_dto import DeviceDto


class CollectCliOutputsPerDeviceCommandDto(BaseModel):
    pod_id: str
    """The unique identifier of the Pod to collect the Commands from."""

    device: DeviceDto
    """The Device to collect the Commands from."""

    commands: list[CommandLineDto] = [CommandLineDto(line="sh ver"), CommandLineDto(line="sh ip int brief")]
    """The list of CommandLines to collect from the Device."""

    use_console: Optional[bool] = True
    """Uses the console interface if True, otherwise uses the first interface in the Device's list of interfaces."""

from pydantic import BaseModel

from .command_output_dto import CommandOutputDto


class DeviceOutputsCollectionResponseDto(BaseModel):
    results: list[CommandOutputDto]
    """The list of outputs collected from the device."""

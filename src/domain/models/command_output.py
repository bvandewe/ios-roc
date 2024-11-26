import datetime
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from neuroglia.data.abstractions import Entity
from neuroglia.mapping.mapper import map_to

from domain.models.command_line import CommandLine
from domain.models.device import Device
from integration.models.command_output_dto import CommandOutputDto


@map_to(CommandOutputDto)
@dataclass
class CommandOutput(Entity[str]):
    id: str
    """The unique identifier of the output record in the Cache DB. (Required by Entity)"""

    aggregate_id: str
    """The unique identifier of the output."""

    created_at: datetime.datetime
    """The date and time the output was created."""

    last_modified: datetime.datetime
    """The date and time the output was last modified."""

    duration: datetime.timedelta
    """The delay between the command being sent and the output being collected."""

    command: CommandLine
    """The command line that was executed."""

    device: Device
    """The device that the command was executed on."""

    _output: str
    """The output text of the command line."""

    error: Optional[str] = None
    """The error message if the command line failed."""

    def __init__(self, line: CommandLine, device: Device):
        self.created_at = datetime.datetime.now(datetime.UTC)
        self.last_modified = self.created_at
        self.duration = datetime.timedelta(milliseconds=0)
        self.aggregate_id = str(uuid.uuid4()).replace("-", "")
        self.id = f"output.{device.id}.{self.created_at.isoformat()}"
        self.command = line
        self.device = device
        self._output = ""
        self.error = None

    def __str__(self):
        return f"CommandOutput: {self.id}, {self.aggregate_id}, {self.created_at}, {self.last_modified}, {self.command}, {self.output}"

    @property
    def output(self) -> str:
        """The output text of the command line."""
        return self._output

    @output.setter
    def output(self, text: str | List[Any] | Dict[str, Any]):
        """Adds output text to the existing output text."""
        if isinstance(text, list):
            text = "\n".join(text)
        if isinstance(text, dict):
            text = "\n".join([f"{k}: {v}" for k, v in text.items()])
        self._output += text
        self.last_modified = datetime.datetime.now(datetime.UTC)
        self.duration = self.last_modified - self.created_at

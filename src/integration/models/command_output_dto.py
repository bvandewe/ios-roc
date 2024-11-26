import datetime
from typing import Optional

from pydantic import BaseModel


class CommandOutputDto(BaseModel):
    command: str
    """The command line that was executed."""

    succeeded: bool
    """Whether the command line was executed successfully"""

    error: Optional[str] = None
    """The error message if the command line failed."""

    duration: datetime.timedelta = datetime.timedelta(milliseconds=0)
    """The collection delay of the output."""

    output: str
    """The output text of the command line."""

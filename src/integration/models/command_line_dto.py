from typing import Optional

from pydantic import BaseModel


class CommandLineDto(BaseModel):
    line: str = "sh ver"
    """The command line to be executed."""

    timeout: Optional[int] = 5
    """The timeout in seconds for the command line."""

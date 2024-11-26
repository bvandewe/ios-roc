from dataclasses import dataclass


@dataclass
class CommandLine:
    line: str
    """The command line to be executed."""

    timeout: int = 15
    """The timeout in seconds for the command line."""

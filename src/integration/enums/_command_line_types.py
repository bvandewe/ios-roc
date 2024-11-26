from integration.enums.custom_enum import CustomEnum


class CommandLineType(CustomEnum):
    """Represents the type of command line"""

    DIS = "disable"
    """CommandLine available in unpriviledge mode"""

    ENA = "enable"
    """CommandLine available in priviledge mode"""

    CFG = "configure"
    """CommandLine available in configuration mode"""

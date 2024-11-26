from enum import Enum


class CollectorType(str, Enum):
    """Represents the type of device"""

    IOS = "cisco_ios_telnet"
    """CommandLine available in unpriviledge mode"""

    # IOSXR = "cisco_xr_telnet"

    # NXOS = "cisco_nxos"

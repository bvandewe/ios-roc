from ipaddress import IPv4Address
from typing import Optional

from pydantic import BaseModel, SecretStr

from integration.enums.interface_authentication_schemes import (
    InterfaceAuthenticationScheme,
)


class InterfaceAuthenticationPropertiesDto(BaseModel):
    username: Optional[str]
    password: Optional[SecretStr]


class CiscoIosCliAuthenticationPropertiesDto(BaseModel):
    username: Optional[str]
    password: Optional[SecretStr]
    secret: Optional[SecretStr]


class InterfaceAuthenticationDto(BaseModel):
    scheme: InterfaceAuthenticationScheme = InterfaceAuthenticationScheme.basic
    properties: CiscoIosCliAuthenticationPropertiesDto = CiscoIosCliAuthenticationPropertiesDto(username="neuro", password=SecretStr("Cisco123"), secret=SecretStr("Cisco123"))


class DeviceInterfaceDto(BaseModel):
    name: str = "console"

    protocol: str = "telnet"

    ip: IPv4Address = IPv4Address("150.101.20.48")

    port: int = 3001

    authentication: InterfaceAuthenticationDto = InterfaceAuthenticationDto()

    configuration: Optional[dict[str, str]] = {"default_timeout": "15"}


class DeviceDto(BaseModel):
    label: str
    """The label of the device."""

    hostname: Optional[str] = None
    """The hostname of the device. Defaults to the label if not provided."""

    interfaces: list[DeviceInterfaceDto] = [DeviceInterfaceDto()]
    """The access information for the device."""

    # collector: CollectorType = CollectorType.IOS
    # """The collector of the device. (Should always be IOS for this IOS ROC!)"""

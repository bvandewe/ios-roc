import datetime
import logging
import uuid
from dataclasses import dataclass, field
from ipaddress import IPv4Address
from typing import Optional

from neuroglia.data.abstractions import Entity
from neuroglia.mapping.mapper import map_from, map_to
from pydantic import SecretStr

from domain.exceptions import DomainException
from integration.enums import CollectorType, InterfaceAuthenticationScheme
from integration.models import (
    CiscoIosCliAuthenticationPropertiesDto,
    DeviceDto,
    DeviceInterfaceDto,
    InterfaceAuthenticationDto,
    InterfaceAuthenticationPropertiesDto,
)

log = logging.getLogger(__name__)


@map_to(InterfaceAuthenticationPropertiesDto)
@map_from(InterfaceAuthenticationPropertiesDto)
@dataclass
class InterfaceAuthenticationProperties:
    username: Optional[str]
    password: Optional[SecretStr]


@map_to(CiscoIosCliAuthenticationPropertiesDto)
@map_from(CiscoIosCliAuthenticationPropertiesDto)
@dataclass
class CiscoIosCliAuthenticationProperties:
    username: Optional[str] = "neuro"
    password: Optional[SecretStr] = SecretStr("Cisco123")
    secret: Optional[SecretStr] = SecretStr("Cisco123")


def default_properties():
    return CiscoIosCliAuthenticationProperties()


@map_to(InterfaceAuthenticationDto)
@map_from(InterfaceAuthenticationDto)
@dataclass
class InterfaceAuthentication:
    scheme: InterfaceAuthenticationScheme = InterfaceAuthenticationScheme.basic
    properties: CiscoIosCliAuthenticationProperties = field(default_factory=default_properties)


def default_authentication():
    return InterfaceAuthentication()


def default_configuration():
    return {"default_timeout": "15"}


@map_to(DeviceInterfaceDto)
@map_from(DeviceInterfaceDto)
@dataclass
class DeviceInterface:
    name: str = "console"
    protocol: str = "telnet"
    ip: IPv4Address = IPv4Address("150.101.20.48")
    port: int = 3001
    authentication: InterfaceAuthentication = field(default_factory=default_authentication)
    configuration: Optional[dict[str, str]] = field(default_factory=default_configuration)


@map_to(DeviceDto)
@map_from(DeviceDto)
@dataclass
class Device(Entity[str]):
    id: str
    """The unique identifier of the device in the Cache DB. (Required by Entity)"""

    aggregate_id: str
    """The unique identifier of the device."""

    created_at: datetime.datetime
    """The date and time the output was created."""

    last_modified: datetime.datetime
    """The date and time the output was last modified."""

    label: str
    """The label of the device."""

    hostname: str
    """The hostname of the device."""

    interfaces: list[DeviceInterface] = field(default_factory=list)
    """The access information for the device."""

    collector: CollectorType = CollectorType.IOS
    """The collector of the device. (Should always be IOS for this IOS ROC!)"""

    def __init__(
        self,
        label: str,
        interfaces: list[DeviceInterface],
        hostname: Optional[str] = None,
        collector_key: Optional[str] = "IOS",
    ):
        self.aggregate_id = str(uuid.uuid4()).replace("-", "")
        self.created_at = datetime.datetime.now()
        self.last_modified = self.created_at
        if " " in label:
            label = label.replace(" ", "_")
        self.label = label
        if hostname is None:
            hostname = label
        elif " " in hostname:
            hostname = hostname.replace(" ", "_")
        self.hostname = hostname
        # for c in CollectorType.__members__.values():
        #     if c.name == collector_key:
        #         self.collector = c
        #         break
        self.collector = CollectorType[collector_key or "IOS"]
        if not self.collector:
            raise DomainException(f"Invalid collector type: {collector_key}. Supported values are {', '.join(CollectorType.__members__)}")

        self.interfaces = interfaces
        self.id = Device.build_id(self.collector, self.label, self.aggregate_id)

    @staticmethod
    def build_id(collector: CollectorType, label: str, aggregate_id: str):
        return f"{collector.name}.{label}.{aggregate_id}"

    def get_interface_by_name(self, name: str) -> Optional[DeviceInterface]:
        for interface in self.interfaces:
            if interface.name == name:
                return interface
        return None

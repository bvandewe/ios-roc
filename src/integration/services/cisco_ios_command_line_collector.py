import logging

from netmiko import ConnectHandler
from netmiko.exceptions import (
    ConnectionException,
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    ReadException,
    ReadTimeout,
)
from neuroglia.eventing.cloud_events.infrastructure import CloudEventBus
from neuroglia.eventing.cloud_events.infrastructure.cloud_event_publisher import (
    CloudEventPublishingOptions,
)
from neuroglia.mapping import Mapper
from neuroglia.mediation import Mediator

from application.settings import IosRocSettings
from domain.models import CommandLine, CommandOutput, Device
from integration.services.cisco_command_line_collector_base import (
    CiscoCommandLineCollectorBase,
    CiscoCommandLineCollectorException,
)

log = logging.getLogger(__name__)


class CiscoIosCommandLineCollector(CiscoCommandLineCollectorBase):
    def __init__(self, mediator: Mediator, mapper: Mapper, cloud_event_bus: CloudEventBus, cloud_event_publishing_options: CloudEventPublishingOptions, app_settings: IosRocSettings):
        super().__init__(mediator, mapper, cloud_event_bus, cloud_event_publishing_options, app_settings)

    async def collect_async(self, command_lines: list[CommandLine], device: Device, interface_name: str) -> list[CommandOutput]:
        """Collects a sequence of command lines from a device with a single connection."""
        interface = device.get_interface_by_name(interface_name)
        if not interface:
            raise CiscoCommandLineCollectorException(f"Interface {interface_name} not found on device {device.hostname}")
        if interface.authentication.properties.password is None:
            raise CiscoCommandLineCollectorException(f"Password is required for device {device.hostname} interface {interface_name}")
        if interface.authentication.properties.secret is None:
            raise CiscoCommandLineCollectorException(f"Enable Password is required for device {device.hostname} interface {interface_name}")

        log.debug(f"Collecting {len(command_lines)} command lines from device {device.hostname} at {interface.ip}:{interface.port}")

        try:
            device_access = {
                "device_type": device.collector.value,
                "ip": str(interface.ip),
                "port": interface.port,
                "username": interface.authentication.properties.username or "",
                "password": interface.authentication.properties.password.get_secret_value() or "",
                "secret": interface.authentication.properties.secret.get_secret_value() or "",
            }
            outputs = []
            prompt_pattern = rf"{device.hostname}"
            with ConnectHandler(**device_access) as net_connect:
                for command_line in command_lines:
                    try:
                        if not net_connect.check_enable_mode("#"):
                            net_connect.enable()
                        cli_ouput = CommandOutput(line=command_line, device=device)
                        log.debug(f"Collecting command line {command_line.line} from device {device.hostname} at {interface.ip}:{interface.port}")
                        collected_text = net_connect.send_command(command_string=command_line.line, read_timeout=command_line.timeout, strip_prompt=False, expect_string=prompt_pattern)
                        cli_ouput.output = collected_text
                        log.debug(f"Collected {len(collected_text)} characters in {cli_ouput.duration.total_seconds()}s for '{command_line.line}' from device {device.hostname}")

                    except (ReadException, ReadTimeout, NetmikoTimeoutException) as e:
                        err = f"A {type(e)} exception occurred when collecting '{command_line.line}' from device {device.hostname}: {e}"
                        log.warning(err)
                        cli_ouput.error = err

                    outputs.append(cli_ouput)

            return outputs

        except NetmikoAuthenticationException as e:
            err = f"An AuthenticationException occurred when connecting to device {device.hostname}: {e}"
            log.error(err)
            raise CiscoCommandLineCollectorException(err)

        except (ConnectionException, NetmikoTimeoutException, Exception) as e:
            log.error(f"A {type(e)} exception occurred when collecting '{command_line.line}' from device {device.hostname}: {e}")
            raise CiscoCommandLineCollectorException(e)

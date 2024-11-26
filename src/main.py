import logging

from fastapi.middleware.cors import CORSMiddleware
from neuroglia.eventing.cloud_events.infrastructure import (
    CloudEventIngestor,
    CloudEventMiddleware,
)
from neuroglia.eventing.cloud_events.infrastructure.cloud_event_publisher import (
    CloudEventPublisher,
)
from neuroglia.hosting.web import ExceptionHandlingMiddleware, WebApplicationBuilder
from neuroglia.mapping.mapper import Mapper
from neuroglia.mediation.mediator import Mediator
from neuroglia.serialization.json import JsonSerializer

from api.services.logger import configure_logging
from api.services.openapi import set_oas_description
from application.settings import IosRocSettings, app_settings
from integration.services.cisco_command_line_collector_base import CiscoCommandLineCollectorBase
from integration.services.cisco_ios_command_line_collector import CiscoIosCommandLineCollector


configure_logging()
log = logging.getLogger(__name__)
log.debug("Bootstraping the app...")

# Set the logging level for httpx specifically
netmiko_logger = logging.getLogger("netmiko")
netmiko_logger.setLevel(logging.INFO)

# App' constants
database_name = "lds-roc"
application_modules = [
    "application.commands",
    "application.events.integration",
    "application.mapping",
    "application.queries",
    "application.services",
    "domain.models",
]

builder = WebApplicationBuilder()
builder.settings = app_settings

# Required shared resources
Mapper.configure(builder, application_modules)
Mediator.configure(builder, application_modules)
JsonSerializer.configure(builder)
CloudEventIngestor.configure(builder, ["application.events.integration"])
CloudEventPublisher.configure(builder)

# App Settings
builder.services.add_singleton(IosRocSettings, singleton=app_settings)

# Custom shared resources
builder.services.add_transient(CiscoCommandLineCollectorBase, CiscoIosCommandLineCollector)

# Inject Queries. (FIX: mediator issue TBD)

builder.add_controllers(["api.controllers"])

app = builder.build()

app.settings = app_settings  # type: ignore (monkey patching)
set_oas_description(app, app_settings)

app.add_middleware(ExceptionHandlingMiddleware, service_provider=app.services)
app.add_middleware(CloudEventMiddleware, service_provider=app.services)
app.use_controllers()

# Enable CORS (TODO: add settings to configure allowed_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.run()
log.debug("App is ready to rock.")

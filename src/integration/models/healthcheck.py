from pydantic import BaseModel, Field

flag = Field(description="Boolean Flag stating if the external dependency is available.")


class SelfHealthCheckResultDto(BaseModel):
    online: bool

    detail: str


class ExternalDependenciesHealthCheckResultDto(BaseModel):
    """Flags statings whether external dependencies are available."""

    identity_provider: bool = flag
    """Whether the IDP is reachable."""

    events_gateway: bool = flag
    """Whether the EventsGateway is reachable."""

    all: bool = Field(description="Boolean Flag stating if all external dependencies are available.")
    """Whether all external dependencies are reachable."""

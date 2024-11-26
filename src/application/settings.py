from typing import Optional

from neuroglia.hosting.abstractions import ApplicationSettings
from pydantic import BaseModel, ConfigDict, computed_field


class IosRocSettings(ApplicationSettings, BaseModel):
    model_config = ConfigDict(extra="allow")
    log_level: str = "INFO"
    local_dev: bool = False
    app_title: str = "Cisco Certs IOS Remote Output Collector"
    app_version: str = "0.1.0"

    # OAuth2.0 Settings
    jwt_authority: str = "http://keycloak99/realms/mozart"  # https://sj-keycloak.ccie.cisco.com/auth/realms/mozart
    jwt_signing_key: str = "copy-from-jwt-authority"
    jwt_audience: str = "ios-roc"
    required_scope: str = "api"

    # SWAGERUI Settings
    oauth2_scheme: Optional[str] = None  # "client_credentials"  # "client_credentials" or "authorization_code" or None/missing
    swagger_ui_jwt_authority: str = "http://localhost:9990/realms/mozart"  # the URL where the local swaggerui can reach its local keycloak, e.g. http://localhost:8087
    swagger_ui_client_id: str = "ios-roc"
    swagger_ui_client_secret: str = "somesecret"

    # App Settings
    default_interface_name: str = "console"

    @computed_field
    def jwt_authorization_url(self) -> str:
        return f"{self.jwt_authority}/protocol/openid-connect/auth"

    @computed_field
    def jwt_token_url(self) -> str:
        return f"{self.jwt_authority}/protocol/openid-connect/token"

    @computed_field
    def swagger_ui_authorization_url(self) -> str:
        return f"{self.swagger_ui_jwt_authority}/protocol/openid-connect/auth"

    @computed_field
    def swagger_ui_token_url(self) -> str:
        return f"{self.swagger_ui_jwt_authority}/protocol/openid-connect/token"


app_settings = IosRocSettings(_env_file=".env")

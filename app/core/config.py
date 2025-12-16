from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PVE_HOST: str = Field(..., description="Proxmox host/IP")
    PVE_USER: str = Field(..., description="User like 'root@pam' or 'api@pve'")
    PVE_TOKEN_NAME: str = Field(..., description="API token name")
    PVE_TOKEN_VALUE: str = Field(..., description="API token value")
    PVE_VERIFY_SSL: bool = Field(default=False, description="Verify SSL cert")
    PVE_TIMEOUT: int = Field(default=10, ge=1, le=120, description="HTTP timeout (seconds)")
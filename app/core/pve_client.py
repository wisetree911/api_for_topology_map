from fastapi import HTTPException
from pydantic import ValidationError
from proxmoxer import ProxmoxAPI

from app.core.config import Settings

def get_settings() -> Settings:
    return Settings()

def get_proxmox():
    s = get_settings()
    try:
        return ProxmoxAPI(
            s.PVE_HOST,
            user=s.PVE_USER,
            token_name=s.PVE_TOKEN_NAME,
            token_value=s.PVE_TOKEN_VALUE,
            verify_ssl=s.PVE_VERIFY_SSL,
            timeout=s.PVE_TIMEOUT,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to connect to Proxmox API: {e}")

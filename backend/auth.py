import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer_scheme = HTTPBearer(auto_error=False)

API_TOKEN: str | None = os.getenv("API_TOKEN")


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """Enforce bearer token auth when API_TOKEN is set in the environment.

    If API_TOKEN is not configured, auth is disabled (local dev convenience).
    """
    if API_TOKEN is None:
        return
    if credentials is None or credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
            headers={"WWW-Authenticate": "Bearer"},
        )

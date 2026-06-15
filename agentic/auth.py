from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from agentic.config import settings

security = HTTPBearer(auto_error=False)


def create_access_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": expires,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        return "anonymous"
    try:
        payload = verify_token(credentials.credentials)
        return payload.get("sub", "anonymous")
    except HTTPException:
        return "anonymous"


async def get_current_user_ws(websocket: WebSocket) -> str:
    token = websocket.headers.get("authorization", "").removeprefix("Bearer ")
    if not token:
        return "anonymous"
    try:
        payload = verify_token(token)
        return payload.get("sub", "anonymous")
    except HTTPException:
        return "anonymous"

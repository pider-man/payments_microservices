"""
Client for interacting with User Service.
"""
import httpx
from config import settings
from fastapi import HTTPException


async def verify_user_token(token: str) -> dict:
    """
    Verify user token with User Service.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.user_service_url}/users/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=401, detail="Invalid token")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="User service unavailable")

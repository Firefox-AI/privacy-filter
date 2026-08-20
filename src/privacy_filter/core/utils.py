import os
from secrets import compare_digest
from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from privacy_filter.core.classes import FilterRequest
from privacy_filter.core.config import env

api_key_header = APIKeyHeader(name="x-pf-api-key", auto_error=False)


async def authorize_request(
    req: FilterRequest,
    api_key: Annotated[str | None, Security(api_key_header)] = None,
) -> FilterRequest:
    if not env.MASTER_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MASTER_KEY is not configured.",
        )

    if api_key is None or not compare_digest(api_key, env.MASTER_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return req

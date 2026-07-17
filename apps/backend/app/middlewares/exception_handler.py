import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("aeos.backend")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "data": None,
            "errors": ["An unexpected error occurred"],
        },
    )

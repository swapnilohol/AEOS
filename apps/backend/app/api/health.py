from fastapi import APIRouter

from app.schemas.response import ApiResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponse)
def health_check() -> ApiResponse:
    return ApiResponse(success=True, message="ok", data={"status": "healthy"})

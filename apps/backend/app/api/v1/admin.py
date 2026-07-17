from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import RoleName, User
from app.schemas.admin import AdminDashboardResponse
from app.schemas.response import ApiResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=ApiResponse[AdminDashboardResponse])
def get_admin_dashboard(
    _admin: User = Depends(require_roles(RoleName.ADMIN.value)),
    db: Session = Depends(get_db),
):
    data = AdminService(db).get_dashboard()
    return ApiResponse(success=True, message="ok", data=data)

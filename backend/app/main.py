from fastapi import FastAPI

from app.core.config import PROJECT_NAME
from app.models import (
    user,
    problem,
    submission,
    testcase
)
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.problem import router as problem_router
from app.routers.submission import (
    router as submission_router
)
from app.routers.testcase import (
    router as testcase_router
)
from app.database import Base, engine
app = FastAPI(
    title=PROJECT_NAME
)
from app.routers.leaderboard import (
    router as leaderboard_router
)
from app.routers import dashboard
app.include_router(
    dashboard.router
)
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(problem_router)
app.include_router(
    submission_router
)
app.include_router(
    testcase_router
)
app.include_router(
    leaderboard_router
)

@app.get("/")
def root():
    return {
        "project": "AEOS",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AEOS Backend"
    }

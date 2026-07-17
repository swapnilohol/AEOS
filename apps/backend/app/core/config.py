from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    jwt_secret: str = "change-me-access"
    jwt_refresh_secret: str = "change-me-refresh"
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    login_max_attempts: int = 5
    login_lockout_minutes: int = 15

    cookie_secure: bool = False
    frontend_origin: str = "http://localhost:3000"

    database_url: str = "postgresql://aeos_user:change-me@postgres:5432/aeos_db"
    redis_url: str = "redis://redis:6379/0"

    # --- Scoring Module ---
    performance_target_ms: int = 1000
    performance_max_penalty_ratio: float = 0.10
    late_penalty_ratio: float = 0.20
    internal_service_token: str = "change-me-internal-token"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

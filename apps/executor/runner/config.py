from pydantic_settings import BaseSettings


class ExecutorSettings(BaseSettings):
    database_url: str = "postgresql://aeos_user:change-me@postgres:5432/aeos_db"
    redis_url: str = "redis://redis:6379/0"

    executor_cpu_limit: float = 1.0
    executor_memory_limit: str = "256m"
    executor_timeout_seconds: int = 10

    execution_queue_key: str = "execution_queue"
    queue_poll_timeout_seconds: int = 5

    backend_internal_url: str = "http://backend:8000/api/v1"
    internal_service_token: str = "change-me-internal-token"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = ExecutorSettings()

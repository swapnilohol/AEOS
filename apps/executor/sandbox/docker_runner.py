import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import docker
from docker.errors import ContainerError, ImageNotFound

from images.language_configs import get_language_config
from runner.config import settings

_docker_client: docker.DockerClient | None = None


def _get_docker_client() -> docker.DockerClient:
    global _docker_client
    if _docker_client is None:
        _docker_client = docker.from_env()
    return _docker_client


@dataclass
class ExecutionOutcome:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    execution_time_ms: int


class SandboxRunner:
    """Runs untrusted student code in an isolated, ephemeral Docker
    container with no network access and enforced CPU/memory/time limits."""

    def run(self, language: str, code: str, stdin_data: str) -> ExecutionOutcome:
        config = get_language_config(language)
        workspace = Path(tempfile.mkdtemp(prefix="aeos-submission-"))

        try:
            (workspace / config.source_filename).write_text(code)
            (workspace / "input.txt").write_text(stdin_data or "")

            shell_cmd = config.run_cmd
            if config.compile_cmd:
                shell_cmd = f"{config.compile_cmd} && {config.run_cmd}"

            return self._run_container(config.image, shell_cmd, workspace)
        finally:
            shutil.rmtree(workspace, ignore_errors=True)

    def _run_container(self, image: str, shell_cmd: str, workspace: Path) -> ExecutionOutcome:
        client = _get_docker_client()
        started = time.monotonic()
        container = None

        try:
            container = client.containers.run(
                image=image,
                command=["sh", "-c", shell_cmd],
                working_dir="/workspace",
                volumes={str(workspace): {"bind": "/workspace", "mode": "rw"}},
                network_mode="none",
                mem_limit=settings.executor_memory_limit,
                nano_cpus=int(settings.executor_cpu_limit * 1_000_000_000),
                user="1000:1000",
                detach=True,
                stdout=True,
                stderr=True,
            )

            timed_out = False
            try:
                exit_status = container.wait(timeout=settings.executor_timeout_seconds)
                exit_code = exit_status.get("StatusCode")
            except Exception:
                timed_out = True
                exit_code = None
                container.kill()

            stdout = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            duration_ms = int((time.monotonic() - started) * 1000)

            return ExecutionOutcome(
                stdout=stdout,
                stderr=stderr if not timed_out else stderr + "\n[Execution timed out]",
                exit_code=exit_code,
                timed_out=timed_out,
                execution_time_ms=duration_ms,
            )
        except ImageNotFound as exc:
            return ExecutionOutcome(
                stdout="",
                stderr=f"Runtime image not available: {exc}",
                exit_code=None,
                timed_out=False,
                execution_time_ms=int((time.monotonic() - started) * 1000),
            )
        except ContainerError as exc:
            return ExecutionOutcome(
                stdout="",
                stderr=str(exc),
                exit_code=exc.exit_status,
                timed_out=False,
                execution_time_ms=int((time.monotonic() - started) * 1000),
            )
        finally:
            if container is not None:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

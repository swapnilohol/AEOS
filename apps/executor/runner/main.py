"""
Executor Service Entrypoint.

Consumes submission IDs from the Redis execution queue (pushed by the
backend's Editor Module after a student submits code) and processes each
one: runs the code against all of a problem's test cases inside an
isolated, network-disabled Docker container, then stores results and a
score, updating the submission's status.

Runs as a long-lived worker process (see docker-compose.yml `executor`
service) — it exposes no HTTP API of its own.
"""
import logging
import signal
import sys

from runner.db import get_session
from runner.processor import SubmissionProcessor
from runner.queue_client import dequeue_submission_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aeos.executor")

_shutdown_requested = False


def _handle_shutdown_signal(signum, frame) -> None:
    global _shutdown_requested
    logger.info("Shutdown signal received; finishing current job then exiting")
    _shutdown_requested = True


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)
    signal.signal(signal.SIGINT, _handle_shutdown_signal)

    logger.info("Executor worker started; polling execution queue")

    while not _shutdown_requested:
        try:
            submission_id = dequeue_submission_id()
        except Exception:
            logger.exception("Failed to poll execution queue; retrying")
            continue

        if submission_id is None:
            continue  # poll timeout elapsed with no job; loop and check shutdown flag

        logger.info("Processing submission %s", submission_id)
        db = get_session()
        try:
            SubmissionProcessor(db).process(submission_id)
        except Exception:
            logger.exception("Unhandled error processing submission %s", submission_id)
        finally:
            db.close()

    logger.info("Executor worker stopped")
    sys.exit(0)


if __name__ == "__main__":
    main()

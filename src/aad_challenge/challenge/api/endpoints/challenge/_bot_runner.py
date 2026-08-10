import time
from typing import Any

import requests

from api.config import config
from api.logger import logger

_TERMINAL_STATUSES = {"passed", "failed", "partial", "error"}


def _auth_headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def trigger_run(
    *,
    server_url: str,
    device_type: str,
    driver_preset: str,
    framework_name: str,
    count: int = 1,
    headless: bool = True,
    session: requests.Session | None = None,
) -> str:
    """Start one bot-runner framework run and return its batch id.

    Only 429 responses are retried because they represent the runner's bounded
    concurrency cap. Other errors, especially 409 device mismatches, fail fast.
    """
    bot_runner_config = config.challenge.bot_runner
    http = session or requests.Session()
    web_url = _join_url(
        str(bot_runner_config.public_base_url),
        _join_url(config.api.prefix, "/_web"),
    )
    logger.info(f"web_url for bot-runner: {web_url}")
    payload: dict[str, Any] = {
        "bot": bot_runner_config.bot,
        "driver_preset": driver_preset,
        "device_type": device_type,
        "url": web_url,
        "count": count,
        "headless": headless,
        "metadata": {
            "framework": framework_name,
            "headless": headless,
            "count": count,
        },
    }
    url = _join_url(server_url, "/api/runs")
    max_attempts = bot_runner_config.busy_retry_count + 1
    backoff = bot_runner_config.busy_backoff_initial_sec

    for attempt in range(max_attempts):
        response = http.post(
            url,
            json=payload,
            headers=_auth_headers(bot_runner_config.api_key.get_secret_value()),
            timeout=bot_runner_config.request_timeout_sec,
        )
        if response.status_code == 429 and attempt < bot_runner_config.busy_retry_count:
            delay = min(backoff, bot_runner_config.busy_backoff_max_sec)
            logger.info(
                f"bot-runner is busy for framework {framework_name}; "
                f"retrying in {delay:.2f}s"
            )
            time.sleep(delay)
            backoff = delay * 2 if delay > 0 else 0
            continue

        response.raise_for_status()
        data = response.json()
        batch_id = data.get("batch_id")
        if not batch_id:
            raise ValueError("bot-runner response did not include batch_id")
        return str(batch_id)

    raise RuntimeError("unreachable bot-runner retry state")


def _status_poll_count(bot_runner_config) -> int:
    """How many status checks fit inside the configured run budget."""
    return max(
        1,
        int(
            bot_runner_config.run_timeout_sec / bot_runner_config.run_poll_interval_sec
        ),
    )


def wait_for_run(
    batch_id: str,
    server_url: str,
) -> str:
    """Poll bot-runner until the run reaches a terminal state.

    Returns that status, or ``"timeout"`` if the run budget elapsed first.
    ``"timeout"`` is deliberately not one of :data:`_TERMINAL_STATUSES`, so a
    caller can tell "the run finished badly" from "we stopped waiting".
    """
    bot_runner_config = config.challenge.bot_runner
    url = _join_url(server_url, f"/api/runs/{batch_id}")
    poll_count = _status_poll_count(bot_runner_config)

    for attempt in range(poll_count):
        is_last_poll = attempt == poll_count - 1
        try:
            response = requests.get(
                url,
                headers=_auth_headers(bot_runner_config.api_key.get_secret_value()),
                timeout=bot_runner_config.request_timeout_sec,
            )
            response.raise_for_status()
            status = str(response.json().get("status", ""))
            if status in _TERMINAL_STATUSES:
                return status
        except requests.RequestException:
            if is_last_poll:
                raise

        if not is_last_poll:
            time.sleep(bot_runner_config.run_poll_interval_sec)

    return "timeout"


__all__ = [
    "trigger_run",
    "wait_for_run",
]

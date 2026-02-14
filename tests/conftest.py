# -*- coding: utf-8 -*-
"""
Fixtures and configuration for AADController tests.

This module provides:
- Mock challenge configuration
- Mock miner commits with scoring logs
- Mock reference commits
- Helper fixtures for testing
"""

import copy
import logging
import os
import re
import subprocess
import threading
import time

import pytest
import requests
from dotenv import load_dotenv

load_dotenv(".env", override=True)

from redteam_core.challenge_pool import ACTIVE_CHALLENGES
from redteam_core.config.main import constants
from redteam_core.validator.models import MinerChallengeCommit, ScoringLog

logger = logging.getLogger(__name__)


# Mock miner output data
MOCK_MINER_OUTPUT = {
    "detection_files": [
        {
            "content": "/**\n * Simple detector stub for `nodriver`.\n * This module exposes `detect_nodriver` and always returns false.\n */\n\nfunction detect_nodriver() {\n  return true;\n}\n\nif (typeof window !== 'undefined') window.detect_nodriver = detect_nodriver;\n",
            "file_name": "nodriver.js",
        },
        {
            "content": "/**\n * Simple detector stub for `playwright`.\n * This module exposes `detect_playwright` and always returns false.\n */\n\nfunction detect_playwright() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_playwright = detect_playwright;\n",
            "file_name": "playwright.js",
        },
        {
            "content": "/**\n * Simple detector stub for `selenimu`.\n * This module exposes `detect_selenium` and always returns false.\n */\n\nfunction detect_selenium() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_selenium = detect_selenium;\n",
            "file_name": "selenium.js",
        },
        {
            "content": "/**\n * Simple detector stub for `zendriver`.\n * This module exposes `detect_zendriver` and always returns false.\n */\n\nfunction detect_zendriver() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_zendriver = detect_zendriver;\n",
            "file_name": "zendriver.js",
        },
        {
            "content": "/**\n * Simple detector stub for `puppeteer`.\n * This module exposes `detect_puppeteer` and always returns false.\n */\n\nfunction detect_puppeteer() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_puppeteer = detect_puppeteer;\n",
            "file_name": "puppeteer.js",
        },
        {
            "content": "/**\n * Simple detector stub for `puppeteer-extra`.\n * This module exposes `detect_puppeteer-extra` and always returns false.\n */\n\nfunction detect_puppeteer_extra() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_puppeteer_extra = detect_puppeteer_extra;\n",
            "file_name": "puppeteer-extra.js",
        },
        {
            "content": "/**\n * General detector for any browser automation.\n * This module exposes `detect_automation` and returns true if any automation is detected.\n * Returns false for genuine human users.\n */\n\nfunction detect_automation() {\n\tconsole.log(navigator.userAgent);\n\treturn false;\n}\n\nif (typeof window !== 'undefined') window.detect_automation = detect_automation;\n",
            "file_name": "automation.js",
        },
        {
            "content": "/**\n * Simple detector stub for `patchright`.\n * This module exposes `detect_patchright` and always returns false.\n */\n\nfunction detect_patchright() {\n  return false;\n}\n\nif (typeof window !== 'undefined') window.detect_patchright = detect_patchright;\n",
            "file_name": "patchright.js",
        },
    ]
}
MOCK_MINER_INPUT = {
    "random_val": "fwYzpCfVG8mTHmCt",
}

# ==========================================================================
# Fixtures
# ==========================================================================


@pytest.fixture
def mock_miner_output():
    """Fixture providing mock miner output data.

    Returns:
        dict: Mock miner output data
    """
    return copy.deepcopy(MOCK_MINER_OUTPUT)


@pytest.fixture(scope="session")
def mock_challenge_info():
    """Fixture providing mock challenge configuration.

    Returns:
        dict: Challenge configuration matching production structure
    """
    return copy.deepcopy(ACTIVE_CHALLENGES["ada_detection_v1"])


@pytest.fixture
def mock_scoring_log():
    """Fixture providing a single mock scoring log.

    Returns:
        ScoringLog: Scoring log with minimal test data
    """
    return ScoringLog(
        miner_input=copy.deepcopy(MOCK_MINER_INPUT),
        miner_output=copy.deepcopy(MOCK_MINER_OUTPUT),
        score=None,
        error=None,
    )


@pytest.fixture
def mock_miner_commits(mock_scoring_log):
    """Fixture providing mock miner commits for testing.

    Creates 2 miner commits with scoring logs pre-populated.

    Returns:
        list[MinerChallengeCommit]: List of miner challenge commits
    """
    commits = []
    # Create a copy of the scoring log for each miner
    log = ScoringLog(
        miner_input=copy.deepcopy({}),
        miner_output=copy.deepcopy(MOCK_MINER_OUTPUT),
        score=None,
        error=None,
    )

    commit = MinerChallengeCommit(
        miner_uid=1,
        miner_hotkey=f"test_hotkey_1",
        challenge_name="ada_detection_v1",
        docker_hub_id=f"test/miner_1@sha256:abc123",
        scoring_logs=[log],
        comparison_logs={},  # Empty initially
    )
    commits.append(commit)

    return commits


@pytest.fixture
def mock_reference_commits():
    """Fixture providing mock reference commits for comparison.

    Creates 1 reference commit with pre-populated scoring logs.

    Returns:
        list[MinerChallengeCommit]: List of reference comparison commits
    """
    commits = []

    for i in range(2):
        log = ScoringLog(
            miner_input=copy.deepcopy(MOCK_MINER_INPUT),
            miner_output=copy.deepcopy(MOCK_MINER_OUTPUT),
            score=None,
            error=None,
        )

        commit = MinerChallengeCommit(
            miner_uid=1000 + i,
            miner_hotkey=f"reference_hotkey_{i}",
            challenge_name="ada_detection_v1",
            docker_hub_id=f"reference/miner_{i}@sha256:def456",
            scoring_logs=[log],
            comparison_logs={},  # Empty initially
        )
        commits.append(commit)

    return commits


@pytest.fixture
def mock_challenge_inputs():
    """Fixture providing mock challenge inputs.

    Returns:
        list[dict]: List of challenge input dictionaries
    """
    return [copy.deepcopy(MOCK_MINER_INPUT)]


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    """Setup logging configuration for tests."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s | %(levelname)5s | %(filename)s:%(lineno)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _expand_env_variables(value: str) -> str:
    """Expand ${VAR} style environment variables in a string."""
    if isinstance(value, str) and "${" in value and "}" in value:
        pattern = r"\$\{([^}]+)\}"

        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))

        return re.sub(pattern, replace_var, value)
    return value


@pytest.fixture(scope="session")
def internal_services_health():
    """Check if internal services are running and healthy."""
    try:
        logger.info("Checking internal services health...")
        api_url = str(constants.INTERNAL_SERVICES.API_URL)
        api_key = constants.INTERNAL_SERVICES.API_KEY

        logger.info(f"Internal services URL: {api_url}")
        logger.info(f"API Key present: {bool(api_key) and len(api_key) > 0}")
        logger.info(
            f"API Key (first 20 chars): {api_key[:20] if api_key else 'None'}..."
        )

        headers = {"X-API-KEY": api_key} if api_key else {}
        response = requests.get(
            f"{api_url}/health", timeout=3, headers=headers, verify=False
        )
        is_healthy = response.status_code == 200
        logger.info(
            f"Internal services health check: {response.status_code} - {'OK' if is_healthy else 'FAILED'}"
        )
        return is_healthy
    except Exception as e:
        logger.error(f"Internal services health check failed: {e}")
        return False


@pytest.fixture(scope="session")
def challenge_container(internal_services_health):
    """Build and run challenge container using kwargs from active_challenges.yaml."""
    challenge_info = ACTIVE_CHALLENGES.get("ada_detection_v1", {})
    challenge_image = challenge_info.get(
        "challenge_image", "redteamsubnet61/ada_detection:v1.0.0-251215"
    )
    run_kwargs = challenge_info.get("challenge_container_run_kwargs", {})
    container_name = run_kwargs.get("name", "ada_detection_v1")

    logger.info(f"=== Challenge container setup starting ===")
    logger.info(f"Container name: {container_name}")
    logger.info(f"Challenge image: {challenge_image}")

    log_process = None
    log_thread = None
    stop_event = threading.Event()

    # Build/pull image
    try:
        logger.info(f"Pulling docker image: {challenge_image}")
        result = subprocess.run(
            ["docker", "pull", challenge_image],
            check=True,
            capture_output=True,
            timeout=300,
        )
        logger.info(f"✓ Image pulled successfully")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠ Image pull failed: {e.stderr.decode()}")
    except Exception as e:
        logger.warning(f"⚠ Image pull exception: {e}")

    # Remove old container if exists
    logger.info(f"Removing old container: {container_name}")
    subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)

    # Build docker run command with kwargs
    try:
        docker_cmd = ["docker", "run", "-d", "--name", container_name]

        # Add platform
        if "platform" in run_kwargs:
            docker_cmd.extend(["--platform", run_kwargs["platform"]])

        # Add privileged
        if run_kwargs.get("privileged", False):
            docker_cmd.append("--privileged")

        # Add environment variables (expand ${VAR} syntax)
        env_dict = run_kwargs.get("environment", {})
        logger.info(f"Setting up {len(env_dict)} environment variables...")
        for key, value in env_dict.items():
            expanded_value = _expand_env_variables(str(value))
            # If expansion resulted in unchanged ${VAR} pattern, log warning but skip
            if expanded_value.startswith("${") and expanded_value.endswith("}"):
                logger.warning(
                    f"  ⚠ {key}: Environment variable not found: {expanded_value}"
                )
                continue
            docker_cmd.extend(["-e", f"{key}={expanded_value}"])
            # Log sensitive env vars securely
            if "KEY" in key or "PASSWORD" in key:
                logger.debug(
                    f"  {key}=***{expanded_value[-10:] if len(expanded_value) > 10 else ''}"
                )
            else:
                logger.debug(
                    f"  {key}={expanded_value[:60]}..."
                    if len(str(expanded_value)) > 60
                    else f"  {key}={expanded_value}"
                )

        # Add volumes (skip if env vars not resolved)
        volumes = run_kwargs.get("volumes", [])
        if volumes:
            logger.info(f"Setting up {len(volumes)} volume(s)...")
        for volume in volumes:
            expanded_volume = _expand_env_variables(volume)
            # Skip volumes with unresolved env vars
            if "${" in expanded_volume and "}" in expanded_volume:
                logger.warning(
                    f"  ⚠ Skipping volume with unresolved env var: {expanded_volume}"
                )
                continue
            docker_cmd.extend(["-v", expanded_volume])
            logger.debug(f"  Volume: {expanded_volume}")

        # Add port mapping
        docker_cmd.extend(["-p", "10001:10001"])
        logger.debug(f"  Port mapping: 10001:10001")

        # Add image
        docker_cmd.append(challenge_image)

        logger.info(f"Starting container...")
        result = subprocess.run(
            docker_cmd,
            check=True,
            capture_output=True,
            timeout=30,
        )

        container_id = result.stdout.decode().strip()
        logger.info(f"✓ Container started: {container_id[:12]}")

        # Wait for container to be ready
        logger.info("Waiting for container to stabilize (5 sec)...")
        time.sleep(5)

        # Verify container is running
        check_result = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"name={container_name}",
                "--format",
                "{{.ID}} {{.Status}}",
            ],
            capture_output=True,
            text=True,
        )

        ps_output = check_result.stdout.strip()
        logger.info(
            f"Container status check: {ps_output if ps_output else 'NOT RUNNING'}"
        )

        if not ps_output:
            logger.error(f"❌ Container is NOT running!")
            # Get logs to debug
            try:
                logs_result = subprocess.run(
                    ["docker", "logs", "--tail", "50", container_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                logger.error(
                    f"Container logs (last 50 lines):\n{logs_result.stdout}\n{logs_result.stderr}"
                )
            except Exception as log_err:
                logger.error(f"Could not retrieve logs: {log_err}")
        else:
            logger.info(f"✓ Container is running!")

            def _stream_logs():
                nonlocal log_process
                try:
                    log_process = subprocess.Popen(
                        ["docker", "logs", "-f", container_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                    )
                    if log_process.stdout:
                        for line in log_process.stdout:
                            if stop_event.is_set():
                                break
                            logger.info(f"[challenge-container] {line.rstrip()}")
                except Exception as ex:
                    logger.warning(f"Log stream stopped: {ex}")

            log_thread = threading.Thread(target=_stream_logs, daemon=True)
            log_thread.start()

        yield container_name

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Container startup failed with error:")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Stdout: {e.stdout.decode() if e.stdout else 'None'}")
        logger.error(f"Stderr: {e.stderr.decode() if e.stderr else 'None'}")

        # Try to get logs
        try:
            logs = subprocess.run(
                ["docker", "logs", "--tail", "100", container_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            logger.error(f"Container logs:\n{logs.stdout}\n{logs.stderr}")
        except Exception as log_err:
            logger.error(f"Could not retrieve logs: {log_err}")
        raise

    finally:
        stop_event.set()
        if log_process and log_process.poll() is None:
            try:
                log_process.terminate()
            except Exception:
                pass
        if log_thread:
            log_thread.join(timeout=2)
        # Cleanup
        logger.info(f"Cleaning up container: {container_name}")
        subprocess.run(["docker", "rm", "-f", container_name], capture_output=True)
        logger.info(f"=== Challenge container cleanup complete ===")

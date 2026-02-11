import os
import random
import subprocess
import time
import requests

import docker
from docker import DockerClient
from docker.types import Ulimit
from docker.models.networks import Network
from pydantic import validate_call

from api.config import config
from api.logger import logger
from api.endpoints.challenge.schemas import MinerOutput, TaskStatusEnum
from api.endpoints.challenge._nst_manager import delete_nst_profile


@validate_call
def copy_detection_files(miner_output: MinerOutput, detections_dir: str) -> None:

    logger.info(f"Copying detection files from {detections_dir}")
    try:
        os.makedirs(detections_dir, exist_ok=True)
        for _detection_file_pm in miner_output.detection_files:
            _detection_path = os.path.join(detections_dir, _detection_file_pm.file_name)
            with open(_detection_path, "w") as _detection_file:
                _detection_file.write(_detection_file_pm.content)

        logger.success("Successfully copied detection files.")

    except Exception as err:
        logger.error(f"Failed to copy detection files: {err}!")
        raise

    return


def run_bot_container(
    docker_client: DockerClient,
    image_name: str = "bot:latest",
    container_name: str = "bot_container",
    network_name: str = "framework_network",
    ulimit: int = 32768,
    **kwargs,
) -> str:
    logger.info(f"Running {image_name} docker container.")
    logger.info(f"Using NSTBrowser profile ID: {kwargs.get('profile_id')}")

    try:
        # Network setup from the provided function
        _networks = docker_client.networks.list(names=[network_name])
        _network: Network
        if not _networks:
            _network = docker_client.networks.create(
                name=network_name, driver="bridge", internal=True
            )
        else:
            _network = docker_client.networks.get(network_name)

        _network_id = _network.id
        if _network_id is None:
            raise RuntimeError("Failed to determine Docker network ID!")

        _network_info = docker_client.api.inspect_network(net_id=_network_id)
        _gateway_ip = _network_info["IPAM"]["Config"][0]["Gateway"]

        _ulimit_nofile = Ulimit(name="nofile", soft=ulimit, hard=ulimit)

        _web_url = f"http://{_gateway_ip}:{config.api.port}/_web"
        logger.info(
            f"Running {image_name} docker container to connect to {_web_url} in {network_name} network."
        )

        _run_kwargs = {
            "image": image_name,
            "name": container_name,
            "network": network_name,
            "ulimits": [_ulimit_nofile],
            "environment": {
                "NSTBROWSER_API_KEY": config.challenge.nstbrowser.api_key.get_secret_value(),
                "NSTBROWSER_PROFILE_ID": kwargs.get("profile_id"),
                "NSTBROWSER_HOST": config.challenge.nstbrowser.host,
                "NSTBROWSER_PORT": config.challenge.nstbrowser.port,
                "NSTBROWSER_PROTOCOL": config.challenge.nstbrowser.protocol,
                "PLAYGROUND_LINK": _web_url,
                "ENV": "PRODUCTION",
            },
            "platform": "linux/amd64",
            "detach": True,
        }
        if "selenium" in image_name:
            _run_kwargs["environment"]["NSTBROWSER_PORT"] = 9222
            _run_kwargs["environment"]["NSTBROWSER_HOST"] = "nstbrowser"
            logger.info(f"Retrieved NSTBrowser IP : nstbrowser:9222")

        _container = docker_client.containers.run(**_run_kwargs)

        # Stream container logs
        try:
            for log in _container.logs(stream=True, follow=True):
                logger.debug(log.decode().strip())
        except Exception as e:
            logger.error(f"Error streaming logs: {e}")

        logger.info(f"Successfully ran {image_name} docker container.")

    except Exception as err:
        logger.error(f"Failed to run {image_name} docker: {str(err)}!")
        raise

    return _container.name


def run_port_forwarding_container(
    docker_client: DockerClient,
    port: int,
):
    try:
        c = docker_client.containers.get("nst-debug-relay")
        c.remove(force=True)
    except docker.errors.NotFound:
        pass  # Container does not exist, proceed to create a new one
    docker_client.containers.run(
        "alpine/socat",
        name=f"nst-debug-relay",
        network_mode="container:nstbrowser",
        command=f"TCP-LISTEN:9222,reuseaddr,fork,bind=0.0.0.0 TCP:127.0.0.1:{port}",
        detach=True,
        restart_policy={"Name": "no"},
    )
    time.sleep(10)  # wait for the container to initialize
    return


def wait_for_task_completion(
    payload_manager,
    framework_order: int,
    framework_name: str,
    bot_timeout: int,
    nst_profile_id: str | None,
):
    while True:
        if payload_manager.check_task_compliance(framework_order):
            logger.info(f"Detection completed for {framework_name} within timeout.")
            payload_manager.update_task_status(
                framework_order, TaskStatusEnum.COMPLETED
            )
            if nst_profile_id:
                delete_nst_profile(nst_profile_id)
            if not framework_name == "human":
                stop_container(container_name=framework_name)
            break

        bot_timeout -= 1
        if bot_timeout <= 0:
            logger.warning(
                f"Detection for {framework_name} timed out after {config.challenge.bot_timeout} seconds."
            )
            payload_manager.update_task_status(
                framework_order, TaskStatusEnum.TIMED_OUT
            )
            if nst_profile_id:
                delete_nst_profile(nst_profile_id)
            if not framework_name == "human":
                stop_container(container_name=framework_name)
            break
        time.sleep(1)
    return


def create_docker_networks(docker_client, networks_list):
    _networks = docker_client.networks.list(names=networks_list)

    if not _networks or len(_networks) < 2:
        logger.info("Creating Docker networks for challenge...")
        docker_client.networks.create(
            name="external_network", driver="bridge", internal=False
        )
        docker_client.networks.create(
            name="internal_network", driver="bridge", internal=True
        )
        return


@validate_call
def stop_container(container_name: str = "detector_container") -> None:
    logger.info(f"Stopping container '{container_name}'")
    try:
        subprocess.run(
            ["sudo", "docker", "rm", "-f", container_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.success(f"Successfully stopped container '{container_name}'.")
    except Exception:
        logger.debug(f"Failed to stop container '{container_name}'!")
        pass  # Continue even if container doesn't exist

    return


def run_verification_webhook():
    logger.info("Running human verification webhook.")
    try:
        _wait_interval = int(random.uniform(7, 15))
        _startup_url = str(config.challenge.verification.startup_url).rstrip("/")
        _url = str(config.challenge.verification.endpoint).rstrip("/")

        _headers = {
            "X-API-KEY": config.challenge.verification.api_key.get_secret_value()
        }
        _body = {
            "startup_url": _startup_url,
            "timed_close_sec": _wait_interval,
            "wait_close": False,
            "extra": config.challenge.verification.extra,
        }

        logger.info(f"Sending request to {_url}, body: {_body}")

        response = requests.post(_url, headers=_headers, json=_body)

        if response.status_code == 200:
            logger.success("Successfully ran human verification webhook.")
        else:
            logger.error(
                f"Failed to run human verification webhook! Status code: {response.status_code}"
            )
    except Exception as err:
        logger.error(f"Error running human verification webhook: {str(err)}!")
        raise

    return


__all__ = [
    "copy_detection_files",
    "run_bot_container",
    "stop_container",
]

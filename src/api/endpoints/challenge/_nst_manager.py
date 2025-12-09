import time
from docker import DockerClient
import requests

from api.logger import logger
from api.config import config


def run_nstbrowser(
    docker_client: DockerClient,
    network_names: list[str],
) -> str:
    logger.info("Running NSTBrowser navigation.")
    
    try:
        _container = docker_client.containers.run(
            image="nstbrowser/browserless:latest",
            name="nstbrowser",
            network=network_names[0], 
            ports={'8848/tcp': 8848},
            platform="linux/amd64",
            environment={'TOKEN': config.challenge.nstbrowser.api_key.get_secret_value(), "PORT": "8848"},
            detach=True,
        )
        time.sleep(10)

        docker_client.api.connect_container_to_network(_container.name, network_names[1])
        logger.info("Successfully ran NSTBrowser container.")
    except Exception as err:
        logger.error(f"Error running NSTBrowser navigation: {str(err)}!")
        raise

    return _container.name

def create_nst_profile() -> str:
    logger.info("Creating NSTBrowser profile.")
    
    try:
        _url = f"http://0.0.0.0:8848/api/v2/browsers/once"
        _headers = {
            "Authorization": f"Bearer {config.challenge.nstbrowser.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        response = requests.post(_url, headers=_headers, json={})
        response.raise_for_status()
        if response:
            profile_data = response.json()
            logger.info(f"NSTBrowser profile data {profile_data}")
            profile_id = profile_data.get("data").get("profileId")
            logger.success(f"Successfully created NSTBrowser profile with ID: {profile_id}.")
            return profile_id
        else:
            logger.error(
                f"Failed to create NSTBrowser profile! Status code: {response.status_code}"
            )
            return None
    except Exception as err:
        logger.error(f"Error creating NSTBrowser profile: {str(err)}!")
        raise

def delete_nst_profile(profile_id: str) -> None:
    logger.info(f"Deleting NSTBrowser profile with ID: {profile_id}.")
    
    try:
        _url = f"http://0.0.0.0:8848/api/v2/profiles/{profile_id}"
        _headers = {
            "Authorization": f"Bearer {config.challenge.nstbrowser.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }

        response = requests.delete(_url, headers=_headers)

        if response.status_code == 204:
            logger.success(f"Successfully deleted NSTBrowser profile with ID: {profile_id}.")
        else:
            logger.error(
                f"Failed to delete NSTBrowser profile! Status code: {response.status_code}"
            )
    except Exception as err:
        logger.error(f"Error deleting NSTBrowser profile: {str(err)}!")
        raise

    return
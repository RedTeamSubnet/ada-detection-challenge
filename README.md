# ADA-3 — Anti-Detect Browser Detection Challenge

RedTeam Subnet's ADA-3 challenge. Miners submit browser-side JavaScript detectors that
identify which **commercial anti-detect browser** is driving a session — AdsPower, Dolphin
Anty, GoLogin, Multilogin, or Octo Browser — while staying silent on genuine human traffic.

Unlike ABS, the targets are not Python automation frameworks. Each target is a paid desktop
application that launches a managed profile and is driven over its own loopback API, so
detection must key on product artifacts rather than a WebDriver or CDP automation flag.

Documentation page: <https://docs.theredteam.io/latest/challenges/ada-detection>

See [`AGENTS.md`](./AGENTS.md) for the detector development workflow and
[`docs/Testing_manuals.md`](./docs/Testing_manuals.md) for local scoring.

## ✨ Features

- RedTeam Subnet challenge
- Challenge module (Python package)
- Challenge controller and manager
- Challenge API (FastAPI)
- Five anti-detect browser targets driven through bot-runner driver presets

---

## 🐤 Getting Started

### 1. 🚧 Prerequisites

- Install [**docker** and **docker compose**](https://docs.docker.com/engine/install)
    - Docker image: [**redteamsubnet61/ada_detection**](https://hub.docker.com/r/redteamsubnet61/ada_detection)

[OPTIONAL] For **DEVELOPMENT** environment:

- Install **Python (>= v3.10)** and **pip (>= 23)**:
    - **[RECOMMENDED] [Miniconda (v3)](https://www.anaconda.com/docs/getting-started/miniconda/install)**
    - _[arm64/aarch64] [Miniforge (v3)](https://github.com/conda-forge/miniforge)_
    - _[Python virtual environment] [venv](https://docs.python.org/3/library/venv.html)_
- Install [**git**](https://git-scm.com/downloads)
- Setup an [**SSH key**](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh)

### 2. 📥 Download or clone the repository

**2.1.** Prepare projects directory (if not exists):

```sh
# Create projects directory:
mkdir -pv ~/workspaces/projects

# Enter into projects directory:
cd ~/workspaces/projects
```

**2.2.** Follow one of the below options **[A]**, **[B]** or **[C]**:

**OPTION A.** Clone the repository:

```sh
git clone https://github.com/RedTeamSubnet/ada-detection.git && \
    cd ada-detection
```

**OPTION B.** Clone the repository (for **DEVELOPMENT**: git + ssh key):

```sh
git clone git@github.com:RedTeamSubnet/ada-detection.git && \
    cd ada-detection
```

**OPTION C.** Download source code:

1. Download archived **zip** or **tar.gz** file from [**releases**](https://github.com/RedTeamSubnet/ada-detection/releases).
2. Extract it into the projects directory.
3. Enter into the project directory.

#### [OPTIONAL] Install dependencies (for **DEVELOPMENT** environment)

```sh
# For DEVELOPMENT environment, install dependencies with pip:
pip install -e .[dev]
# Install pre-commit hooks:
pre-commit install
```

### 3. 🌎 Configure environment variables

[NOTE] Please, check **[environment variables](#-environment-variables)** section for more details.

```sh
# Copy '.env.example' file to '.env' file:
cp -v ./.env.example ./.env
# Edit environment variables to fit in your environment:
nano ./.env
```

### 4. 🏁 Start the server

```sh
## OPTIONAL: Configure 'compose.override.yml' file.
# For DEVELOPMENT environment:
cp -v ./templates/compose/compose.override.dev.yml ./compose.override.yml
# Edit 'compose.override.yml' file to fit in your environment:
nano ./compose.override.yml

## 1. Check docker compose configuration is valid:
./compose.sh validate
# Or:
docker compose config

## 2. Start docker compose:
./compose.sh start -l
# Or:
docker compose up -d --remove-orphans --force-recreate && \
    docker compose logs -f -n 100
```

### 5. ✅ Check server is running

Check with CLI (curl):

```sh
# Send a ping request with 'curl' to REST API server and parse JSON response with 'jq':
curl -s http://localhost:10001/ping | jq
```

Check with web browser:

- Health check: <http://localhost:10001/health>
- Swagger: <http://localhost:10001/docs>
- Redoc: <http://localhost:10001/redoc>
- OpenAPI JSON: <http://localhost:10001/openapi.json>

### 6. 🛑 Stop the server

Docker runtime:

```sh
# Stop docker compose:
./compose.sh stop
# Or:
docker compose down --remove-orphans
```

👍

---

## ⚙️ Configuration

### 🌎 Environment Variables

[**`.env.example`**](./.env.example):

```sh
## --- Environment variable --- ##
ENV=LOCAL
DEBUG=false
# TZ=UTC
# PYTHONDONTWRITEBYTECODE=1


## -- API configs -- ##
AAD_CHALLENGE_API_PORT=10001
# AAD_CHALLENGE_API_CONFIGS_DIR="/etc/ada_detection"
# AAD_CHALLENGE_API_LOGS_DIR="/var/log/ada_detection"
# AAD_CHALLENGE_API_DATA_DIR="/var/lib/ada_detection"
# AAD_CHALLENGE_API_TMP_DIR="/tmp/ada_detection"
# AAD_CHALLENGE_API_VERSION="1"
# AAD_CHALLENGE_API_PREFIX=""
# AAD_CHALLENGE_API_DOCS_ENABLED=true
# AAD_CHALLENGE_API_DOCS_OPENAPI_URL="{api_prefix}/openapi.json"
# AAD_CHALLENGE_API_DOCS_DOCS_URL="{api_prefix}/docs"
# AAD_CHALLENGE_API_DOCS_REDOC_URL="{api_prefix}/redoc"
```

---

## 🏗️ Build Docker Image

Before building the docker image, make sure you have installed **docker** and **docker compose**.

To build the docker image, run the following command:

```sh
# Build docker image:
./scripts/build.sh
# Or:
docker compose build
```

## 📚 Documentation

- <https://docs.theredteam.io/latest/challenges>

---

## 📑 References

- RedTeam Subnet: <https://www.theredteam.io>
- Bittensor: <https://www.bittensor.com>
- FastAPI - <https://fastapi.tiangolo.com>
- Docker - <https://docs.docker.com>
- Docker Compose - <https://docs.docker.com/compose>

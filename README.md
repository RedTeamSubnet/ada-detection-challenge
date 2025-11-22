# Auto Browser Sniffer Challenge

The **Auto Browser Sniffer Challenge** is a series designed to test the skills of participants in developing a browser SDK that can accurately detect automation frameworks and genuine human interaction on a webpage. The latest iteration, **AB Sniffer**, introduces a new modular architecture for detection, an updated set of target frameworks, and refined, more stringent evaluation criteria.

Participants are tasked with creating an script that can be injected on a website to automatically identify various automation frameworks (such as Nodriver, Seleniumbase, Puppeteerextra, Botasaurus, and others) and distinguish them from genuine human interaction. The challenge emphasizes reliable detection across multiple execution modes, including headless environments. During evaluation, each of the 9 target scenarios will be run multiple times in a randomized and shuffled order to prevent predictable patterns. Submissions are rigorously scored based on accuracy, consistency, and coverage, with a critical penalty applied for any false positives involving human interaction.

The challenge infrastructure includes a `web endpoint` where each submission automatically sends its payload for evaluation, and a `score endpoint` for receiving the results. This score endpoint is secured using symmetric authentication.

## ⚙️ How It Works

1. **Miner Submits Detection Scripts**: The miner submits their detection scripts.
2. **Challenger container**: Will call `auth key` with symmetric authentication.
3. **Scripts are Loaded into a Web Page**: The submitted scripts are injected into a test web page where the evaluation will take place.
4. **Randomized Scenarios are Run**: The system runs 9 different scenarios (8 automation frameworks + 1 human user) against the web page. This is repeated 3 times, and the order of the scenarios is randomized and shuffled in each set.
5. **Payloads are Sent to Web Endpoint**: During each of the 27 test runs, a payload containing the detection results is automatically sent to the `web endpoint` for collection.
6. **The Final Score is Returned**: After all 27 sessions are complete and the final score is calculated, the `/score` endpoint completes the process by returning the final score in the HTTP response to the original request.

## ✨ Features

- SDK for browser type detection
- Scoring based on accuracy of detection
- API server for challenge interaction
- Health check endpoint
- Dockerfile for deployment
- FastAPI
- Web service

---

## 🛠 Installation

### 1. 📦 Install dependencies

[TIP] Skip this step, if you're going to use **docker** runtime

```sh
pip install -r ./requirements.txt
```

### 2. 🏁 Start the server

#### Docker runtime

**OPTION A.** Run with **docker compose**:

```sh
## 1. Configure 'compose.override.yml' file.

# Copy 'compose.override.[ENV].yml' file to 'compose.override.yml' file:
cp -v ./templates/compose/compose.override.[ENV].yml ./compose.override.yml
# For example, DEVELOPMENT environment:
cp -v ./templates/compose/compose.override.dev.yml ./compose.override.yml
# For example, STATGING or PRODUCTION environment:
cp -v ./templates/compose/compose.override.prod.yml ./compose.override.yml

# Edit 'compose.override.yml' file to fit in your environment:
nano ./compose.override.yml


## 2. Check docker compose configuration is valid:
./compose.sh validate
# Or:
docker compose config


## 3. Start docker compose:
./compose.sh start -l
# Or:
docker compose up -d --remove-orphans --force-recreate && \
    docker compose logs -f --tail 100
```

### 5. ✅ Check server is running

Check with CLI (curl):

```sh
# Send a ping request with 'curl' to API server and parse JSON response with 'jq':
curl -s -k https://localhost:10001/ping | jq
```

Check with web browser:

- Health check: <https://localhost:10001/health>
- Swagger: <https://localhost:10001/docs>
- Redoc: <https://localhost:10001/redoc>
- OpenAPI JSON: <https://localhost:10001/openapi.json>

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

[**`.env.example`**](https://github.com/RedTeamSubnet/RedTeam/blob/feat/webui-auto-challenge/redteam_core/challenge_pool/webui_auto/.env.example):

```sh
## --- Environment variable --- ##
ENV=LOCAL
DEBUG=false


## -- API configs -- ##
ABS_API_PORT=10001
# ABS_API_LOGS_DIR="/var/log/rest.rt-abs-challenger"
# ABS_API_DATA_DIR="/var/lib/rest.rt-abs-challenger"

# ABS_API_VERSION="1"
# ABS_API_PREFIX=""
# ABS_API_DOCS_ENABLED=true
# ABS_API_DOCS_OPENAPI_URL="{api_prefix}/openapi.json"
# ABS_API_DOCS_DOCS_URL="{api_prefix}/docs"
# ABS_API_DOCS_REDOC_URL="{api_prefix}/redoc"

## -- Rewarding Service Endpoints & Auth -- ##
ABS_WEB_ENDPOINT_URL="http://localhost:8000/web"
ABS_SCORE_ENDPOINT_URL="http://localhost:8000/score"
REWARDING_SECRET_KEY="your-strong-secret-key-here" # IMPORTANT: Change this to a strong, unique key
```

## 🏗️ Build Docker Image

To build the docker image, run the following command:

```sh
# Build docker image:
./scripts/build.sh
# Or:
docker compose build
```

---

## 📑 References

- FastAPI - <https://fastapi.tiangolo.com>
- Docker - <https://docs.docker.com>
- Docker Compose - <https://docs.docker.com/compose>

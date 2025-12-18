# Anti-Detect Automation Detection (AAD) Challenge Platform

## Overview

Welcome to the Anti-Detect Automation Detection (AAD) Challenge Platform. This project is the official server that runs and evaluates submissions for the AAD challenge.

The primary goal of this challenge is to **detect how different automation frameworks utilize WebSockets and other stealth techniques to control a browser**. To achieve this, all tests are conducted within the specialized **NST-Browser**, providing a consistent and secure environment for analysis.

This platform's purpose is to test a detection script's ability to accurately identify these automation frameworks while correctly classifying genuine human interaction, with a strong penalty for false positives.

### How The Challenge Works

When you submit your solution for scoring, the following automated process occurs:

1. **Submission Received**: The AAD server receives your set of detection scripts via an API call to the `/score` endpoint.
2. **NST-Browser Environment**: The server launches a primary **NST-Browser** container. For every single test, a new, clean browser profile is created within NST-Browser to prevent any data leakage between runs.
3. **Isolated Bot Execution**: For each target automation framework (e.g., `nodriver`), the server spins up a *second*, isolated Docker container running that specific bot.
4. **Test Scenario**: The bot container is instructed to connect to the NST-Browser instance and visit a webpage. This page has been dynamically injected with *your* detection scripts.
5. **Detection & Payload**: Your script executes inside the NST-Browser environment. It must analyze the browser's behavior, looking for signs of WebSocket control or other automation artifacts, and send its findings (a "payload") back to the server's internal `/_payload` endpoint.
6. **Human Verification**: The "human" test is unique. The server will log a message, and a human operator must visit the challenge page to complete the test manually. Your submitted scripts must correctly identify this interaction as non-automated (i.e., they should **not** fire a detection).
7. **Cleanup & Repetition**: After each test, the bot's Docker container is destroyed, and the NST-Browser profile is wiped. The process is repeated multiple times for each framework to ensure your script is consistent.
8. **Scoring**: Once all tests are complete, a final score is calculated based on your accuracy, consistency, and ability to distinguish bots from a human. The final score is then returned to you in the API response.

### Scoring System

The scoring is designed to reward precision and heavily penalize mistakes, especially when misidentifying a human.

- **Human as Bot = 0 Score**: If your script incorrectly identifies the human user as a bot more than the allowed number of times, your **final score is 0**, regardless of how well you detected the actual bots.
- **Perfect Human Detection**: Correctly identifying the human in all runs earns you **1 full point** towards your total (this means your scripts detect nothing during human interaction).
- **Perfect Bot Detection**: Correctly identifying a specific bot framework across all its test runs (e.g., 3 out of 3 times) without any collisions earns **1 full point** per framework.
- **Collisions**: If you correctly identify the bot but *also* identify other frameworks incorrectly at the same time (a "collision"), you receive a reduced score of **0.1 points** for that run.
**Automation Detection** Upon correctly identifying automation in each session, you will earn one point. Accurate detection of automation entails that any automation framework should indicate the framework as automation by returning a `True` value. Conversely, in the case of human interaction, it should return a `False` value. The total points awarded for automation are determined by summing all correct detections and dividing by the total number of sessions.
- **Final Score**: The final score is a normalized calculation: `Final Score = (Total Points Earned) / (Number of Frameworks + 1 + 1)`.

### Local Testing & Submission

To test your solution locally, you first need to run the challenge server. Then, you must send an authenticated `POST` request to the `/score` endpoint.

The body of the request must be a JSON object containing your detection scripts for each *bot automation framework*. **You do not submit a separate script for human detection.** Your submitted scripts are expected to remain silent (i.e., not detect any automation) during a human interaction test.

**Example of the JSON structure for your submission:**

```json
{
  "detection_files": [
    {
      "file_name": "nodriver.js",
      "content": "/* your javascript code to detect nodriver */"
    },
    {
      "file_name": "playwright.js",
      "content": "/* your javascript code to detect playwright */"
    },
    {
      "file_name": "patchright.js",
      "content": "/* your javascript code to detect patchright */"
    },
    {
      "file_name": "puppeteer.js",
      "content": "/* your javascript code to detect puppeteer */"
    },
    {
      "file_name": "automation.js",
      "content": "/* your javascript code to detect automation */"
    }
  ]
}
```

*(Note: You must provide a script for every target framework configured in the challenge. The current target frameworks are: nodriver, playwright, patchright, puppeteer.)*

The API key for authentication is the `AAD_CHALLENGE_API_KEY` value defined in your `.env` file.

---

## Testing manuals

- Testing manuals are provided in [docs/testing_manuals.md](./docs/Testing_manuals.md) file
- Miners should follow each step to correctly set up Testing environment
